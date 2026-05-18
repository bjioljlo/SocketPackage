from socket import socket

from socket_package import MyByteArray
from socket_package.Protocol.RecvMsgProtocol import ProtocolRouter

from tests.examples.ProtocolKinds import MainKind, SubKind
from tests.examples.SampleServerManager import SampleServerManager


class SampleServerRecvMsgProtocol(ProtocolRouter):
    def __init__(self, sampleMgr: SampleServerManager) -> None:
        super().__init__()
        self._SampleMgr: SampleServerManager = sampleMgr
        self.register(MainKind.CONTROL, SubKind.STOP, self._stop_server)
        self.register(MainKind.CONTROL, SubKind.HEARTBEAT, self._on_heartbeat)
        self.register(MainKind.CHAT, SubKind.CLIENT_MESSAGE, self._on_client_message)

    def _stop_server(self, mainSocket: socket, client_id: int, msg: MyByteArray):
        self._SampleMgr.SampleStop()

    def _on_heartbeat(self, mainSocket: socket, client_id: int, msg: MyByteArray):
        return None

    def _on_client_message(self, mainSocket: socket, client_id: int, msg: MyByteArray):
        message: str = msg.ReadStr()
        aMsg = MyByteArray()
        aMsg.WriteStr(message)
        self._SampleMgr.SampleBroadcastMessages(mainSocket, aMsg)
        self._SampleMgr.SampleSendMsg(mainSocket, aMsg)
