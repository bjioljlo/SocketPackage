import socket
import threading

from dataclasses import dataclass, field
from typing import Dict, Optional, Set

from socket_package.Protocol.FrameCodec import FrameDecoder, FrameTooLargeError
from socket_package.Protocol.MyByteArray import MyByteArray
from socket_package.Protocol.MySocket import TSocket
from socket_package.Protocol.ProtocolKinds import MainKind, SubKind
from socket_package.Protocol.RecvMsgProtocol import IRecvProtocol
from socket_package.Protocol.SocketConfig import ServerConfig


@dataclass
class ClientMeta:
    room_name: Optional[str] = None


@dataclass
class RoomMeta:
    members: Set[socket.socket] = field(default_factory=set)
    owner: Optional[socket.socket] = None


class ServerSocket(TSocket):
    def __init__(self, config: ServerConfig | None = None) -> None:
        self.__clients: Dict[socket.socket, ClientMeta] = {}
        self.__rooms: Dict[str, RoomMeta] = {}
        self.__clients_lock = threading.Lock()
        self.__server_socket: socket.socket | None = None
        self.__IsStop = False
        self.__config = config or ServerConfig()

    @property
    def config(self) -> ServerConfig:
        return self.__config

    def _register_client(self, client_socket: socket.socket) -> None:
        if client_socket is None:
            raise ValueError("client_socket is None.")
        with self.__clients_lock:
            self.__clients[client_socket] = ClientMeta()

    def Run(self, recvProtocol: IRecvProtocol):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__server_socket = server_socket
        server_socket.bind((self.__config.host, self.__config.port))
        server_socket.listen(self.__config.backlog)
        server_socket.settimeout(self.__config.accept_timeout_sec)
        print("\n[Server][{}] ".format("Listening for connections..."))
        while not self.__IsStop:
            try:
                print("\n[Server][{}] ".format("Start Accepted connection..."))
                client_socket, addr = server_socket.accept()
                print("\n[Server][{}] ".format("Accepted connection from {}:{}".format(addr[0], addr[1])))
                self._register_client(client_socket)
                client_thread = threading.Thread(target=self._handle_client, args=(client_socket, recvProtocol), daemon=True)
                client_thread.start()
            except socket.timeout:
                print("\n[Server][{}] ".format("Socket timeout ..."))
            except OSError:
                break
        print("\n[Server][{}] ".format("Shutdown ..."))
        server_socket.close()

    def Stop(self):
        print("\n[Server][{}] ".format("Run Stop"))
        self.__IsStop = True
        if self.__server_socket is not None:
            self.__server_socket.close()
        with self.__clients_lock:
            for client in list(self.__clients.keys()):
                self.SendMessages(client, MainKind.CONTROL, SubKind.STOP, MyByteArray(), self.__config.protocol_version)
                client.close()

    def _remove_client_from_room_no_lock(self, client_socket: socket.socket) -> None:
        client_meta = self.__clients.get(client_socket)
        if not client_meta or client_meta.room_name is None:
            return

        room_name = client_meta.room_name
        room = self.__rooms.get(room_name)
        client_meta.room_name = None
        if room is None:
            return

        room.members.discard(client_socket)
        if room.owner == client_socket:
            if room.members:
                room.owner = next(iter(room.members))
            else:
                self.__rooms.pop(room_name, None)
                return

        if not room.members:
            self.__rooms.pop(room_name, None)

    def _validate_room_name(self, room_name: str) -> None:
        if room_name is None or not isinstance(room_name, str) or not room_name.strip():
            raise ValueError("room_name must be a non-empty string.")

    def CreateRoom(self, room_name: str, client_socket: socket.socket) -> None:
        self._validate_room_name(room_name)
        if client_socket is None:
            raise ValueError("client_socket is None.")

        with self.__clients_lock:
            if room_name in self.__rooms:
                raise ValueError(f"Room '{room_name}' already exists.")
            client_meta = self.__clients.get(client_socket)
            if client_meta is None:
                raise ValueError("client_socket is not registered.")
            if client_meta.room_name is not None:
                raise ValueError("client_socket is already in a room.")

            self.__rooms[room_name] = RoomMeta(members={client_socket}, owner=client_socket)
            client_meta.room_name = room_name

    def JoinRoom(self, room_name: str, client_socket: socket.socket) -> None:
        self._validate_room_name(room_name)
        if client_socket is None:
            raise ValueError("client_socket is None.")

        with self.__clients_lock:
            room = self.__rooms.get(room_name)
            if room is None:
                raise ValueError(f"Room '{room_name}' does not exist.")
            client_meta = self.__clients.get(client_socket)
            if client_meta is None:
                raise ValueError("client_socket is not registered.")
            if client_meta.room_name is not None:
                raise ValueError("client_socket is already in a room.")

            room.members.add(client_socket)
            client_meta.room_name = room_name

    def LeaveRoom(self, client_socket: socket.socket) -> None:
        if client_socket is None:
            raise ValueError("client_socket is None.")

        with self.__clients_lock:
            client_meta = self.__clients.get(client_socket)
            if client_meta is None:
                raise ValueError("client_socket is not registered.")
            if client_meta.room_name is None:
                return
            self._remove_client_from_room_no_lock(client_socket)

    def TransferRoomOwnership(self, room_name: str, new_owner_socket: socket.socket) -> None:
        self._validate_room_name(room_name)
        if new_owner_socket is None:
            raise ValueError("new_owner_socket is None.")

        with self.__clients_lock:
            room = self.__rooms.get(room_name)
            if room is None:
                raise ValueError(f"Room '{room_name}' does not exist.")
            if new_owner_socket not in room.members:
                raise ValueError("new_owner_socket must be a member of the room.")
            room.owner = new_owner_socket

    def GetRoomMembers(self, room_name: str) -> list[socket.socket]:
        self._validate_room_name(room_name)
        with self.__clients_lock:
            room = self.__rooms.get(room_name)
            if room is None:
                raise ValueError(f"Room '{room_name}' does not exist.")
            return list(room.members)

    def GetRoomOwner(self, room_name: str) -> socket.socket:
        self._validate_room_name(room_name)
        with self.__clients_lock:
            room = self.__rooms.get(room_name)
            if room is None:
                raise ValueError(f"Room '{room_name}' does not exist.")
            if room.owner is None:
                raise ValueError(f"Room '{room_name}' has no owner.")
            return room.owner

    def GetClientRoom(self, client_socket: socket.socket) -> Optional[str]:
        if client_socket is None:
            raise ValueError("client_socket is None.")
        with self.__clients_lock:
            client_meta = self.__clients.get(client_socket)
            if client_meta is None:
                raise ValueError("client_socket is not registered.")
            return client_meta.room_name

    def _handle_client(self, client_socket:socket, recvProtocol: IRecvProtocol):
        decoder = FrameDecoder(max_frame_size=self.__config.max_frame_size)
        while True:
            try:
                request:bytearray = client_socket.recv(self.__config.buffer_size)
            except Exception:
                break
            if not request:
                break
            try:
                frames = decoder.feed(request)
            except FrameTooLargeError as error:
                print(f"\n[Server][FrameError] {error}")
                break
            for frame in frames:
                aMsg = MyByteArray(frame)
                version = aMsg.ReadInt()
                main_kind = aMsg.ReadInt()
                sub_kind = aMsg.ReadInt()
                if version != self.__config.protocol_version:
                    print(
                        "\n[Server][VersionMismatch] recv={}, expected={}".format(
                            version, self.__config.protocol_version
                        )
                    )
                    continue
                # Auto-respond to Ping with Pong echoing timestamp
                if main_kind == MainKind.CONTROL:
                    if sub_kind == SubKind.HEARTBEAT:
                        continue
                    if sub_kind == SubKind.PING:
                        try:
                            sent_ts = aMsg.ReadInt64()
                            out = MyByteArray()
                            out.WriteInt64(sent_ts)
                            self.SendMessages(client_socket, MainKind.CONTROL, SubKind.PONG, out, self.__config.protocol_version)
                        except Exception:
                            pass
                        continue
                recvProtocol.recv_msg(client_socket, main_kind, sub_kind, aMsg)

        with self.__clients_lock:
            client_index = list(self.__clients).index(client_socket) if client_socket in self.__clients else -1
        print("\n[Server][{}] ".format("Client disconnect...{}".format(client_index)))
        client_socket.close()
        with self.__clients_lock:
            self._remove_client_from_room_no_lock(client_socket)
            self.__clients.pop(client_socket, None)

    def BroadcastMessages(self, client_socket: socket, main_kind: int, sub_kind: int, msg: MyByteArray, sendSelf: bool = False):
        """Broadcast a message to all the clients that are currently connected to the server.
        :param client_socket: The client socket that sent the message.
        :param main_kind: The main_kind of the message.
        :param sub_kind: The sub_kind of the message.
        :param msg: The message to be sent.
        :param sendSelf: Whether to send the message to the client that sent the message.
        :type sendSelf: bool, optional
        """
        if client_socket is None:
            raise ValueError("client_socket is None.")
        if main_kind is None:
            raise ValueError("main_kind is None.")
        if sub_kind is None:
            raise ValueError("sub_kind is None.")
        if msg is None:
            raise ValueError("msg is None.")
        with self.__clients_lock:
            clients = list(self.__clients.keys())

        for client in clients:
            if client is None:
                continue
            if client == client_socket:
                if not sendSelf:
                    continue
            try:
                self.SendMessages(client, main_kind, sub_kind, msg)
            except Exception as e:
                print(f"Error sending message to client {client.fileno()}: {e}")

    def BroadcastRoomMessages(self, room_name: str, client_socket: socket.socket, main_kind: int, sub_kind: int, msg: MyByteArray, sendSelf: bool = False):
        if room_name is None:
            raise ValueError("room_name is None.")
        if client_socket is None:
            raise ValueError("client_socket is None.")
        if main_kind is None:
            raise ValueError("main_kind is None.")
        if sub_kind is None:
            raise ValueError("sub_kind is None.")
        if msg is None:
            raise ValueError("msg is None.")

        with self.__clients_lock:
            room = self.__rooms.get(room_name)
            if room is None:
                raise ValueError(f"Room '{room_name}' does not exist.")
            recipients = list(room.members)

        for client in recipients:
            if client == client_socket and not sendSelf:
                continue
            try:
                self.SendMessages(client, main_kind, sub_kind, msg)
            except Exception as e:
                print(f"Error sending room message to client {client.fileno()}: {e}")
