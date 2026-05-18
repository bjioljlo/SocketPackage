import time

from socket_package.Protocol.SocketConfig import ServerConfig
from socket_package.Server import ServerSocket
from socket_package.Server.ServerSocket import ClientInfo


class TestServerSocketClientIdentity:
    def test_client_id_auto_increment(self):
        config = ServerConfig(port=0, accept_timeout_sec=0.1)
        server = ServerSocket(config)
        assert server._ServerSocket__next_client_id == 1

    def test_get_client_info_returns_none_for_invalid_id(self):
        config = ServerConfig(port=0, accept_timeout_sec=0.1)
        server = ServerSocket(config)
        assert server.get_client_info(999) is None

    def test_get_all_clients_returns_empty_dict(self):
        config = ServerConfig(port=0, accept_timeout_sec=0.1)
        server = ServerSocket(config)
        clients = server.get_all_clients()
        assert clients == {}

    def test_client_info_player_data_default_empty(self):
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            info = ClientInfo(1, sock, time.time())
            assert info.player_data == {}
        finally:
            sock.close()

    def test_client_info_player_data_set_and_get(self):
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            info = ClientInfo(1, sock, time.time())
            info.player_data["username"] = "Alice"
            info.player_data["level"] = 42
            assert info.player_data["username"] == "Alice"
            assert info.player_data["level"] == 42
        finally:
            sock.close()