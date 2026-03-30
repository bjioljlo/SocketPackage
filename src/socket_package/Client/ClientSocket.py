import socket
import threading
import time

from socket_package.Protocol.FrameCodec import FrameDecoder, FrameTooLargeError
from socket_package.Protocol.MyByteArray import MyByteArray
from socket_package.Protocol.MySocket import TSocket
from socket_package.Protocol.ProtocolKinds import MainKind, SubKind
from socket_package.Protocol.RecvMsgProtocol import IRecvProtocol
from socket_package.Protocol.SocketConfig import ClientConfig

class ClientSocket(TSocket):
    @property
    def mainSocket(self) -> socket:
        return self.__client_socket

    @property
    def IsConnect(self) -> bool:
        return self.__IsConnect

    @property
    def IsShutDown(self) -> bool:
        return self.__IsShutDown

    def __init__(self, config: ClientConfig | None = None) -> None:
        self.__client_socket: socket.socket | None = None
        self.__IsConnect: bool = False
        self.__IsShutDown: bool = False
        self.__config = config or ClientConfig()

    @property
    def config(self) -> ClientConfig:
        return self.__config

    def Run(self, recvProtocol: IRecvProtocol):
        """
        Establishes a connection to the server and starts a thread to receive messages.

        This method attempts to connect to a server at a specified IP address and port.
        Once connected, it spawns a new thread to handle incoming messages using the
        provided `recvProtocol` protocol. The connection process will retry until
        successful or until the client is manually stopped.

        :param recvProtocol: An instance implementing the IRecvProtocol interface,
                            responsible for handling received messages.
        """
        while not self.__IsConnect:
            if not self.__IsConnect and recvProtocol is not None:
                try:
                    print("\n[Client][{}] ".format("Start Run Client Socket"))
                    self.__client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    self.__client_socket.connect((self.__config.host, self.__config.port))
                    receive_thread = threading.Thread(target=self._receive_messages, args=(self.__client_socket, recvProtocol), daemon=True)
                    receive_thread.start()
                    self.__IsConnect = True
                except Exception:
                    print("\n[Client][{}] ".format("Server can not connect!"))
                    time.sleep(self.__config.retry_interval_sec)

    def Stop(self):
        """
        Stops the client and closes the connection to the server.

        This method closes the socket used to communicate with the server and
        sets the `IsShutDown` flag to True. It can be used to manually stop the
        client.
        """
        #TODO 結束client之前要完成的事
        print("\n[Client][{}] ".format("Stop"))
        if self.__client_socket is not None:
            self.__client_socket.close()
        self.__IsShutDown = True

    def _receive_messages(self, client_socket:socket, recvProtocol: IRecvProtocol):
        decoder = FrameDecoder(max_frame_size=self.__config.max_frame_size)
        while True:
            try:
                response:bytearray = client_socket.recv(self.__config.buffer_size)
            except Exception:
                break
            if not response:
                break
            try:
                frames = decoder.feed(response)
            except FrameTooLargeError as error:
                print(f"\n[Client][FrameError] {error}")
                break
            for frame in frames:
                aMsg = MyByteArray(frame)
                version = aMsg.ReadInt()
                main_kind = aMsg.ReadInt()
                sub_kind = aMsg.ReadInt()
                if version != self.__config.protocol_version:
                    print(
                        "\n[Client][VersionMismatch] recv={}, expected={}".format(
                            version, self.__config.protocol_version
                        )
                    )
                    continue
                if main_kind == MainKind.CONTROL and sub_kind == SubKind.HEARTBEAT:
                    continue
                recvProtocol.recv_msg(client_socket, main_kind, sub_kind, aMsg)
        print("\n[Client][{}] ".format("Server disconnect..."))
        client_socket.close()
        self.__IsConnect = False
