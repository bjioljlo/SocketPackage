from enum import IntEnum

from socket_package.Protocol.ProtocolKinds import MainKind as CoreMainKind
from socket_package.Protocol.ProtocolKinds import SubKind as CoreSubKind


class MainKind(IntEnum):
    # Reuse reserved core kind.
    CONTROL = int(CoreMainKind.CONTROL)

    # User-defined business kinds.
    CHAT = 123
    CHAT_BROADCAST = 456
    CHAT_ECHO = 789


class SubKind(IntEnum):
    # Reuse reserved core sub-kinds.
    STOP = int(CoreSubKind.STOP)
    HEARTBEAT = int(CoreSubKind.HEARTBEAT)

    # User-defined business sub-kinds.
    CLIENT_MESSAGE = 321
    BROADCAST_MESSAGE = 789
    ECHO_MESSAGE = 456


__all__ = ["MainKind", "SubKind", "CoreMainKind", "CoreSubKind"]
