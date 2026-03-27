from dataclasses import dataclass

from socket_package.Protocol.ProtocolKinds import PROTOCOL_VERSION


@dataclass(slots=True, frozen=True)
class ClientConfig:
    host: str = "127.0.0.1"
    port: int = 9999
    buffer_size: int = 4096
    retry_interval_sec: float = 1.0
    protocol_version: int = PROTOCOL_VERSION
    max_frame_size: int = 1024 * 1024


@dataclass(slots=True, frozen=True)
class ServerConfig:
    host: str = "0.0.0.0"
    port: int = 9999
    backlog: int = 5
    accept_timeout_sec: float = 1.0
    buffer_size: int = 4096
    protocol_version: int = PROTOCOL_VERSION
    max_frame_size: int = 1024 * 1024
