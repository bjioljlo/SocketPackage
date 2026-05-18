import socket
import threading
import time

import pytest

from socket_package.Protocol.FrameCodec import FrameDecoder, encode_frame
from socket_package.Protocol.MyByteArray import MyByteArray
from socket_package.Protocol.RecvMsgProtocol import ProtocolRouter, UnhandledPolicy
from socket_package.Protocol.ProtocolKinds import PROTOCOL_VERSION
from socket_package.Protocol.SocketConfig import ServerConfig
from socket_package.Server.ServerSocket import ServerSocket


class RoomServerProtocol(ProtocolRouter):
    CREATE_ROOM = 100
    JOIN_ROOM = 101
    ROOM_MESSAGE = 102

    def __init__(self, server: ServerSocket) -> None:
        super().__init__(UnhandledPolicy.RAISE)
        self._server = server
        self.register(100, 1, self._create_room)
        self.register(101, 1, self._join_room)
        self.register(102, 1, self._room_message)

    def _create_room(self, mainSocket: socket.socket, msg: MyByteArray) -> None:
        room_name = msg.ReadStr()
        self._server.CreateRoom(room_name, mainSocket)

    def _join_room(self, mainSocket: socket.socket, msg: MyByteArray) -> None:
        room_name = msg.ReadStr()
        self._server.JoinRoom(room_name, mainSocket)

    def _room_message(self, mainSocket: socket.socket, msg: MyByteArray) -> None:
        room_name = msg.ReadStr()
        message = msg.ReadStr()
        payload = MyByteArray()
        payload.WriteStr(message)
        self._server.BroadcastRoomMessages(room_name, mainSocket, 200, 201, payload)


class RoomClient:
    def __init__(self, host: str, port: int):
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.connect((host, port))
        self._decoder = FrameDecoder()
        self.messages: list[str] = []
        self._running = True
        self._thread = threading.Thread(target=self._receive_loop, daemon=True)
        self._thread.start()

    def _receive_loop(self) -> None:
        while self._running:
            try:
                data = self._sock.recv(4096)
            except OSError:
                break
            if not data:
                break
            for frame in self._decoder.feed(data):
                msg = MyByteArray(frame)
                protocol = msg.ReadInt()
                main_kind = msg.ReadInt()
                sub_kind = msg.ReadInt()
                if protocol != PROTOCOL_VERSION:
                    continue
                if main_kind == 200 and sub_kind == 201:
                    self.messages.append(msg.ReadStr())

    def send(self, main_kind: int, sub_kind: int, payload: MyByteArray) -> None:
        packet = MyByteArray()
        packet.WriteInt(PROTOCOL_VERSION)
        packet.WriteInt(main_kind)
        packet.WriteInt(sub_kind)
        payload_bytes = packet.Msg + payload.Msg
        self._sock.sendall(encode_frame(bytes(payload_bytes)))

    def close(self) -> None:
        self._running = False
        try:
            self._sock.close()
        except OSError:
            pass
        self._thread.join(timeout=1)


def _find_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


@pytest.mark.integration
def test_room_broadcasts_only_to_room_members():
    port = _find_free_port()
    server = ServerSocket(ServerConfig(host="127.0.0.1", port=port))
    protocol = RoomServerProtocol(server)
    server_thread = threading.Thread(target=server.Run, args=(protocol,), daemon=True)
    server_thread.start()

    time.sleep(0.1)

    client_a = RoomClient("127.0.0.1", port)
    client_b = RoomClient("127.0.0.1", port)
    client_c = RoomClient("127.0.0.1", port)

    try:
        create_payload = MyByteArray()
        create_payload.WriteStr("game-room")
        client_a.send(100, 1, create_payload)

        join_payload = MyByteArray()
        join_payload.WriteStr("game-room")
        client_b.send(101, 1, join_payload)

        time.sleep(0.1)

        room_payload = MyByteArray()
        room_payload.WriteStr("game-room")
        room_payload.WriteStr("hello room")
        client_a.send(102, 1, room_payload)

        time.sleep(0.2)

        assert client_b.messages == ["hello room"]
        assert client_c.messages == []
    finally:
        client_a.close()
        client_b.close()
        client_c.close()
        server.Stop()
        server_thread.join(timeout=1)
