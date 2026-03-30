from SampleClientManager import SampleClientManager
from socket_package.Client import ClientSocket
from SampleClientRecvMsgProtocol import SampleClientRecvMsgProtocol
import threading

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