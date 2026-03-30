from abc import ABC, abstractmethod
from socket import socket

from socket_package.Protocol.FrameCodec import encode_frame
from socket_package.Protocol.MyByteArray import MyByteArray
from socket_package.Protocol.ProtocolKinds import MainKind, PROTOCOL_VERSION, SubKind
from socket_package.Protocol.RecvMsgProtocol import IRecvProtocol

class ISocket(ABC):
    '''Socket分類介面'''
    @abstractmethod
    def Run(self, recvProtocol :IRecvProtocol):
        pass
    @abstractmethod
    def Stop(self):
        pass
    @abstractmethod
    def SendMessages(self, mainSocket:socket, main_kind: int, sub_kind: int, msg: MyByteArray):
        pass
    @abstractmethod
    def BroadcastMessages(self, client_socket: socket, main_kind: int, sub_kind: int, msg: MyByteArray, sendSelf: bool = False):
        pass

class TSocket(ISocket):
    '''Socket分類實作'''
    @abstractmethod
    def Run(self, recvProtocol :IRecvProtocol):
        pass
    @abstractmethod
    def Stop(self):
        pass

    @abstractmethod
    def BroadcastMessages(self, client_socket: socket, main_kind: int, sub_kind: int, msg: MyByteArray, sendSelf: bool = False):
        pass

    def SendMessages(
        self,
        mainSocket: socket,
        main_kind: int,
        sub_kind: int,
        msg: MyByteArray,
        protocol_version: int = PROTOCOL_VERSION,
    ):
        if mainSocket is None:
            raise ValueError("mainSocket is None.")
        if msg is None:
            raise ValueError("msg is None.")

        print("\n SendMessages :{} - {}".format(main_kind, sub_kind))
        aMsg = MyByteArray()
        aMsg.WriteInt(protocol_version)
        aMsg.WriteInt(main_kind)
        aMsg.WriteInt(sub_kind)
        payload = aMsg.Msg + msg.Msg
        mainSocket.sendall(encode_frame(payload))

    def SendHeartbeat(self, mainSocket: socket, protocol_version: int = PROTOCOL_VERSION):
        self.SendMessages(mainSocket, MainKind.CONTROL, SubKind.HEARTBEAT, MyByteArray(), protocol_version=protocol_version)
