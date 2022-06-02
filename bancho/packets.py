import struct
from abc import ABC
from typing import Any
from typing import Union
from typing import Callable
from typing import Iterator
from typing import Collection
from abc import abstractmethod
from __future__ import annotations

from bancho.objects.player import Player
from .constants.packets import ClientPackets
from .constants.packets import ServerPackets

""" 
modified bancho.py reader
thx cm <3
"""
class BasePacket(ABC):
    def __init__(self, reader: Reader) -> None:
        ...

    @abstractmethod
    async def handle(self, player: Player) -> None:
        ...

class Ping(BasePacket):
    async def handle(self, player: Player) -> None:
        # await p.buff(Writer.pong())
        pass  # nah server isn't here >:(

# TODO: more packets
SUPPORTED_PACKETS = {
    ClientPackets.PING: Ping
}

class Reader:
    def __init__(self, body: memoryview) -> None:
        self.body = body
        self.last_length = 0

    def __iter__(self) -> Iterator[BasePacket]:
        return self

    def __next__(self) -> BasePacket:
        while self.body:
            type, len = self._read_header()

            # ignore unsupported packets
            if type not in SUPPORTED_PACKETS:
                if len != 0:
                    self.body = self.body[len:]
            else:
                # packet supported, read
                break
        else:
            raise StopIteration

        # we have a packet handler for this.
        self.last_length = len
        return SUPPORTED_PACKETS.get(type)(self)

    """ read functions """
    # TODO: read functions
    def _read_header(self) -> tuple[ClientPackets, int]:
        """Read the header of an osu! packet (id & length)."""
        data = struct.unpack("<HxI", self.body[:7])
        self.body = self.body[7:]
        return ClientPackets(data[0]), data[1]

    def read_raw(self) -> memoryview:
        val = self.body[: self.last_length]
        self.body = self.body[self.last_length :]
        return val
    
    def read_i8(self) -> int:
        val = self.body[0]
        self.body = self.body[1:]
        return val - 256 if val > 127 else val

    def read_u8(self) -> int:
        val = self.body[0]
        self.body = self.body[1:]
        return val

    def read_i16(self) -> int:
        val = int.from_bytes(self.body[:2], "little", signed=True)
        self.body = self.body[2:]
        return val

    def read_u16(self) -> int:
        val = int.from_bytes(self.body[:2], "little", signed=False)
        self.body = self.body[2:]
        return val

    def read_i32(self) -> int:
        val = int.from_bytes(self.body[:4], "little", signed=True)
        self.body = self.body[4:]
        return val

    def read_u32(self) -> int:
        val = int.from_bytes(self.body[:4], "little", signed=False)
        self.body = self.body[4:]
        return val

    def read_i64(self) -> int:
        val = int.from_bytes(self.body[:8], "little", signed=True)
        self.body = self.body[8:]
        return val

    def read_u64(self) -> int:
        val = int.from_bytes(self.body[:8], "little", signed=False)
        self.body = self.body[8:]
        return val

    def read_f16(self) -> float:
        (val,) = struct.unpack_from("<e", self.body[:2])
        self.body = self.body[2:]
        return val

    def read_f32(self) -> float:
        (val,) = struct.unpack_from("<f", self.body[:4])
        self.body = self.body[4:]
        return val

    def read_f64(self) -> float:
        (val,) = struct.unpack_from("<d", self.body[:8])
        self.body = self.body[8:]
        return val

    def read_i32_list_i16l(self) -> tuple[int]:
        length = int.from_bytes(self.body[:2], "little")
        self.body = self.body[2:]

        val = struct.unpack(f'<{"I" * length}', self.body[: length * 4])
        self.body = self.body[length * 4 :]
        return val

    def read_i32_list_i32l(self) -> tuple[int]:
        length = int.from_bytes(self.body[:4], "little")
        self.body = self.body[4:]

        val = struct.unpack(f'<{"I" * length}', self.body[: length * 4])
        self.body = self.body[length * 4 :]
        return val

    def read_string(self) -> str:
        exists = self.body[0] == 0x0B
        self.body = self.body[1:]

        if not exists:
            return ""

        length = shift = 0

        while True:
            byte = self.body[0]
            self.body = self.body[1:]

            length |= (byte & 0x7F) << shift
            if (byte & 0x80) == 0:
                break

            shift += 7

        val = self.body[:length].tobytes().decode()  # copy
        self.body = self.body[length:]
        return val

