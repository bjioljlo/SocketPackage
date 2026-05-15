from tests.examples.SampleServerManager import SampleServerManager
from tests.examples.SampleServerRecvMsgProtocol import SampleServerRecvMsgProtocol
from socket_package.Server import ServerSocket

if __name__ == "__main__":
    mainServer = ServerSocket()
    Sample = SampleServerManager(mainServer)
    recv = SampleServerRecvMsgProtocol(Sample)
    mainServer.Run(recv)
