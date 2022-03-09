from quart import Quart, render_template, websocket, request
from cmyui import log, Ansi

app = Quart(__name__)

app.config["SERVER_NAME"] = "its.moe"

# Bancho GET
@app.route("/", subdomain="c")
@app.route("/", subdomain="ce")
@app.route("/", subdomain="c4")
@app.route("/", subdomain="c5")
@app.route("/", subdomain="c6")
async def bancho_get():
    log(await request.data, Ansi.LYELLOW)
    return b"Hello World!", 200

# Bancho POST
@app.route("/", subdomain="c", methods=["POST"])
@app.route("/", subdomain="ce", methods=["POST"])
@app.route("/", subdomain="c4", methods=["POST"])
@app.route("/", subdomain="c5", methods=["POST"])
@app.route("/", subdomain="c6", methods=["POST"])
async def bancho_post():
    log(await request.body, Ansi.LBLUE)
    return b"no", 200, {"cho-token": "no"}



app.run(port=443, certfile="cert.pem", keyfile="key.pem")