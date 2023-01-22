import hmac
import hashlib
import base64

from src.functions.core.config import settings as c


def get_secret_hash(username):
    msg = username + c.up_client_id
    dig = hmac.new(str(c.up_client_secret).encode('utf-8'),
                   msg=str(msg).encode('utf-8'), digestmod=hashlib.sha256).digest()
    d2 = base64.b64encode(dig).decode()
    return d2
