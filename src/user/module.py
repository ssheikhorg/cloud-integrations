import traceback
from http import HTTPStatus
import json
import boto3

from .helpers import initiate_auth, get_secret_hash
from utils.config import settings

client = boto3.client('cognito-idp')


def cognito_signup(event, context):
    print(event)
    for field in ["username", "password", "email", "name"]:
        if not event.get(field):
            return {"error": False, "success": True, 'message': f"{field} is not present", "data": None}
    username = event['username']
    email = event["email"]
    password = event['password']
    name = event["name"]
    try:
        resp = client.cognito_signup(
            ClientId=settings.user_pool_client_id,
            SecretHash=get_secret_hash(username),
            Username=username,
            Password=password,
            UserAttributes=[
                {
                    'Name': "name",
                    'Value': name
                },
                {
                    'Name': "email",
                    'Value': email
                }
            ],
            ValidationData=[
                {
                    'Name': "email",
                    'Value': email
                },
                {
                    'Name': "custom:username",
                    'Value': username
                }
            ])

    except client.exceptions.UsernameExistsException as e:
        return {"error": False,
                "success": True,
                "message": "This username already exists",
                "data": None}
    except client.exceptions.InvalidPasswordException as e:

        return {"error": False,
                "success": True,
                "message": "Password should have Caps,\
                          Special chars, Numbers",
                "data": None}
    except client.exceptions.UserLambdaValidationException as e:
        return {"error": False,
                "success": True,
                "message": "Email already exists",
                "data": None}

    except Exception as e:
        return {"error": False,
                "success": True,
                "message": str(e),
                "data": None}

    return {"error": False,
            "success": True,
            "message": "Please confirm your signup, \
                        check Email for validation code",
            "data": None}


def cognito_confirm_signup(event, context):
    try:
        username = event['username']
        password = event['password']
        code = event['code']
        response = client.cognito_confirm_signup(
            ClientId=settings.user_pool_client_id,
            SecretHash=get_secret_hash(username),
            Username=username,
            ConfirmationCode=code,
            ForceAliasCreation=False,
        )
    except client.exceptions.UserNotFoundException:
        # return {"error": True, "success": False, "message": "Username doesnt exists"}
        return event
    except client.exceptions.CodeMismatchException:
        return {"error": True, "success": False, "message": "Invalid Verification code"}

    except client.exceptions.NotAuthorizedException:
        return {"error": True, "success": False, "message": "User is already confirmed"}

    except Exception as e:
        return {"error": True, "success": False, "message": f"Unknown error {e.__str__()} "}

    return event


def cognito_resend_confirmation_code(event, context):
    try:
        username = event['username']
        response = client.resend_confirmation_code(
            ClientId=settings.user_pool_client_id,
            SecretHash=get_secret_hash(username),
            Username=username
        )
    except client.exceptions.UserNotFoundException:
        return {"error": True, "success": False, "message": "User not found"}
    except Exception as e:
        return {"error": True, "success": False, "message": f"Unknown error {e.__str__()} "}
    return {"error": False, "success": True, "message": "success"}


def cognito_sign_in(event, context):
    for field in ["username", "password"]:
        if event.get(field) is None:
            return {"error": True,
                    "success": False,
                    "message": f"{field} is required",
                    "data": None}
    username = event['username']
    password = event['password']
    resp, msg = initiate_auth(client, username, password)
    if msg != None:
        return {'message': msg,
                "error": True, "success": False, "data": None}
    if resp.get("AuthenticationResult"):
        return {'message': "success",
                "error": False,
                "success": True,
                "data": {
                    "id_token": resp["AuthenticationResult"]["IdToken"],
                    "refresh_token": resp["AuthenticationResult"]["RefreshToken"],
                    "access_token": resp["AuthenticationResult"]["AccessToken"],
                    "expires_in": resp["AuthenticationResult"]["ExpiresIn"],
                    "token_type": resp["AuthenticationResult"]["TokenType"]
                }}
    else:  # this code block is relevant only when MFA is enabled
        return {"error": True,
                "success": False,
                "data": None, "message": None}


