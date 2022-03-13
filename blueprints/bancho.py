import time
import uuid

import bcrypt
from cmyui import log
from cmyui import Ansi
from quart import request
from quart import Blueprint
from quart import current_app

from packets import Reader
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
    body = await request.data

    # not osu!
    if "User-Agent" not in headers or headers["User-Agent"] != "osu!":
        return await bancho_get()

    # client requesting login
    if "osu-token" not in headers:
        async with current_app.config["DB"].connection() as db:
            return await login(body, db)

    # TODO: client reconnecting/doing other stuff

    # DEBUG
    log("=== DEBUG ===", Ansi.LCYAN)
    #log(f"Headers: {headers}", Ansi.LYELLOW)
    log(f"Body: {body}", Ansi.LBLUE)
    log("=== DEBUG ===", Ansi.LCYAN)

    """
    TODO: handle client packets
    to complete this part of bancho we need:
            - [] a player object 
            - [] a channel object
            - [] a message object
            - [] a match object
            - [] a replay object
    
    with memoryview(body) as body:
        for packet in Reader(body):
            ...
    """
    return b"ok", 200

# bancho login
bcryptCache = {}
async def login(body, db):
    # used to calculate length of execution
    handleStartTime = time.time()

    """ begin parsing """
    # invalid request check: line breaks split
    if len(clientData := body.decode().split("\n")[:-1]) != 3:
        return b"", 200, {"cho-token": "invalid request"}

    username = clientData[0]
    passwordMD5 = clientData[1].encode()

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
    """ end parsing """

    """ start checking data """
    user = await db.fetch_one(  # try username
        "SELECT id, username, usernameSafe, "
        "privileges, passwordHash, country, "
        "silenceEnd, supporterEnd "
        "FROM users WHERE usernameSafe = :username",
        {"username": username.lower()}
    )

    # check user existance
    if not user:
        user = await db.fetch_one(  # try email
            "SELECT id, username, usernameSafe, "
            "privileges, passwordHash, country, "
            "silenceEnd, supporterEnd "
            "FROM users WHERE email = :email",
            {"email": username.lower()}
        )
        # check user existance again
        if not user:
            return Writer.userID(-1), 200, {"cho-token": "unknown user"}
    user = dict(user)

    # check user password
    passwordHash = user["passwordHash"].encode()
    if passwordHash in bcryptCache:  # password cached (fast)
        if passwordMD5 != bcryptCache[passwordHash]:
            return Writer.userID(-1), 200, {"cho-token": "incorrect password"}
    else:  # password not cached (slow)
        if not bcrypt.checkpw(passwordMD5, passwordHash): 
            return Writer.userID(-1), 200, {"cho-token": "incorrect password"}
    
        bcryptCache[passwordHash] = passwordMD5  # cache password
    """ end checking data """

    """ start writing data """
    data = bytearray(Writer.protocolVersion(19))
    data += Writer.userID(2)
    data += Writer.banchoPrivileges(BanchoPrivileges.SUPPORTER)
    data += Writer.channelInfoEnd()
    data += Writer.userPresence(
        user["id"],                   # User ID
        user["username"],             # Username
        utcOffset,                    # UTC Offset
        118,                          # Country Code
        BanchoPrivileges.SUPPORTER,   # Bancho Privileges
        Modes.MANIA,                  # Mode
        40.3399,                      # Longitude
        127.5101,                     # Latitude
        1                             # Global Rank
    )
    data += Writer.userStatistics(
        user["id"],              # User ID
        Actions.TESTING,         # Action
        "ohaeskai",              # Action Text
        "",                      # Map MD5
        Mods.NOMOD,              # Mods
        Modes.MANIA,             # Mode
        0,                       # Map ID
        0,                       # Ranked Score
        7.27,                    # Accuracy
        727,                     # Plays
        727,                     # Total Score
        1,                       # Global Rank
        727                      # PP
    )

    # calculate execution time
    handleEndTime = f"{((time.time() - handleStartTime) * 1000):.2f}ms"

    data += Writer.notification(f"ohasekai: Welcome {user['username']}!\nTook {handleEndTime}")
    """ end writing data """

    return bytes(data), 200, {"cho-token": str(uuid.uuid4())}