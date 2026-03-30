from socket_package.Client import ClientSocket
from socket_package.Protocol.ProtocolKinds import MainKind as CoreMainKind
from socket_package.Protocol.ProtocolKinds import PROTOCOL_VERSION
from socket_package.Protocol.ProtocolKinds import SubKind as CoreSubKind
from socket_package.Protocol.SocketConfig import ClientConfig, ServerConfig
from socket_package.Server import ServerSocket

from ProtocolKinds import MainKind, SubKind
from SampleClientRecvMsgProtocol import SampleClientRecvMsgProtocol
from SampleServerRecvMsgProtocol import SampleServerRecvMsgProtocol
from socket_package import MyByteArray


def test_package_exposes_only_core_protocol_kinds():
    assert [kind.value for kind in CoreMainKind] == [0]
    assert [kind.value for kind in CoreSubKind] == [0, 1]


def test_client_socket_uses_injected_config():
    cfg = ClientConfig(
        host="192.168.0.10",
        port=7788,
        buffer_size=2048,
        retry_interval_sec=0.5,
        protocol_version=PROTOCOL_VERSION,
        max_frame_size=8192,
    )
    client = ClientSocket(cfg)
    assert client.config == cfg


def test_server_socket_uses_injected_config():
    cfg = ServerConfig(
        host="127.0.0.1",
        port=8899,
        backlog=10,
        accept_timeout_sec=0.2,
        buffer_size=2048,
        protocol_version=PROTOCOL_VERSION,
        max_frame_size=8192,
    )
    server = ServerSocket(cfg)
    assert server.config == cfg


def test_sample_server_protocol_routes_stop_and_chat():
    class FakeServerManager:
        def __init__(self):
            self.stopped = False
            self.broadcast = None
            self.echo = None

        def SampleStop(self):
            self.stopped = True

        def SampleBroadcastMessages(self, mainSocket, aMsg: MyByteArray):
            self.broadcast = MyByteArray(aMsg.Msg).ReadStr()

        def SampleSendMsg(self, mainSocket, aMsg: MyByteArray):
            self.echo = MyByteArray(aMsg.Msg).ReadStr()

    mgr = FakeServerManager()
    protocol = SampleServerRecvMsgProtocol(mgr)

    protocol.recv_msg(None, MainKind.CONTROL, SubKind.STOP, MyByteArray())
    assert mgr.stopped is True

    protocol.recv_msg(None, MainKind.CONTROL, SubKind.HEARTBEAT, MyByteArray())

    chat = MyByteArray()
    chat.WriteStr("hi")
    protocol.recv_msg(None, MainKind.CHAT, SubKind.CLIENT_MESSAGE, chat)
    assert mgr.broadcast == "hi"
    assert mgr.echo == "hi"


def test_sample_client_protocol_routes_actions():
    class FakeClientManager:
        def __init__(self):
            self.stopped = False
            self.other = None
            self.me = None

        def SampleStop(self):
            self.stopped = True

        def SampleShowOther(self, msg: MyByteArray):
            self.other = msg.ReadStr()

        def SampleShowMe(self, msg: MyByteArray):
            self.me = msg.ReadStr()

    mgr = FakeClientManager()
    protocol = SampleClientRecvMsgProtocol(mgr)

    protocol.recv_msg(None, MainKind.CONTROL, SubKind.STOP, MyByteArray())
    assert mgr.stopped is True

    protocol.recv_msg(None, MainKind.CONTROL, SubKind.HEARTBEAT, MyByteArray())

    other = MyByteArray()
    other.WriteStr("other-msg")
    protocol.recv_msg(None, MainKind.CHAT_BROADCAST, SubKind.BROADCAST_MESSAGE, other)
    assert mgr.other == "other-msg"

    me = MyByteArray()
    me.WriteStr("me-msg")
    protocol.recv_msg(None, MainKind.CHAT_ECHO, SubKind.ECHO_MESSAGE, me)
    assert mgr.me == "me-msg"
