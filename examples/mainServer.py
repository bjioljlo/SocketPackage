import sys
from pathlib import Path

_repo_root = Path(__file__).resolve().parents[1]
if str(_repo_root) not in sys.path:
    sys.path.insert(0, str(_repo_root))

from examples.SampleServerManager import SampleServerManager
from examples.SampleServerRecvMsgProtocol import SampleServerRecvMsgProtocol
from socket_package.Server import ServerSocket

if __name__ == "__main__":
    mainServer = ServerSocket()
    Sample = SampleServerManager(mainServer)
    recv = SampleServerRecvMsgProtocol(Sample)
    mainServer.Run(recv)
