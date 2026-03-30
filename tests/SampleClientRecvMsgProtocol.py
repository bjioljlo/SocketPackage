from SampleClientManager import SampleClientManager
from socket_package import MyByteArray
from socket_package.Protocol.RecvMsgProtocol import ProtocolRouter
from socket import socket
from ProtocolKinds import MainKind, SubKind

class SampleClientRecvMsgProtocol(ProtocolRouter):
    def __init__(self, sampleMgr: SampleClientManager) -> None:
        super().__init__()
        self._SampleMgr:SampleClientManager = sampleMgr
        self.register(MainKind.CONTROL, SubKind.STOP, self._stop_client)
        self.register(MainKind.CONTROL, SubKind.HEARTBEAT, self._heartbeat)
        self.register(MainKind.CHAT_BROADCAST, SubKind.BROADCAST_MESSAGE, self._show_other)
        self.register(MainKind.CHAT_ECHO, SubKind.ECHO_MESSAGE, self._show_me)

    def _stop_client(self, mainSocket: socket, msg: MyByteArray):
        self._SampleMgr.SampleStop()

    def _show_other(self, mainSocket: socket, msg: MyByteArray):
        self._SampleMgr.SampleShowOther(msg)

    def _show_me(self, mainSocket: socket, msg: MyByteArray):
        self._SampleMgr.SampleShowMe(msg)

    def _heartbeat(self, mainSocket: socket, msg: MyByteArray):
        return None
