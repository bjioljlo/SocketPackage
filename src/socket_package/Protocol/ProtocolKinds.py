from enum import IntEnum


PROTOCOL_VERSION = 1


class MainKind(IntEnum):
    """Reserved core kinds owned by the package."""

    CONTROL = 0


class SubKind(IntEnum):
    """Reserved core sub-kinds under MainKind.CONTROL."""

    STOP = 0
    HEARTBEAT = 1
