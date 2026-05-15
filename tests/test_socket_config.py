from socket_package.Client import ClientSocket
from socket_package.Protocol.ProtocolKinds import MainKind as CoreMainKind
from socket_package.Protocol.ProtocolKinds import PROTOCOL_VERSION
from socket_package.Protocol.ProtocolKinds import SubKind as CoreSubKind
from socket_package.Protocol.SocketConfig import ClientConfig, ServerConfig
from socket_package.Server import ServerSocket


def test_package_exposes_only_core_protocol_kinds():
    assert [kind.value for kind in CoreMainKind] == [0]
    assert [kind.value for kind in CoreSubKind] == [0, 1]


def test_client_socket_uses_injected_config():
    cfg = ClientConfig(
        host="192.168.0.10",
        port=7788,
        buffer_size=2048,
        retry_interval_sec=0.5,
        protocol_version=PROTOCOL_VERSION,
        max_frame_size=8192,
    )
    client = ClientSocket(cfg)
    assert client.config == cfg


def test_server_socket_uses_injected_config():
    cfg = ServerConfig(
        host="127.0.0.1",
        port=8899,
        backlog=10,
        accept_timeout_sec=0.2,
        buffer_size=2048,
        protocol_version=PROTOCOL_VERSION,
        max_frame_size=8192,
    )
    server = ServerSocket(cfg)
    assert server.config == cfg
