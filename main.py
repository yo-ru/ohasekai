from cmyui import log
from cmyui import Ansi
from quart import Quart

app = Quart(__name__)
app.config["SERVER_NAME"] = "its.moe"

# Bancho
from blueprints.bancho import bancho
for sd in ["c", "ce", "c4", "c5", "c6"]:
    app.register_blueprint(bancho, subdomain=sd)

if __name__ == "__main__":
    app.run(port=8000) # blocking call