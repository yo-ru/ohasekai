from typing import Union
from typing import Optional
from functools import cached_property

from ..constants.mode import Mode
from ..constants.mode import ModeData
from ..constants.action import ActionData
from ..constants.privileges import Privileges
from ..constants.privileges import BanchoPrivileges


class Player:
    def __init__(
        self,
        id: int,
        username: str,
        usernameSafe: str,
        privileges: Union[int, Privileges],
        token: str,
        passwordHash: bytes,

        mode: Optional[ModeData],
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

    def buff(self, packet: bytes) -> None:
        """ add packet to buffer """
        self._buffer += packet

    def debuff(self) -> bytes:
        """ return buffer then clear buffer """
        if self._buffer:
            data = bytes(self._buffer)
            self._buffer.clear()
            return data
        return b""

    @cached_property
    def bancho_privileges(self) -> int:
        """ return privileges for bancho """
        privs = BanchoPrivileges(0)
        if self.privileges & Privileges.NORMAL:
            privs |= BanchoPrivileges.PLAYER
        if self.privileges & Privileges.SUPPORTER:
            privs |= BanchoPrivileges.SUPPORTER
        if self.privileges & Privileges.STAFF:
            privs |= BanchoPrivileges.MODERATOR
        if self.privileges & Privileges.ADMINISTRATOR:
            privs |= BanchoPrivileges.ADMINISTRATOR
        if self.privileges & Privileges.DEVELOPER:
            privs |= BanchoPrivileges.DEVELOPER
        return privs




    