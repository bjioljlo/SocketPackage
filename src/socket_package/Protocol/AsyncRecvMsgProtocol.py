from abc import ABC, abstractmethod
from asyncio import StreamWriter

from socket_package.Protocol.MyByteArray import MyByteArray


class IAsyncRecvProtocol(ABC):
    '''非同步接收分類介面'''
    @abstractmethod
    async def recv_msg(self, writer: StreamWriter, main_kind: int, sub_kind: int, msg: MyByteArray):
        pass