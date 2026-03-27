from SampleServerManager import SampleServerManager
from socket_package.Server import ServerSocket
from SampleServerRecvMsgProtocol import SampleServerRecvMsgProtocol

if __name__ == "__main__":
    mainServer = ServerSocket() #  Init ServerSocket
    Sample = SampleServerManager(mainServer) # Your any Manager file use ServerSocket
    recv = SampleServerRecvMsgProtocol(Sample) # Your protocol file override from class TRecvMainkind
    mainServer.Run(recv)  # Run socket
