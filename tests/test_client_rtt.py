import time
from socket_package.Protocol.MyByteArray import MyByteArray


def test_client_rtt_computation():
    # simulate client sending ping and later receiving pong with same timestamp
    sent_ts = int(time.time() * 1000)
    mba = MyByteArray()
    mba.WriteInt64(sent_ts)
    # simulate network delay
    time.sleep(0.01)
    mba2 = MyByteArray(mba.Msg)
    recv_ts = int(time.time() * 1000)
    val = mba2.ReadInt64()
    rtt = recv_ts - val
    assert rtt >= 0
