from abc import ABC, abstractmethod
from enum import Enum
from socket import socket
from typing import Callable

from socket_package.Protocol.MyByteArray import MyByteArray

ProtocolHandler = Callable[[socket, MyByteArray], None]

class IRecvMainkind(ABC):
    '''接收分類介面'''
    @abstractmethod
    def recv_msg(self, mainSocket:socket, mainkind: int, subkind: int, msg: MyByteArray):
        pass

class TRecvMainkind(IRecvMainkind):
    '''接收分類實作'''
    @abstractmethod
    def recv_msg(self, mainSocket:socket, mainkind: int, subkind: int, msg: MyByteArray):
        print("\n ReceivedMessages :{} - {}".format(mainkind, subkind))


class UnhandledPolicy(str, Enum):
    LOG = "log"
    IGNORE = "ignore"
    RAISE = "raise"


class ProtocolRouter(TRecvMainkind):
    """Simple protocol router by (mainkind, subkind)."""

    def __init__(self, unhandled_policy: UnhandledPolicy = UnhandledPolicy.LOG) -> None:
        self._routes: dict[tuple[int, int], ProtocolHandler] = {}
        self._unhandled_policy = unhandled_policy

    def register(self, mainkind: int, subkind: int, handler: ProtocolHandler) -> None:
        self._routes[(mainkind, subkind)] = handler

    def route(self, mainkind: int, subkind: int):
        def decorator(handler: ProtocolHandler) -> ProtocolHandler:
            self.register(mainkind, subkind, handler)
            return handler

        return decorator

    def recv_msg(self, mainSocket: socket, mainkind: int, subkind: int, msg: MyByteArray):
        handler = self._routes.get((mainkind, subkind))
        if handler is None:
            self.on_unhandled(mainSocket, mainkind, subkind, msg)
            return
        handler(mainSocket, msg)

    def on_unhandled(self, mainSocket: socket, mainkind: int, subkind: int, msg: MyByteArray):
        if self._unhandled_policy == UnhandledPolicy.IGNORE:
            return
        if self._unhandled_policy == UnhandledPolicy.RAISE:
            raise KeyError(f"Unhandled protocol: {mainkind}-{subkind}")
        print("\n Unhandled protocol :{} - {}".format(mainkind, subkind))
