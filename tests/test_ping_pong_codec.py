import time
from socket_package.Protocol.MyByteArray import MyByteArray


def test_int64_roundtrip():
    mba = MyByteArray()
    mba.WriteInt64(1610000000000)
    data = mba.Msg
    mba2 = MyByteArray(data)
    val = mba2.ReadInt64()
    assert val == 1610000000000
