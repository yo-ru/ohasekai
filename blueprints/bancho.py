import uuid
import struct

from cmyui import log
from cmyui import Ansi
from quart import request
from quart import Blueprint
from quart import current_app

from packets import Writer
from constants.mods import Mods
from constants.modes import Modes
from constants.actions import Actions
from constants.privileges import BanchoPrivileges

bancho = Blueprint('bancho', __name__)

# bancho GET
@bancho.route("/")
async def bancho_get():
    log(await request.data, Ansi.LYELLOW)
    return b"Hello World!", 200

# bancho POST
@bancho.route("/", methods=["POST"])
async def bancho_post():
    headers = request.headers

    if "User-Agent" not in headers or headers["User-Agent"] != "osu!":
        return

    # client requesting login
    if "osu-token" not in headers:
        body = await request.data

        """ begin parsing through login request """

        # invalid request check: line breaks split
        if len(clientData := body.decode().split("\n")[:-1]) != 3:
            return b"", 200, {"cho-token": "invalid request"}

        username = clientData[0]
        passwordMD5 = clientData[1]

        # invalid request check: third line split
        if len(clientInfo := clientData[2].split("|")) != 5:
            return b"", 200, {"cho-token": "invalid request"}

        # TODO: osu! version check
        osuVersion = clientInfo[0]

        # invalid request check: ensure utcOffset is a decimal
        if not clientInfo[1].replace("-", "").isdecimal():
            return b"", 200, {"cho-token": "invalid request"}
        utcOffset = int(clientInfo[1])

        # display city
        displayCity = clientInfo[2] == '1'

        # invalid request check: client hashes split
        if len(clientHashes := clientInfo[3][:-1].split(":")) != 5:
            return b"", 200, {"cho-token", "invalid request"}

        """
        osuPathMD5: 0
        adaptersStr: 1
        adaptersMD5: 2
        uninstallMD5: 3
        diskSignatureMD5: 4
        """     
        adapters = [a for a in clientHashes[1][:-1].split(".") if a]
        runningWine = clientHashes[1] == "runningunderwine"

        if not (adapters or runningWine):
            return b"", 200, {"cho-token", "invalid request"}

        # private PMs
        privatePMs = int(clientInfo[4]) == 1 

        """ end parsing, begin checking data """

        async with current_app.config["DB"].connection() as db:
            ...

        if username not in ["peppy", "Yoru"]:
            return Writer.userID(-1), 200, {"cho-token": "no"}

        data = bytearray(Writer.protocolVersion(19))
        data += Writer.userID(2)
        data += Writer.banchoPrivileges(BanchoPrivileges.SUPPORTER)
        data += Writer.channelInfoEnd()
        data += Writer.userPresence(
            2,                            # User ID
            username,                     # Username
            utcOffset,                    # UTC Offset
            0,                            # Country Code
            BanchoPrivileges.SUPPORTER,   # Bancho Privileges
            Modes.MANIA,                  # Mode
            0.0,                          # Longitude
            0.0,                          # Latitude
            1                             # Global Rank
        )
        data += Writer.userStatistics(
            2,                       # User ID
            Actions.SUBMITTING,      # Action
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
        data += Writer.notification(f"ohasekai: Welcome {username}!")
        return bytes(data), 200, {"cho-token": str(uuid.uuid4())}
    
    # TODO: client reconnecting/doing other stuff
    return