from __future__ import annotations
from distutils.log import Log

import struct
from abc import ABC
from typing import Iterator
from abc import abstractmethod

from bancho.objects import glob
from bancho.objects.player import Player
from bancho.constants.packets import ClientPackets

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
        # await player.buff(Writer.pong())
        pass  # nah server isn't here >:(

class Logout(BasePacket):
    def __init__(self, reader: Reader) -> None:
        reader.read_i32()

    async def handle(self, player: Player) -> None:
        player.logout()

# TODO: more packets
SUPPORTED_PACKETS = {
    ClientPackets.PING: Ping,
    ClientPackets.LOGOUT: Logout
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

        # we have a packet handler for this
        self.last_length = len
        return SUPPORTED_PACKETS.get(type)(self)

    """ read functions """
    def _read_header(self) -> tuple[ClientPackets, int]:
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

        val = self.body[:length].tobytes().decode()
        self.body = self.body[length:]
        return val