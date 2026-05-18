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
        self.__stop_heartbeat_event: threading.Event = threading.Event()
        self._last_rtt_ms: float | None = None

    def get_rtt_ms(self) -> float | None:
        """Return last measured RTT in milliseconds or None if not measured."""
        return self._last_rtt_ms

    def send_ping(self) -> None:
        """Send a Ping control message containing current timestamp in ms."""
        if self.__client_socket is None:
            raise ValueError("Not connected")
        msg = MyByteArray()
        now_ms = int(time.time() * 1000)
        msg.WriteInt64(now_ms)
        self.SendMessages(self.__client_socket, MainKind.CONTROL, SubKind.PING, msg, self.__config.protocol_version)

    @property
    def config(self) -> ClientConfig:
        return self.__config

    def BroadcastMessages(
        self,
        client_socket: socket.socket,
        main_kind: int,
        sub_kind: int,
        msg: MyByteArray,
        sendSelf: bool = False,
    ) -> None:
        """Single upstream connection: broadcast is a normal framed send on that socket."""
        if client_socket is None:
            raise ValueError("client_socket is None.")
        if msg is None:
            raise ValueError("msg is None.")
        self.SendMessages(client_socket, main_kind, sub_kind, msg)

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
                    self.__stop_heartbeat_event.clear()
                    heartbeat_thread = threading.Thread(target=self._heartbeat_loop, daemon=True)
                    heartbeat_thread.start()
                    self.__heartbeat_thread = heartbeat_thread
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
        self.__stop_heartbeat_event.set()
        if self.__client_socket is not None:
            self.__client_socket.close()
        self.__IsShutDown = True

    def _heartbeat_loop(self):
        while not self.__stop_heartbeat_event.is_set():
            if self.__client_socket is not None and self.__IsConnect:
                try:
                    self.SendHeartbeat(self.__client_socket, self.__config.protocol_version)
                except Exception:
                    pass
            self.__stop_heartbeat_event.wait(timeout=self.__config.heartbeat_interval_sec)

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
                # Handle control messages locally
                if main_kind == MainKind.CONTROL:
                    if sub_kind == SubKind.HEARTBEAT:
                        continue
                    if sub_kind == SubKind.PONG:
                        try:
                            sent_ts = aMsg.ReadInt64()
                            now_ms = int(time.time() * 1000)
                            self._last_rtt_ms = float(now_ms - sent_ts)
                        except Exception:
                            pass
                        continue
                recvProtocol.recv_msg(client_socket, main_kind, sub_kind, aMsg)
        print("\n[Client][{}] ".format("Server disconnect..."))
        client_socket.close()
        self.__IsConnect = False