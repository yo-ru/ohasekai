import time
import uuid

import bcrypt
from cmyui import log
from cmyui import Ansi
from quart import request
from quart import Blueprint
from quart import current_app

from bancho.constants.action import ActionData

from .objects import glob
from .packets import Reader
from .packets import Writer
from .constants.mode import Mode
from .objects.player import Player
from .constants.mode import ModeData
from .constants.action import ActionData
from .constants.privileges import BanchoPrivileges

bancho = Blueprint('bancho', __name__)

# bancho GET
@bancho.route("/")
async def bancho_get():
    return b"ohasekai<br>yoru's bancho attempt.", 200

# bancho POST
@bancho.route("/", methods=["POST"])
async def bancho_post():
    headers = request.headers
    osuToken = headers.get("osu-token")
    body = await request.data

    # not osu!
    if "User-Agent" not in headers or headers["User-Agent"] != "osu!":
        return await bancho_get()

    # client requesting login
    if not osuToken:
        async with current_app.config["DB"].connection() as db:
            return await login(body, db)

    # get player object from osu-token
    player = glob.players.get(osuToken)

    # server most likely restarted
    if not player:
        return Writer.restartServer(0) + Writer.notification(f"{current_app.config['SERVER_NAME']}: server restarted!"), 200

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
    
    return player.debuff(), 200

# bancho login
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
    bcryptCache = glob.bcryptCache
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
    playerMode = ModeData(
        mode = Mode.OSU,
        globalRank = 1,
        pp = 727,
        totalScore = 727,
        rankedScore = 727,
        accuracy = 7.27,
        plays = 727
    )

    player = Player(
        id = user["id"],
        username = user["username"],
        usernameSafe = user["usernameSafe"],
        privileges = user["privileges"],
        token = str(uuid.uuid4()),
        passwordHash = user["passwordHash"],

        mode = dict[Mode.OSU, playerMode],
        action = ActionData
    )

    data = bytearray(Writer.protocolVersion(19))
    data += Writer.userID(player.id)
    data += Writer.banchoPrivileges(BanchoPrivileges.SUPPORTER)
    data += Writer.channelInfoEnd()

    userPresence = Writer.userPresence(
        player.id,                    # User ID
        player.username,              # Username
        utcOffset,                    # UTC Offset
        118,                          # Country Code
        BanchoPrivileges.SUPPORTER,   # Bancho Privileges
        player.action.mode,           # Mode
        40.3399,                      # Longitude
        127.5101,                     # Latitude
        playerMode.globalRank         # Global Rank
    )
    userStatistics = Writer.userStatistics(
        player.id,               # User ID
        player.action.action,    # Action
        player.action.text,      # Action Text
        player.action.mapMD5,    # Map MD5
        player.action.mods,      # Mods
        player.action.mode,      # Mode
        player.action.mapID,     # Map ID
        playerMode.mode,         # Ranked Score
        playerMode.accuracy,     # Accuracy
        playerMode.plays,        # Plays
        playerMode.totalScore,   # Total Score
        playerMode.globalRank,   # Global Rank
        playerMode.pp            # PP
    )

    userData = userPresence + userStatistics
    data += userData

    # send userPresence and userStatistics to all online players
    for t, p in glob.players.items():
        p.buff(userData)

    # calculate execution time
    handleEndTime = (time.time() - handleStartTime) * 1000

    data += Writer.notification(f"{current_app.config['SERVER_NAME']}: Welcome {player.username}!\nTook {handleEndTime:.2f}ms")
    """ end writing data """

    # append player to players dict
    glob.players[player.token] = player

    # user officially logged in
    return bytes(data), 200, {"cho-token": player.token}