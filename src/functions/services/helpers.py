import hmac
import hashlib
import base64

from ...core.config import settings as c


def get_secret_hash(username):
    msg = username + c.up_client_id
    dig = hmac.new(str(c.up_client_id).encode('utf-8'),
                   msg=str(msg).encode('utf-8'), digestmod=hashlib.sha256).digest()
    d2 = base64.b64encode(dig).decode()
    return d2


def get_base64_string(string):
    """Encode a string to base64."""
    return base64.b64encode(string.encode("utf-8")).decode("utf-8")


def get_base64_decoded_string(string):
    """Decode a base64 string."""
    return base64.b64decode(string).decode("utf-8")
