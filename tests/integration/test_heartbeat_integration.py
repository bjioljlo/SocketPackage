"""Integration tests for auto-heartbeat detection over real sockets."""

import threading
import time

import pytest

from socket_package.Client import ClientSocket
from socket_package.Protocol.MyByteArray import MyByteArray
from socket_package.Protocol.ProtocolKinds import MainKind, SubKind
from socket_package.Protocol.RecvMsgProtocol import IRecvProtocol
from socket_package.Protocol.SocketConfig import ClientConfig, ServerConfig
from socket_package.Server import ServerSocket


class _CollectorProtocol(IRecvProtocol):
    """Protocol that collects received messages for test assertions."""

    def __init__(self):
        self.received: list[tuple[int, int, bytes]] = []
        self._lock = threading.Lock()

    def recv_msg(self, mainSocket, main_kind: int, sub_kind: int, msg: MyByteArray):
        with self._lock:
            self.received.append((main_kind, sub_kind, bytes(msg.Msg)))


@pytest.mark.integration
def test_heartbeat_exchange_keeps_connection_alive():
    """
    Client sends heartbeats automatically; server processes them.
    Non-heartbeat messages still flow through to the protocol handler,
    and the connection stays alive.
    """
    server_config = ServerConfig(
        port=0,
        accept_timeout_sec=0.5,
        heartbeat_timeout_sec=5.0,
    )
    server = ServerSocket(server_config)
    server_protocol = _CollectorProtocol()

    server_thread = threading.Thread(target=server.Run, args=(server_protocol,), daemon=True)
    server_thread.start()
    time.sleep(0.3)

    bound_port = _get_bound_port(server)
    assert bound_port is not None, "Server failed to bind"

    client_config = ClientConfig(
        port=bound_port,
        heartbeat_interval_sec=0.2,
    )
    client = ClientSocket(client_config)
    client_protocol = _CollectorProtocol()

    client_thread = threading.Thread(target=client.Run, args=(client_protocol,), daemon=True)
    client_thread.start()
    time.sleep(0.5)

    assert client.IsConnect, "Client should be connected"

    # Send a non-heartbeat message to verify the wire is working
    payload_str = "ping-from-client"
    payload = MyByteArray()
    payload.WriteStr(payload_str)
    client.SendMessages(client.mainSocket, MainKind.CONTROL, SubKind.STOP, payload)

    time.sleep(0.5)

    assert len(server_protocol.received) > 0, (
        "Server protocol should have received the application message"
    )
    main_kind, sub_kind, msg_bytes = server_protocol.received[-1]
    assert main_kind == MainKind.CONTROL
    assert sub_kind == SubKind.STOP
    # The msg_bytes include the full MyByteArray: 3 ints (version, main_kind, sub_kind)
    # followed by the payload. Skip the 3 ints, then read the string.
    decoded = MyByteArray(bytearray(msg_bytes))
    decoded.ReadInt()  # skip version
    decoded.ReadInt()  # skip main_kind
    decoded.ReadInt()  # skip sub_kind
    assert decoded.ReadStr() == payload_str

    client.Stop()
    server.Stop()
    time.sleep(0.3)

    assert not client.IsConnect


@pytest.mark.integration
def test_server_disconnects_on_heartbeat_timeout():
    """
    When client stops sending heartbeats, the server should
    eventually detect the timeout and disconnect the client.
    """
    server_config = ServerConfig(
        port=0,
        accept_timeout_sec=0.5,
        heartbeat_timeout_sec=1.0,
    )
    server = ServerSocket(server_config)
    server_protocol = _CollectorProtocol()

    server_thread = threading.Thread(target=server.Run, args=(server_protocol,), daemon=True)
    server_thread.start()
    time.sleep(0.3)

    bound_port = _get_bound_port(server)
    assert bound_port is not None, "Server failed to bind"

    client_config = ClientConfig(
        port=bound_port,
        heartbeat_interval_sec=0.1,
    )
    client = ClientSocket(client_config)
    client_protocol = _CollectorProtocol()

    client_thread = threading.Thread(target=client.Run, args=(client_protocol,), daemon=True)
    client_thread.start()
    time.sleep(0.5)

    assert client.IsConnect, "Client should be connected initially"

    # Stop the client to stop heartbeat sending
    client.Stop()

    # Wait for server's heartbeat timeout checker to clean up
    time.sleep(2.0)

    # The server should have no tracked clients after the timeout
    with server._ServerSocket__clients_lock:
        assert not server._ServerSocket__clients, "Server should have no tracked clients"

    assert not client.IsConnect, "Client should be marked disconnected"


def _get_bound_port(server: ServerSocket) -> int | None:
    """Extract the bound port from the server's internal socket."""
    sock = server._ServerSocket__server_socket
    if sock is None:
        return None
    return sock.getsockname()[1]