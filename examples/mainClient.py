import sys
import threading
from pathlib import Path

_repo_root = Path(__file__).resolve().parents[1]
if str(_repo_root) not in sys.path:
    sys.path.insert(0, str(_repo_root))

from examples.SampleClientManager import SampleClientManager
from examples.SampleClientRecvMsgProtocol import SampleClientRecvMsgProtocol
from socket_package.Client import ClientSocket

if __name__ == "__main__":
    mainClient = ClientSocket()
    Sample = SampleClientManager(mainClient)
    recv = SampleClientRecvMsgProtocol(Sample)
    mainClient.Run(recv)

    input_threading = threading.Thread(target=Sample.SampleSendInput)
    input_threading.start()

    while not mainClient.IsShutDown:
        if not mainClient.IsConnect:
            mainClient.Run(recv)
