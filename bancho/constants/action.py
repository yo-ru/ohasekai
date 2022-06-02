from enum import unique
from enum import IntEnum
from dataclasses import dataclass

from bancho.constants.mode import Mode
from bancho.constants.mods import Mods

@unique
class Action(IntEnum):
    IDLE = 0
    AFK = 1
    PLAYING = 2
    EDITING = 3
    MODDING = 4
    MULTIPLAYER = 5
    WATCHING = 6
    UNKNOWN = 7
    TESTING = 8
    SUBMITTING = 9
    PAUSED = 10
    LOBBY = 11
    MULTIPLAYING = 12
    OSUDIRECT = 13

@dataclass
class ActionData:
    action: Action = Action.IDLE
    text: str = ""
    mapMD5: str = ""
    mods: Mods = Mods.NOMOD
    mode: Mode = Mode.OSU
    mapID: int = 0