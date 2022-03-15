from .player import Player


players: dict[str, Player] = {}
bcryptCache: dict[bytes, bytes] = {}