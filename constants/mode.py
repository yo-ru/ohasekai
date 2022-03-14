from __future__ import annotations

from enum import unique
from enum import IntEnum


GAMEMODE_REPR_LIST = (
    "osu!",
    "osu!taiko",
    "osu!catch",
    "osu!mania"
)


@unique
class Mode(IntEnum):
    OSU = 0
    TAIKO = 1
    CATCH = 2
    MANIA = 3

    def __repr__(self) -> str:
        return GAMEMODE_REPR_LIST[self.value]