import struct
from typing import Any
from typing import Union
from typing import Callable
from typing import Collection

from .constants.packets import ClientPackets
from .constants.packets import ServerPackets

class Reader:
    def __init__(self, body: memoryview) -> None:
        self.body = body

    # TODO: iteration >:c

""" read functions """
# TODO: read functions

class Writer:
    def __init__(self) -> None:
        ...

    def userID(resp: int) -> bytes:
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

def write_message(sender: str, msg: str, recipient: str, sender_id: int) -> bytearray:
    ret = bytearray(write_string(sender))
    ret += write_string(msg)
    ret += write_string(recipient)
    ret += sender_id.to_bytes(4, "little", signed=True)
    return ret

def write_channel(name: str, topic: str, count: int) -> bytearray:
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