from socket import socket
from socket_package.Client import ClientSocket
from socket_package import MyByteArray
from ProtocolKinds import MainKind, SubKind
from socket_package.Protocol.ProtocolKinds import PROTOCOL_VERSION

class SampleClientManager():
    def __init__(self, socket: ClientSocket) -> None:
        self._socket:ClientSocket = socket
    def SampleSendMsg(self, mainSocket: socket, aMsg: MyByteArray):
        self._socket.SendMessages(mainSocket, MainKind.CHAT_ECHO, SubKind.ECHO_MESSAGE, aMsg)
    def SampleBroadcastMessages(self, mainSocket: socket, aMsg: MyByteArray):
        self._socket.BroadcastMessages(mainSocket, MainKind.CHAT_BROADCAST, SubKind.BROADCAST_MESSAGE, aMsg)
    def SampleStop(self):
        self._socket.Stop()
    def SampleShowOther(self, msg: MyByteArray):
        message:str = msg.ReadStr()
        print("\n[Other][{}] ".format(message))
    def SampleShowMe(self, msg: MyByteArray):
        message:str = msg.ReadStr()
        print("\n[Me][{}] ".format(message))
    def SampleStopSingle(self):
        aMsg = MyByteArray()
        self._socket.SendMessages(self._socket.mainSocket, MainKind.CONTROL, SubKind.STOP, aMsg)
    def SampleSend(self, message:str):
        aMsg = MyByteArray()
        aMsg.WriteStr(message)
        self._socket.SendMessages(self._socket.mainSocket, MainKind.CHAT, SubKind.CLIENT_MESSAGE, aMsg)
    def SampleSendInput(self):
        while True:
            message = input("[Input] ")
            if message == 'Stop':
                self.SampleStopSingle()
                break
            if message == 'HB':
                self._socket.SendHeartbeat(self._socket.mainSocket, PROTOCOL_VERSION)
                continue
            self.SampleSend(message)
