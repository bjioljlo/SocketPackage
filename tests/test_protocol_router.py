import pytest

from socket_package import MyByteArray
from socket_package.Protocol.RecvMsgProtocol import ProtocolRouter, UnhandledPolicy


def test_protocol_router_dispatches_registered_handler():
    router = ProtocolRouter()
    called = {"value": False, "message": ""}

    def handler(main_socket, msg: MyByteArray):
        called["value"] = True
        called["message"] = msg.ReadStr()

    router.register(100, 200, handler)
    payload = MyByteArray()
    payload.WriteStr("hello")

    router.recv_msg(mainSocket=None, main_kind=100, sub_kind=200, msg=payload)

    assert called["value"] is True
    assert called["message"] == "hello"


def test_protocol_router_calls_unhandled_when_route_missing():
    class TestRouter(ProtocolRouter):
        def __init__(self):
            super().__init__()
            self.unhandled = None

        def on_unhandled(self, mainSocket, main_kind: int, sub_kind: int, msg: MyByteArray):
            self.unhandled = (main_kind, sub_kind)

    router = TestRouter()
    router.recv_msg(mainSocket=None, main_kind=1, sub_kind=2, msg=MyByteArray())

    assert router.unhandled == (1, 2)


def test_protocol_router_ignores_unhandled_when_policy_ignore():
    router = ProtocolRouter(unhandled_policy=UnhandledPolicy.IGNORE)
    router.recv_msg(mainSocket=None, main_kind=8, sub_kind=9, msg=MyByteArray())


def test_protocol_router_raises_unhandled_when_policy_raise():
    router = ProtocolRouter(unhandled_policy=UnhandledPolicy.RAISE)
    with pytest.raises(KeyError):
        router.recv_msg(mainSocket=None, main_kind=8, sub_kind=9, msg=MyByteArray())
