import time

from socket_package.Protocol.SocketConfig import ClientConfig, ServerConfig


class TestClientConfigHeartbeat:
    def test_heartbeat_interval_default(self):
        cfg = ClientConfig()
        assert cfg.heartbeat_interval_sec == 5.0

    def test_heartbeat_interval_custom(self):
        cfg = ClientConfig(heartbeat_interval_sec=10.0)
        assert cfg.heartbeat_interval_sec == 10.0

    def test_heartbeat_interval_preserves_other_fields(self):
        cfg = ClientConfig(host="1.2.3.4", port=5555, heartbeat_interval_sec=3.0)
        assert cfg.host == "1.2.3.4"
        assert cfg.port == 5555
        assert cfg.heartbeat_interval_sec == 3.0


class TestServerConfigHeartbeat:
    def test_heartbeat_timeout_default(self):
        cfg = ServerConfig()
        assert cfg.heartbeat_timeout_sec == 15.0

    def test_heartbeat_timeout_custom(self):
        cfg = ServerConfig(heartbeat_timeout_sec=30.0)
        assert cfg.heartbeat_timeout_sec == 30.0

    def test_heartbeat_timeout_preserves_other_fields(self):
        cfg = ServerConfig(port=7777, heartbeat_timeout_sec=10.0)
        assert cfg.port == 7777
        assert cfg.heartbeat_timeout_sec == 10.0


class TestClientInfo:
    def test_client_info_creation(self):
        from socket_package.Server.ServerSocket import ClientInfo

        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            now = time.time()
            info = ClientInfo(sock, now)
            assert info.client_socket is sock
            assert info.last_heartbeat_time == now
        finally:
            sock.close()