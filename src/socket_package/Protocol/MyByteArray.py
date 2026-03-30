import struct

class MyByteArray():
    '''傳輸訊息類'''
    __msg:bytearray
    __offset:int
    @property
    def Msg(self) -> bytearray:
        return self.__msg
    def __init__(self, msg: bytearray = b'') -> None:
        self.__msg = msg
        self.__offset = 0
    def WriteByte(self, input: bytes):
        self.__msg += struct.pack("s", input)
    def WriteByteArray(self, input: bytearray):
        length = len(input)
        formatStr:str = str(length) + "s"
        msg:bytearray = struct.pack("I", length)
        msg += struct.pack(formatStr, input)
        self.__msg += msg
    def WriteStr(self, input: str):
        temp_bytes = input.encode('utf-8')
        self.WriteByteArray(temp_bytes)
    def WriteInt(self, input: int):
        self.__msg += struct.pack("I", input)

    def ReadByte(self):
        output = struct.unpack_from("s", self.__msg, self.__offset)[0]
        self.__offset += struct.calcsize("s")
        return output
    def ReadStr(self) -> str:
        temp_bytes = self.ReadByteArray()
        output_str = temp_bytes.decode('utf-8')
        return output_str
    def ReadInt(self) -> int:
        output = struct.unpack_from("I", self.__msg, self.__offset)[0]
        self.__offset += struct.calcsize("I")
        return output
    def ReadByteArray(self) -> bytearray:
        output_length = struct.unpack_from("I", self.__msg, self.__offset)[0]
        self.__offset += struct.calcsize("I")
        formatStr:str = str(output_length) + "s"
        output = struct.unpack_from(formatStr, self.__msg, self.__offset)[0]
        self.__offset += struct.calcsize(formatStr)
        return output
    def Clear(self):
        self.__msg = b''
        self.__offset = 0