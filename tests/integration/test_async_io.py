"""Integration tests for asyncio-based AsyncClientSocket and AsyncServerSocket."""

import asyncio
import threading

import pytest

from socket_package import AsyncClientSocket, AsyncServerSocket
from socket_package.Protocol.AsyncRecvMsgProtocol import IAsyncRecvProtocol
from socket_package.Protocol.MyByteArray import MyByteArray
from socket_package.Protocol.ProtocolKinds import MainKind, SubKind
from socket_package.Protocol.SocketConfig import ClientConfig, ServerConfig


class _CollectorAsyncProtocol(IAsyncRecvProtocol):
    """Async protocol that collects received messages."""

    def __init__(self):
        self.received: list[tuple[int, int, bytes]] = []
        self._lock = threading.Lock()

    async def recv_msg(self, writer, main_kind: int, sub_kind: int, msg: MyByteArray):
        with self._lock:
            self.received.append((main_kind, sub_kind, bytes(msg.Msg)))


@pytest.mark.integration
@pytest.mark.asyncio
async def test_async_client_server_echo():
    """
    AsyncServerSocket receives a message from AsyncClientSocket
    and dispatches it to the protocol handler.
    """
    server_config = ServerConfig(port=0, accept_timeout_sec=0.5)
    server = AsyncServerSocket(server_config)
    server_protocol = _CollectorAsyncProtocol()

    server_task = asyncio.create_task(server.Run(server_protocol))
    await asyncio.sleep(0.3)

    bound_port = server._AsyncServerSocket__server.sockets[0].getsockname()[1]

    client_config = ClientConfig(port=bound_port)
    client = AsyncClientSocket(client_config)
    client_protocol = _CollectorAsyncProtocol()

    client_task = asyncio.create_task(client.Run(client_protocol))
    await asyncio.sleep(0.3)

    assert client.is_connected

    payload = MyByteArray()
    payload.WriteStr("hello-async")
    client.SendMessages(MainKind.CONTROL, SubKind.STOP, payload)
    await asyncio.sleep(0.3)

    assert len(server_protocol.received) > 0
    main_kind, sub_kind, msg_bytes = server_protocol.received[-1]
    assert main_kind == MainKind.CONTROL
    assert sub_kind == SubKind.STOP
    decoded = MyByteArray(bytearray(msg_bytes))
    decoded.ReadInt()
    decoded.ReadInt()
    decoded.ReadInt()
    assert decoded.ReadStr() == "hello-async"

    await client.Stop()
    server_task.cancel()
    try:
        await server_task
    except asyncio.CancelledError:
        pass