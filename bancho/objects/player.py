from typing import Union
from typing import Optional

from ..constants.mode import Mode
from ..constants.mode import ModeData
from ..constants.action import ActionData
from ..constants.privileges import Privileges


class Player:
    def __init__(
        self,
        id: int,
        username: str,
        usernameSafe: str,
        privileges: Union[int, Privileges],
        token: str,
        passwordHash: bytes,

        mode: dict[Mode, ModeData],
        action: Optional[ActionData]
    ) -> None:
        self.id = id
        self.username = username
        self.usernameSafe = usernameSafe
        self.privileges = privileges
        self.token = token
        self.passwordHash = passwordHash

        self.mode = mode
        self.action = action

        self._buffer = bytearray()  # specific player packet buffer

    def __repr__(self) -> str:
        return f"{self.username} ({self.id})"

    def addPacket(self, packet: bytes) -> None:
        self._buffer += packet

    def sendBuffer(self) -> bytes:
        if self._buffer:
            data = bytes(self._buffer)
            self._buffer.clear()
            return data
        return b""



    