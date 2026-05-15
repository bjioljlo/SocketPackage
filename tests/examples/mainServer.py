import sys
from pathlib import Path

_repo_root = Path(__file__).resolve().parents[2]
if str(_repo_root) not in sys.path:
    sys.path.insert(0, str(_repo_root))

from socket_package.Server import ServerSocket
from tests.examples.SampleServerManager import SampleServerManager
from tests.examples.SampleServerRecvMsgProtocol import SampleServerRecvMsgProtocol

if __name__ == "__main__":
    mainServer = ServerSocket() #  Init ServerSocket
    Sample = SampleServerManager(mainServer) # Your any Manager file use ServerSocket
    recv = SampleServerRecvMsgProtocol(Sample) # Your protocol file override from class TRecvProtocol
    mainServer.Run(recv)  # Run socket
