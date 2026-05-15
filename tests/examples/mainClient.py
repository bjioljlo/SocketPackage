import sys
import threading
from pathlib import Path

_repo_root = Path(__file__).resolve().parents[2]
if str(_repo_root) not in sys.path:
    sys.path.insert(0, str(_repo_root))

from socket_package.Client import ClientSocket
from tests.examples.SampleClientManager import SampleClientManager
from tests.examples.SampleClientRecvMsgProtocol import SampleClientRecvMsgProtocol

if __name__ == "__main__":
    mainClient = ClientSocket() # Init ClientSocket
    Sample = SampleClientManager(mainClient) # Create Your Any Manager use by ClientSocket
    recv = SampleClientRecvMsgProtocol(Sample)  # Your protocol file override from class TRecvProtocol
    mainClient.Run(recv)  # Run socket

    # your app function
    input_threading = threading.Thread(target=Sample.SampleSendInput)
    input_threading.start()

    # check connect and reconnect
    while not mainClient.IsShutDown:
        if not mainClient.IsConnect:
            mainClient.Run(recv)
