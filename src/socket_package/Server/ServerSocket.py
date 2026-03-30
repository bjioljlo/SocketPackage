import socket
import threading

from socket_package.Protocol.FrameCodec import FrameDecoder, FrameTooLargeError
from socket_package.Protocol.MyByteArray import MyByteArray
from socket_package.Protocol.MySocket import TSocket
from socket_package.Protocol.ProtocolKinds import MainKind, SubKind
from socket_package.Protocol.RecvMsgProtocol import IRecvProtocol
from socket_package.Protocol.SocketConfig import ServerConfig

class ServerSocket(TSocket):
    def __init__(self, config: ServerConfig | None = None) -> None:
        self.__clients: list[socket.socket] = []
        self.__clients_lock = threading.Lock()
        self.__server_socket: socket.socket | None = None
        self.__IsStop = False
        self.__config = config or ServerConfig()

    @property
    def config(self) -> ServerConfig:
        return self.__config

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
                    self.__clients.append(client_socket)
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
            for client in list(self.__clients):
                self.SendMessages(client, MainKind.CONTROL, SubKind.STOP, MyByteArray(), self.__config.protocol_version)
                client.close()

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
                if main_kind == MainKind.CONTROL and sub_kind == SubKind.HEARTBEAT:
                    continue
                recvProtocol.recv_msg(client_socket, main_kind, sub_kind, aMsg)

        with self.__clients_lock:
            client_index = self.__clients.index(client_socket) if client_socket in self.__clients else -1
        print("\n[Server][{}] ".format("Client disconnect...{}".format(client_index)))
        client_socket.close()
        with self.__clients_lock:
            if client_socket in self.__clients:
                self.__clients.remove(client_socket)

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
            clients = list(self.__clients)

        for client in clients:
            if client is None:
                continue
            if client == client_socket:
                if not sendSelf: continue
            try:
                self.SendMessages(client, main_kind, sub_kind, msg)
            except Exception as e:
                print(f"Error sending message to client {client.fileno()}: {e}")
