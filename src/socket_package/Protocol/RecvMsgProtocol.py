from abc import ABC, abstractmethod
from enum import Enum
from socket import socket
from typing import Callable

from socket_package.Protocol.MyByteArray import MyByteArray

ProtocolHandler = Callable[[socket, MyByteArray], None]

class IRecvProtocol(ABC):
    '''接收分類介面'''
    @abstractmethod
    def recv_msg(self, mainSocket:socket, main_kind: int, sub_kind: int, msg: MyByteArray):
        pass

class TRecvProtocol(IRecvProtocol):
    '''接收分類實作'''
    @abstractmethod
    def recv_msg(self, mainSocket:socket, main_kind: int, sub_kind: int, msg: MyByteArray):
        print("\n ReceivedMessages :{} - {}".format(main_kind, sub_kind))


class UnhandledPolicy(str, Enum):
    LOG = "log"
    IGNORE = "ignore"
    RAISE = "raise"


class ProtocolRouter(TRecvProtocol):
    """Simple protocol router by (main_kind, sub_kind)."""

    def __init__(self, unhandled_policy: UnhandledPolicy = UnhandledPolicy.LOG) -> None:
        self._routes: dict[tuple[int, int], ProtocolHandler] = {}
        self._unhandled_policy = unhandled_policy

    def register(self, main_kind: int, sub_kind: int, handler: ProtocolHandler) -> None:
        self._routes[(main_kind, sub_kind)] = handler

    def route(self, main_kind: int, sub_kind: int):
        def decorator(handler: ProtocolHandler) -> ProtocolHandler:
            self.register(main_kind, sub_kind, handler)
            return handler

        return decorator

    def recv_msg(self, mainSocket: socket, main_kind: int, sub_kind: int, msg: MyByteArray):
        handler = self._routes.get((main_kind, sub_kind))
        if handler is None:
            self.on_unhandled(mainSocket, main_kind, sub_kind, msg)
            return
        handler(mainSocket, msg)

    def on_unhandled(self, mainSocket: socket, main_kind: int, sub_kind: int, msg: MyByteArray):
        if self._unhandled_policy == UnhandledPolicy.IGNORE:
            return
        if self._unhandled_policy == UnhandledPolicy.RAISE:
            raise KeyError(f"Unhandled protocol: {main_kind}-{sub_kind}")
        print("\n Unhandled protocol :{} - {}".format(main_kind, sub_kind))
