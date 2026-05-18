import asyncio
from asyncio import StreamReader, StreamWriter

from socket_package.Protocol.AsyncRecvMsgProtocol import IAsyncRecvProtocol
from socket_package.Protocol.FrameCodec import FrameDecoder, FrameTooLargeError, encode_frame
from socket_package.Protocol.MyByteArray import MyByteArray
from socket_package.Protocol.ProtocolKinds import MainKind, PROTOCOL_VERSION, SubKind
from socket_package.Protocol.SocketConfig import ClientConfig


class AsyncClientSocket:
    def __init__(self, config: ClientConfig | None = None) -> None:
        self.__reader: StreamReader | None = None
        self.__writer: StreamWriter | None = None
        self.__config = config or ClientConfig()
        self.__is_connected: bool = False

    @property
    def config(self) -> ClientConfig:
        return self.__config

    @property
    def is_connected(self) -> bool:
        return self.__is_connected

    async def Run(self, recvProtocol: IAsyncRecvProtocol) -> None:
        """Connect to the server and start reading messages asynchronously."""
        try:
            self.__reader, self.__writer = await asyncio.open_connection(
                self.__config.host, self.__config.port
            )
            self.__is_connected = True
            print("\n[AsyncClient][{}] ".format("Connected to server"))
            await self._receive_messages(recvProtocol)
        except (ConnectionRefusedError, OSError) as e:
            print("\n[AsyncClient][{}] ".format(f"Connection failed: {e}"))
            raise

    async def _receive_messages(self, recvProtocol: IAsyncRecvProtocol) -> None:
        decoder = FrameDecoder(max_frame_size=self.__config.max_frame_size)
        try:
            while True:
                data = await self.__reader.read(self.__config.buffer_size)
                if not data:
                    break
                try:
                    frames = decoder.feed(data)
                except FrameTooLargeError as error:
                    print(f"\n[AsyncClient][FrameError] {error}")
                    break
                for frame in frames:
                    aMsg = MyByteArray(frame)
                    version = aMsg.ReadInt()
                    main_kind = aMsg.ReadInt()
                    sub_kind = aMsg.ReadInt()
                    if version != self.__config.protocol_version:
                        print(
                            "\n[AsyncClient][VersionMismatch] recv={}, expected={}".format(
                                version, self.__config.protocol_version
                            )
                        )
                        continue
                    if main_kind == MainKind.CONTROL and sub_kind == SubKind.HEARTBEAT:
                        continue
                    await recvProtocol.recv_msg(self.__writer, main_kind, sub_kind, aMsg)
        except Exception:
            pass
        finally:
            print("\n[AsyncClient][{}] ".format("Server disconnected"))
            self._close()

    def SendMessages(
        self,
        main_kind: int,
        sub_kind: int,
        msg: MyByteArray,
        protocol_version: int = PROTOCOL_VERSION,
    ) -> None:
        """Encode and send a framed message via the writer. Non-async because write is buffered."""
        if self.__writer is None:
            raise ValueError("Not connected.")
        if msg is None:
            raise ValueError("msg is None.")

        print("\n SendMessages :{} - {}".format(main_kind, sub_kind))
        aMsg = MyByteArray()
        aMsg.WriteInt(protocol_version)
        aMsg.WriteInt(main_kind)
        aMsg.WriteInt(sub_kind)
        payload = aMsg.Msg + msg.Msg
        encoded = encode_frame(payload)
        self.__writer.write(encoded)

    async def Stop(self) -> None:
        """Close the connection cleanly."""
        print("\n[AsyncClient][{}] ".format("Stop"))
        self._close()

    def _close(self) -> None:
        self.__is_connected = False
        if self.__writer is not None:
            try:
                self.__writer.close()
            except Exception:
                pass
            self.__writer = None
        self.__reader = None