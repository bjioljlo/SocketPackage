import struct
from typing import List


_LENGTH_STRUCT = struct.Struct("I")


class FrameTooLargeError(ValueError):
    pass


def encode_frame(payload: bytes) -> bytes:
    return _LENGTH_STRUCT.pack(len(payload)) + payload


class FrameDecoder:
    def __init__(self, max_frame_size: int = 1024 * 1024) -> None:
        if max_frame_size <= 0:
            raise ValueError("max_frame_size must be positive.")
        self._buffer = bytearray()
        self._max_frame_size = max_frame_size

    def feed(self, data: bytes) -> List[bytes]:
        self._buffer.extend(data)
        frames: List[bytes] = []

        while len(self._buffer) >= _LENGTH_STRUCT.size:
            (length,) = _LENGTH_STRUCT.unpack_from(self._buffer, 0)
            if length > self._max_frame_size:
                self._buffer.clear()
                raise FrameTooLargeError(f"Frame too large: {length}, max allowed: {self._max_frame_size}")
            frame_end = _LENGTH_STRUCT.size + length
            if len(self._buffer) < frame_end:
                break
            frames.append(bytes(self._buffer[_LENGTH_STRUCT.size:frame_end]))
            del self._buffer[:frame_end]

        return frames
