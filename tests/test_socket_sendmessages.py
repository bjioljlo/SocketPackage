import pytest

from socket_package import MyByteArray
from socket_package.Protocol.FrameCodec import FrameDecoder
from socket_package.Protocol.MySocket import TSocket
from socket_package.Protocol.ProtocolKinds import MainKind, PROTOCOL_VERSION, SubKind


class _FakeSocket:
    def __init__(self) -> None:
        self.sent = bytearray()

    def sendall(self, data: bytes):
        self.sent.extend(data)


class _SocketImpl(TSocket):
    def Run(self, recvmainkind):
        return None

    def Stop(self):
        return None


def test_sendmessages_writes_header_and_payload_in_frame():
    sock = _FakeSocket()
    impl = _SocketImpl()
    body = MyByteArray()
    body.WriteStr("payload")

    impl.SendMessages(sock, 11, 22, body)

    frames = FrameDecoder().feed(bytes(sock.sent))
    assert len(frames) == 1

    msg = MyByteArray(frames[0])
    assert msg.ReadInt() == PROTOCOL_VERSION
    assert msg.ReadInt() == 11
    assert msg.ReadInt() == 22
    assert msg.ReadStr() == "payload"


def test_sendmessages_validates_arguments():
    impl = _SocketImpl()
    with pytest.raises(ValueError):
        impl.SendMessages(None, 1, 2, MyByteArray())
    with pytest.raises(ValueError):
        impl.SendMessages(_FakeSocket(), 1, 2, None)


def test_sendheartbeat_writes_control_message():
    sock = _FakeSocket()
    impl = _SocketImpl()
    impl.SendHeartbeat(sock)

    frames = FrameDecoder().feed(bytes(sock.sent))
    msg = MyByteArray(frames[0])
    assert msg.ReadInt() == PROTOCOL_VERSION
    assert msg.ReadInt() == MainKind.CONTROL
    assert msg.ReadInt() == SubKind.HEARTBEAT
