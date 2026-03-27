import pytest

from socket_package.Protocol.FrameCodec import FrameDecoder, FrameTooLargeError, encode_frame


def test_encode_frame_prefixes_length():
    payload = b"abc"
    frame = encode_frame(payload)
    assert frame[:4] == (3).to_bytes(4, "little")
    assert frame[4:] == payload


def test_frame_decoder_supports_fragmented_input():
    payload = b"hello-world"
    frame = encode_frame(payload)
    decoder = FrameDecoder()

    assert decoder.feed(frame[:5]) == []
    assert decoder.feed(frame[5:]) == [payload]


def test_frame_decoder_supports_multiple_frames():
    p1 = b"one"
    p2 = b"two"
    decoder = FrameDecoder()

    out = decoder.feed(encode_frame(p1) + encode_frame(p2))
    assert out == [p1, p2]


def test_frame_decoder_rejects_too_large_frame():
    decoder = FrameDecoder(max_frame_size=2)
    with pytest.raises(FrameTooLargeError):
        decoder.feed(encode_frame(b"abc"))
