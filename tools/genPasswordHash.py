from hashlib import md5

from cmyui import log
from cmyui import Ansi
from bcrypt import hashpw
from bcrypt import gensalt

log(f"Enter Password:", Ansi.LGREEN)
passwordRaw = input().encode()

passwordMD5 = md5(passwordRaw).hexdigest().encode()
passwordBcrypt = hashpw(passwordMD5, gensalt()).decode()

log(f"NOTE: You can use this hash to manually change passwords for users by replacing their hash in the database with this newly generated one.", Ansi.LRED)
log(f"Generated Hash: {passwordBcrypt}", Ansi.LYELLOW)