class Writer:
    def __init__(self) -> None:
        ...

    def userID(resp: int) -> bytes:
        """
        resp:
        -1: authentication failed
        -2: old client
        -3: banned
        -4: banned
        -5: error occurred
        -6: needs supporter
        -7: password reset
        -8: requires verification
        ??: valid id
        """
        return write(ServerPackets.USER_ID, (resp, write_i32))

    def notification(message: str) -> bytes:
        return write(ServerPackets.NOTIFICATION, (message, write_string))

    def protocolVersion(version: int) -> bytes:
        return write(ServerPackets.PROTOCOL_VERSION, (version, write_i32))

    def banchoPrivileges(privileges: int) -> bytes:
        return write(ServerPackets.PRIVILEGES, (privileges, write_i32))

    def silenceEnd(delta: int) -> bytes:
        return write(ServerPackets.SILENCE_END, (delta, write_i32))

    def userPresence(
        userID: int,
        userName: str,
        utcOffset: int,
        countryCode: int,
        banchoPrivleges: int,
        mode: int,
        latitude: int,
        longitude: int,
        globalRank: int
    ) -> bytes:
        return write(
            ServerPackets.USER_PRESENCE, 
            (userID, write_i32),
            (userName, write_string),
            (utcOffset + 24, write_u8),
            (countryCode, write_u8),
            (banchoPrivleges | (mode << 5), write_u8),
            (longitude, write_f32),
            (latitude, write_f32),
            (globalRank, write_i32)
        )
    
    def userStatistics(
        userID: int,
        action: int,
        actionText: str,
        mapMD5: str,
        mods: int,
        mode: int,
        mapID: int,
        rankedScore: int,
        accuracy: float,
        plays: int,
        totalScore: int,
        globalRank: int,
        pp: int
    ) -> bytes:
        return write(
            ServerPackets.USER_STATS,
            (userID, write_i32),
            (action, write_u8),
            (actionText, write_string),
            (mapMD5, write_string),
            (mods, write_i32),
            (mode, write_u8),
            (mapID, write_i32),
            (rankedScore, write_i64),
            (accuracy / 100.0, write_f32),
            (plays, write_i32),
            (totalScore, write_i64),
            (globalRank, write_i32),
            (pp, write_i16)
        )

    def channelInfoEnd() -> bytes:
        return write(ServerPackets.CHANNEL_INFO_END)

    def restartServer(ms: int) -> bytes:
        return write(ServerPackets.RESTART, (ms, write_i32))

    def sendMessage(fro: str, msg: str, to: str, froID: int) -> bytes:
        return write(ServerPackets.SEND_MESSAGE, ((fro, msg, to, froID), write_message))

    def pong() -> bytes:
        return write(ServerPackets.PONG)

""" write functions """
def write(packetID: int, *args: tuple[Any, Callable]) -> bytes:
    packet = bytearray(struct.pack("<Hx", packetID))

    for packetArgs, packetType in args:
        packet += packetType(packetArgs)

    packet[3:3] = struct.pack("<I", len(packet) - 3)
    return bytes(packet)

def write_uleb128(num: int) -> Union[bytes, bytearray]:
    if num == 0:
        return b"\x00"

    ret = bytearray()

    while num != 0:
        ret.append(num & 0x7F)
        num >>= 7
        if num != 0:
            ret[-1] |= 0x80

    return ret

def write_string(string: str) -> bytes:
    if string:
        encoded = string.encode()
        ret = b"\x0b" + write_uleb128(len(encoded)) + encoded
    else:
        ret = b"\x00"

    return ret

def write_i32_list(list: Collection[int]) -> bytearray:
    ret = bytearray(len(list).to_bytes(2, "little"))

    for i in list:
        ret += i.to_bytes(4, "little")

    return ret

def write_message(*args: tuple[str, str, str, int]) -> bytearray:
    for fro, msg, to, froID in args:
        ret = bytearray(write_string(fro))
        ret += write_string(msg)
        ret += write_string(to)
        ret += froID.to_bytes(4, "little", signed=True)
        return ret

def write_channel(*args: tuple[str, str, int]) -> bytearray:
    for name, topic, count in args:
        ret = bytearray(write_string(name))
        ret += write_string(topic)
        ret += count.to_bytes(2, "little")
        return ret

def write_i8(num: int) -> bytes:
    return struct.pack("<b", num)

def write_u8(num: int) -> bytes:
    return struct.pack("<B", num)

def write_i16(num: int) -> bytes:
    return struct.pack("<h", num)

def write_u16(num: int) -> bytes:
    return struct.pack("<H", num)

def write_i32(num: int) -> bytes:
    return struct.pack("<i", num)

def write_u32(num: int) -> bytes:
    return struct.pack("<I", num)

def write_f16(num: float) -> bytes:
    return struct.pack("<e", num)

def write_f32(num: float) -> bytes:
    return struct.pack("<f", num)

def write_i64(num: int) -> bytes:
    return struct.pack("<q", num)

def write_u64(num: int) -> bytes:
    return struct.pack("<Q", num)

def write_f64(num: float) -> bytes:
    return struct.pack("<d", num)