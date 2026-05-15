import threading

from tests.examples.SampleClientManager import SampleClientManager
from tests.examples.SampleClientRecvMsgProtocol import SampleClientRecvMsgProtocol
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
