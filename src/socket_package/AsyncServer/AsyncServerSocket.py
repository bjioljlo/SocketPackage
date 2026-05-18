import asyncio
from asyncio import StreamReader, StreamWriter

from socket_package.Protocol.AsyncRecvMsgProtocol import IAsyncRecvProtocol
from socket_package.Protocol.FrameCodec import FrameDecoder, FrameTooLargeError, encode_frame
from socket_package.Protocol.MyByteArray import MyByteArray
from socket_package.Protocol.ProtocolKinds import MainKind, PROTOCOL_VERSION, SubKind
from socket_package.Protocol.SocketConfig import ServerConfig


class AsyncServerSocket:
    def __init__(self, config: ServerConfig | None = None) -> None:
        self.__config = config or ServerConfig()
        self.__clients: list[StreamWriter] = []
        self.__clients_lock = asyncio.Lock()
        self.__server: asyncio.AbstractServer | None = None
        self.__is_stopped: bool = False

    @property
    def config(self) -> ServerConfig:
        return self.__config

    async def Run(self, recvProtocol: IAsyncRecvProtocol) -> None:
        """Start the async server and begin accepting connections."""
        self.__is_stopped = False
        self.__server = await asyncio.start_server(
            lambda reader, writer: self._handle_client(reader, writer, recvProtocol),
            host=self.__config.host,
            port=self.__config.port,
            backlog=self.__config.backlog,
        )
        addr = self.__server.sockets[0].getsockname()
        print(f"\n[AsyncServer][{addr}] Serving...")

        async with self.__server:
            await self.__server.serve_forever()

    async def _handle_client(
        self,
        reader: StreamReader,
        writer: StreamWriter,
        recvProtocol: IAsyncRecvProtocol,
    ) -> None:
        addr = writer.get_extra_info("peername")
        print(f"\n[AsyncServer][Accepted] {addr}")

        async with self.__clients_lock:
            self.__clients.append(writer)

        decoder = FrameDecoder(max_frame_size=self.__config.max_frame_size)
        try:
            while True:
                data = await reader.read(self.__config.buffer_size)
                if not data:
                    break
                try:
                    frames = decoder.feed(data)
                except FrameTooLargeError as error:
                    print(f"\n[AsyncServer][FrameError] {error}")
                    break
                for frame in frames:
                    aMsg = MyByteArray(frame)
                    version = aMsg.ReadInt()
                    main_kind = aMsg.ReadInt()
                    sub_kind = aMsg.ReadInt()
                    if version != self.__config.protocol_version:
                        print(
                            "\n[AsyncServer][VersionMismatch] recv={}, expected={}".format(
                                version, self.__config.protocol_version
                            )
                        )
                        continue
                    if main_kind == MainKind.CONTROL and sub_kind == SubKind.HEARTBEAT:
                        continue
                    await recvProtocol.recv_msg(writer, main_kind, sub_kind, aMsg)
        except Exception:
            pass
        finally:
            print(f"\n[AsyncServer][Disconnected] {addr}")
            async with self.__clients_lock:
                if writer in self.__clients:
                    self.__clients.remove(writer)
            try:
                writer.close()
            except Exception:
                pass

    def SendMessages(
        self,
        writer: StreamWriter,
        main_kind: int,
        sub_kind: int,
        msg: MyByteArray,
        protocol_version: int = PROTOCOL_VERSION,
    ) -> None:
        """Encode and send a framed message to a specific client."""
        if writer is None:
            raise ValueError("writer is None.")
        if msg is None:
            raise ValueError("msg is None.")

        print("\n SendMessages :{} - {}".format(main_kind, sub_kind))
        aMsg = MyByteArray()
        aMsg.WriteInt(protocol_version)
        aMsg.WriteInt(main_kind)
        aMsg.WriteInt(sub_kind)
        payload = aMsg.Msg + msg.Msg
        encoded = encode_frame(payload)
        writer.write(encoded)

    async def BroadcastMessages(
        self,
        sender_writer: StreamWriter,
        main_kind: int,
        sub_kind: int,
        msg: MyByteArray,
        sendSelf: bool = False,
    ) -> None:
        """Broadcast a framed message to all connected clients."""
        if sender_writer is None:
            raise ValueError("sender_writer is None.")
        if msg is None:
            raise ValueError("msg is None.")

        async with self.__clients_lock:
            clients = list(self.__clients)

        for client_writer in clients:
            if client_writer == sender_writer and not sendSelf:
                continue
            try:
                self.SendMessages(client_writer, main_kind, sub_kind, msg)
            except Exception as e:
                print(f"Error sending to client: {e}")

    async def Stop(self) -> None:
        """Stop the server and close all client connections."""
        print("\n[AsyncServer][{}] ".format("Stop"))
        self.__is_stopped = True

        async with self.__clients_lock:
            for writer in list(self.__clients):
                try:
                    writer.close()
                except Exception:
                    pass
            self.__clients.clear()

        if self.__server is not None:
            self.__server.close()