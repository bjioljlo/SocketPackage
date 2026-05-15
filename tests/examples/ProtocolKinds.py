from enum import IntEnum

from socket_package.Protocol.ProtocolKinds import MainKind as CoreMainKind
from socket_package.Protocol.ProtocolKinds import SubKind as CoreSubKind


class MainKind(IntEnum):
    CONTROL = int(CoreMainKind.CONTROL)
    CHAT = 123
    CHAT_BROADCAST = 456
    CHAT_ECHO = 789


class SubKind(IntEnum):
    STOP = int(CoreSubKind.STOP)
    HEARTBEAT = int(CoreSubKind.HEARTBEAT)
    CLIENT_MESSAGE = 321
    BROADCAST_MESSAGE = 789
    ECHO_MESSAGE = 456


__all__ = ["MainKind", "SubKind", "CoreMainKind", "CoreSubKind"]