def cognito_admin_sign_in(event, context):
    try:
        username = event['username']
        password = event['password']
        response = client.admin_initiate_auth(
            UserPoolId=settings.user_pool_id,
            ClientId=settings.user_pool_client_id,
            AuthFlow='ADMIN_NO_SRP_AUTH',
            AuthParameters={
                'USERNAME': username,
                'PASSWORD': password
            }
        )
    except client.exceptions.NotAuthorizedException:
        return {"error": True, "success": False, "message": "Incorrect username or password"}
    except client.exceptions.UserNotFoundException:
        return {"error": True, "success": False, "message": "User not found"}
    except Exception as e:
        return {"error": True, "success": False, "message": f"Unknown error {e.__str__()} "}
    return {"error": False, "success": True, "message": "success", "data": response}


def cognito_forgot_password(event, context):
    try:
        username = event['username']
        response = client.forgot_password(
            ClientId=settings.user_pool_client_id,
            SecretHash=get_secret_hash(username),
            Username=username
        )
    except client.exceptions.UserNotFoundException:
        return {"error": True, "success": False, "message": "User not found"}
    except Exception as e:
        return {"error": True, "success": False, "message": f"Unknown error {e.__str__()} "}
    return {"error": False, "success": True, "message": "success"}


def cognito_confirm_forgot_password(event, context):
    try:
        username = event['username']
        password = event['password']
        code = event['code']
        response = client.confirm_forgot_password(
            ClientId=settings.user_pool_client_id,
            SecretHash=get_secret_hash(username),
            Username=username,
            ConfirmationCode=code,
            Password=password
        )
    except client.exceptions.UserNotFoundException:
        return {"error": True, "success": False, "message": "User not found"}
    except client.exceptions.CodeMismatchException:
        return {"error": True, "success": False, "message": "Invalid Verification code"}
    except Exception as e:
        return {"error": True, "success": False, "message": f"Unknown error {e.__str__()} "}
    return {"error": False, "success": True, "message": "success"}


"""COGNITO USER POOL TRIGGERS WITH AUTHORIZER"""


def cognito_get_user(event, context):
    try:
        access_token = event['access_token']
        response = client.get_user(
            AccessToken=access_token
        )
    except client.exceptions.NotAuthorizedException:
        return {"error": True, "success": False, "message": "Not Authorized"}
    except Exception as e:
        return {"error": True, "success": False, "message": f"Unknown error {e.__str__()} "}
    return {"error": False, "success": True, "message": "success", "data": response}


def cognito_change_password(event, context):
    try:
        access_token = event['access_token']
        previous_password = event['previous_password']
        proposed_password = event['proposed_password']
        response = client.change_password(
            AccessToken=access_token,
            PreviousPassword=previous_password,
            ProposedPassword=proposed_password
        )
    except client.exceptions.NotAuthorizedException:
        return {"error": True, "success": False, "message": "Not Authorized"}
    except client.exceptions.InvalidPasswordException:
        return {"error": True, "success": False, "message": "Invalid Password"}
    except Exception as e:
        return {"error": True, "success": False, "message": f"Unknown error {e.__str__()} "}
    return {"error": False, "success": True, "message": "Password changed successfully"}


def cognito_sign_out(event, context):
    try:
        access_token = event['access_token']
        response = client.global_sign_out(
            AccessToken=access_token
        )
    except client.exceptions.NotAuthorizedException:
        return {"error": True, "success": False, "message": "Not Authorized"}
    except Exception as e:
        return {"error": True, "success": False, "message": f"Unknown error {e.__str__()} "}
    return {"error": False, "success": True, "message": "success"}


def cognito_delete_user(event, context):
    try:
        access_token = event['access_token']
        response = client.delete_user(
            AccessToken=access_token
        )
    except client.exceptions.NotAuthorizedException:
        return {"error": True, "success": False, "message": "Not Authorized"}
    except Exception as e:
        return {"error": True, "success": False, "message": f"Unknown error {e.__str__()} "}
    return {"error": False, "success": True, "message": "success"}
