from socket import socket
from socket_package import MyByteArray
from socket_package.Server import ServerSocket
from ProtocolKinds import MainKind, SubKind


class SampleServerManager():
    def __init__(self, socket: ServerSocket) -> None:
        self._socket:ServerSocket = socket
    def SampleSendMsg(self, mainSocket: socket, aMsg: MyByteArray):
        self._socket.SendMessages(mainSocket, MainKind.CHAT_ECHO, SubKind.ECHO_MESSAGE, aMsg)
    def SampleBroadcastMessages(self, mainSocket: socket, aMsg: MyByteArray):
        self._socket.BroadcastMessages(mainSocket, MainKind.CHAT_BROADCAST, SubKind.BROADCAST_MESSAGE, aMsg)
    def SampleStop(self):
        self._socket.Stop()
