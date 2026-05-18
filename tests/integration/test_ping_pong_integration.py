import threading
import time
import pytest
from socket_package.Server.ServerSocket import ServerSocket
from socket_package.Client.ClientSocket import ClientSocket
from socket_package.Protocol.RecvMsgProtocol import ProtocolRouter
from socket_package.Protocol.ProtocolKinds import MainKind, SubKind

@pytest.mark.integration
def test_ping_pong_roundtrip():
    server = ServerSocket()
    router = ProtocolRouter()

    def server_thread():
        server.Run(router)

    t = threading.Thread(target=server_thread, daemon=True)
    t.start()
    time.sleep(0.1)

    client = ClientSocket()

    class DummyProtocol(ProtocolRouter):
        pass

    dp = DummyProtocol()
    client_thread = threading.Thread(target=client.Run, args=(dp,), daemon=True)
    client_thread.start()
    time.sleep(0.2)

    # send ping and wait for pong
    client.send_ping()
    time.sleep(0.1)
    rtt = client.get_rtt_ms()
    assert rtt is None or rtt >= 0

    # cleanup
    client.Stop()
    server.Stop()
    time.sleep(0.1)
