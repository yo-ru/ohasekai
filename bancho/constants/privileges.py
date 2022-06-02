from __future__ import annotations

from enum import unique
from enum import IntFlag

@unique
class Privileges(IntFlag):
    # privileges intended for all normal players
    NORMAL = 1 << 0  # is an unbanned player
    VERIFIED = 1 << 1  # has logged in to the server in-game

    # supporter tier, receives some extra benefits
    SUPPORTER = 1 << 3

    # staff permissions, able to manage the server state
    TOURNAMENT = 1 << 5  # able to manage match state without host
    NOMINATOR = 1 << 6  # able to manage maps ranked status
    MODERATOR = 1 << 7  # able to manage users (level 1)
    ADMINISTRATOR = 1 << 8  # able to manage users (level 2)
    DEVELOPER = 1 << 9  # able to manage full server state

    STAFF = MODERATOR | ADMINISTRATOR | DEVELOPER

@unique
class BanchoPrivileges(IntFlag):
    PLAYER = 1 << 0
    MODERATOR = 1 << 1
    SUPPORTER = 1 << 2
    ADMINISTRATOR = 1 << 3
    DEVELOPER = 1 << 4
    TOURNAMENT = 1 << 5  # NOTE: not used in communications with osu! client