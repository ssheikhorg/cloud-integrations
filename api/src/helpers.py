import hmac
import hashlib
import base64
from config import settings


def get_secret_hash(username):
    msg = username + settings.user_pool_client_id
    dig = hmac.new(str(settings.user_pool_client_secret).encode('utf-8'),
        msg = str(msg).encode('utf-8'), digestmod=hashlib.sha256).digest()
    d2 = base64.b64encode(dig).decode()
    return d2


def initiate_auth(client, username, password):
    secret_hash = get_secret_hash(username)
    try:
        resp = client.admin_initiate_auth(
                 UserPoolId=settings.user_pool_id,
                 ClientId=settings.user_pool_client_id,
                 AuthFlow='ADMIN_NO_SRP_AUTH',
                 AuthParameters={
                     'USERNAME': username,
                     'SECRET_HASH': secret_hash,
                     'PASSWORD': password,
                  },
                ClientMetadata={
                  'username': username,
                  'password': password,
              })
    except client.exceptions.NotAuthorizedException:
        return None, "The username or password is incorrect"
    except client.exceptions.UserNotConfirmedException:
        return None, "User is not confirmed"
    except Exception as e:
        return None, e.__str__()
    return resp, None
