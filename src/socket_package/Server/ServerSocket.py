import socket
import threading
import time

from socket_package.Protocol.FrameCodec import FrameDecoder, FrameTooLargeError
from socket_package.Protocol.MyByteArray import MyByteArray
from socket_package.Protocol.MySocket import TSocket
from socket_package.Protocol.ProtocolKinds import MainKind, SubKind
from socket_package.Protocol.RecvMsgProtocol import IRecvProtocol
from socket_package.Protocol.SocketConfig import ServerConfig


class ClientInfo:
    __slots__ = ("client_id", "client_socket", "last_heartbeat_time", "player_data")

    def __init__(self, client_id: int, client_socket: socket.socket, last_heartbeat_time: float) -> None:
        self.client_id = client_id
        self.client_socket = client_socket
        self.last_heartbeat_time = last_heartbeat_time
        self.player_data: dict[str, object] = {}


class ServerSocket(TSocket):
    def __init__(self, config: ServerConfig | None = None) -> None:
        self.__clients: dict[int, ClientInfo] = {}
        self.__socket_to_id: dict[int, int] = {}  # fileno -> client_id
        self.__clients_lock = threading.Lock()
        self.__server_socket: socket.socket | None = None
        self.__IsStop = False
        self.__config = config or ServerConfig()
        self.__next_client_id: int = 1

    @property
    def config(self) -> ServerConfig:
        return self.__config

    def get_client_info(self, client_id: int) -> ClientInfo | None:
        with self.__clients_lock:
            return self.__clients.get(client_id)

    def get_all_clients(self) -> dict[int, ClientInfo]:
        with self.__clients_lock:
            return dict(self.__clients)

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
                with self.__clients_lock:
                    client_id = self.__next_client_id
                    self.__next_client_id += 1
                    self.__clients[client_id] = ClientInfo(client_id, client_socket, time.time())
                    self.__socket_to_id[client_socket.fileno()] = client_id
                client_thread = threading.Thread(target=self._handle_client, args=(client_socket, client_id, recvProtocol), daemon=True)
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
            for client_info in list(self.__clients.values()):
                self.SendMessages(client_info.client_socket, MainKind.CONTROL, SubKind.STOP, MyByteArray(), self.__config.protocol_version)
                client_info.client_socket.close()

    def _handle_client(self, client_socket:socket, client_id: int, recvProtocol: IRecvProtocol):
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
                if main_kind == MainKind.CONTROL and sub_kind == SubKind.HEARTBEAT:
                    with self.__clients_lock:
                        if client_id in self.__clients:
                            self.__clients[client_id].last_heartbeat_time = time.time()
                    try:
                        self.SendMessages(client_socket, MainKind.CONTROL, SubKind.HEARTBEAT, MyByteArray(), self.__config.protocol_version)
                    except Exception:
                        pass
                    continue
                recvProtocol.recv_msg(client_socket, client_id, main_kind, sub_kind, aMsg)

        print("\n[Server][{}] ".format("Client disconnect...{}".format(client_id)))
        client_socket.close()
        with self.__clients_lock:
            if client_id in self.__clients:
                del self.__clients[client_id]
            if client_socket.fileno() in self.__socket_to_id:
                del self.__socket_to_id[client_socket.fileno()]

    def BroadcastMessages(self, client_socket: socket, main_kind: int, sub_kind: int, msg: MyByteArray, sendSelf: bool = False):
        """Broadcast a message to all the clients that are currently connected to the server.\n
        :param client_socket: The client socket that sent the message.\n
        :param main_kind: The main_kind of the message.\n
        :param sub_kind: The sub_kind of the message.\n
        :param msg: The message to be sent.\n
        :param sendSelf: Whether to send the message to the client that sent the message.\n
        :type sendSelf: bool, optional\n
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
            clients = list(self.__clients.values())

        for client_info in clients:
            client = client_info.client_socket
            if client is None:
                continue
            if client == client_socket:
                if not sendSelf: continue
            try:
                self.SendMessages(client, main_kind, sub_kind, msg)
            except Exception as e:
                print(f"Error sending message to client {client.fileno()}: {e}")