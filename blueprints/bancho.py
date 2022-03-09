import struct

from cmyui import log
from cmyui import Ansi
from quart import request
from quart import Blueprint

from packets import Writer
from constants.mods import Mods
from constants.modes import Modes
from constants.actions import Actions
from constants.privileges import BanchoPrivileges, Privileges

bancho = Blueprint('bancho', __name__)

# Bancho GET
@bancho.route("/")
async def bancho_get():
    log(await request.data, Ansi.LYELLOW)
    return b"Hello World!", 200

# Bancho POST
@bancho.route("/", methods=["POST"])
async def bancho_post():
    headers = request.headers

    if "User-Agent" not in headers or headers["User-Agent"] != "osu!":
        return

    # client asking for login
    if "osu-token" not in headers:
        body = await request.data

        clientData = body.decode().split("\n")[:-1]
        username = clientData[0]
        passwordMD5 = clientData[1]

        if username not in ["peppy", "Yoru"]:
            return Writer.userID(-1), 200, {"cho-token": "no"}

        data = bytearray(Writer.protocolVersion(19))
        data += Writer.userID(2)
        data += Writer.banchoPrivileges(BanchoPrivileges.SUPPORTER)
        data += Writer.channelInfoEnd()
        data += Writer.userPresence(
            2,                            # User ID
            username,                     # Username
            0,                            # UTC Offset
            0,                            # Country Code
            BanchoPrivileges.SUPPORTER,   # Bancho Privileges (Supporter)
            Modes.MANIA,                  # Mode
            0.0,                          # Longitude
            0.0,                          # Latitude
            1                             # Global Rank
        )
        data += Writer.userStatistics(
            2,                       # User ID
            Actions.Submitting,      # Action
            "themselves to Satan.",  # Action Text
            "",                      # Map MD5
            Mods.NOMOD,              # Mods
            Modes.MANIA,             # Mode
            0,                       # Map ID
            0,                       # Ranked Score
            100.0,                   # Accuracy
            0,                       # Plays
            0,                       # Total Score
            1,                       # Global Rank
            727                      # PP
        )
        data += Writer.notification(f"{username}, I'm questioning my will to live.")
        return bytes(data), 200, {"cho-token": "smack-my-ass"}
    
    # TODO: other stuff
    return b""