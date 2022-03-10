import aiohttp

import pymysql
import databases
from cmyui import log
from cmyui import Ansi
from quart import Quart
from environs import Env

# get environment variables
env = Env()
env.read_env()

# quart
app = Quart(__name__)
app.config["SERVER_NAME"] = env.str("SERVER_NAME")
app.config["SECRET_KEY"]  = env.str("SECRET_KEY")

# tasks ran at start up (before we serve)
@app.before_serving
async def on_start() -> None:
    log("=== ohasekai ===", Ansi.LCYAN)

    # prepare mysql for connections
    app.config["DB"] = databases.Database(env.str("DB_DSN"))
    try:
        await app.config["DB"].connect()
    except pymysql.err.OperationalError:
        log("Failed to connect to MySQL!", Ansi.LRED),
        exit(1)
    except:
        log("Fatal error occured when connecting to MySQL!", Ansi.LRED)
        exit(1)
    log("MySQL prepared...", Ansi.LYELLOW)

    # prepare client session
    app.config["HTTP"] = aiohttp.ClientSession
    log("HTTP prepared...", Ansi.LYELLOW)

    log("Done!", Ansi.LGREEN)
    log("================", Ansi.LCYAN)

# bancho
from blueprints.bancho import bancho
for sd in ["c", "ce", "c4"]:
    app.register_blueprint(bancho, subdomain=sd)

if __name__ == "__main__":
    app.run(port=8000) # blocking call