import socket

import pytest

from socket_package.Protocol.FrameCodec import FrameDecoder
from socket_package.Protocol.MyByteArray import MyByteArray
from socket_package.Protocol.ProtocolKinds import MainKind, SubKind
from socket_package.Server.ServerSocket import ClientMeta, ServerSocket


class FakeSocket:
    def __init__(self, name: str):
        self.name = name
        self.sent = bytearray()

    def sendall(self, data: bytes):
        self.sent.extend(data)

    def fileno(self):
        return hash(self.name)

    def __repr__(self) -> str:
        return f"FakeSocket({self.name})"


def test_create_join_leave_room_updates_membership_and_owner_transfer():
    server = ServerSocket()
    socket_a = FakeSocket("A")
    socket_b = FakeSocket("B")

    server._register_client(socket_a)
    server._register_client(socket_b)

    server.CreateRoom("lobby", socket_a)
    assert server.GetClientRoom(socket_a) == "lobby"
    assert server.GetRoomOwner("lobby") == socket_a

    server.JoinRoom("lobby", socket_b)
    members = server.GetRoomMembers("lobby")
    assert set(members) == {socket_a, socket_b}

    server.LeaveRoom(socket_a)
    assert server.GetClientRoom(socket_a) is None
    assert server.GetRoomOwner("lobby") == socket_b

    server.LeaveRoom(socket_b)
    with pytest.raises(ValueError):
        server.GetRoomOwner("lobby")


def test_broadcast_room_messages_only_delivers_to_room_members():
    server = ServerSocket()
    socket_a = FakeSocket("A")
    socket_b = FakeSocket("B")
    socket_c = FakeSocket("C")

    server._register_client(socket_a)
    server._register_client(socket_b)
    server._register_client(socket_c)

    server.CreateRoom("room-1", socket_a)
    server.JoinRoom("room-1", socket_b)

    payload = MyByteArray()
    payload.WriteStr("hello room")

    server.BroadcastRoomMessages("room-1", socket_a, 1234, 5678, payload)

    assert len(socket_a.sent) == 0
    assert len(socket_c.sent) == 0

    frames = FrameDecoder().feed(bytes(socket_b.sent))
    assert len(frames) == 1
    message = MyByteArray(frames[0])
    assert message.ReadInt() == server.config.protocol_version
    assert message.ReadInt() == 1234
    assert message.ReadInt() == 5678
    assert message.ReadStr() == "hello room"


def test_transfer_room_ownership_to_existing_member():
    server = ServerSocket()
    socket_a = FakeSocket("A")
    socket_b = FakeSocket("B")

    server._register_client(socket_a)
    server._register_client(socket_b)

    server.CreateRoom("alpha", socket_a)
    server.JoinRoom("alpha", socket_b)

    server.TransferRoomOwnership("alpha", socket_b)
    assert server.GetRoomOwner("alpha") == socket_b
