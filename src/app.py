from http import HTTPStatus
import json
import boto3
# from aws_lambda_powertools.event_handler import APIGatewayHttpResolver

# from api.helpers import initiate_auth, get_secret_hash
# from utils.config import settings


# app = APIGatewayHttpResolver()
client = boto3.client('cognito-idp')



def handler(event, context):
    # return app.resolve(event, context)

    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": "Hello World",
            "input": event,
        }),
    }

# @app.post("/signup")
# def sign_up(event, context):
#     print(event)
#     for field in ["username", "password", "email", "name"]:
#         if not event.get(field):
#             return {"error": False, "success": True, 'message': f"{field} is not present", "data": None}
#     username = event['username']
#     email = event["email"]
#     password = event['password']
#     name = event["name"]
#     try:
#         resp = client.sign_up(
#             ClientId=settings.user_pool_client_id,
#             SecretHash=get_secret_hash(username),
#             Username=username,
#             Password=password,
#             UserAttributes=[
#                 {
#                     'Name': "name",
#                     'Value': name
#                 },
#                 {
#                     'Name': "email",
#                     'Value': email
#                 }
#             ],
#             ValidationData=[
#                 {
#                     'Name': "email",
#                     'Value': email
#                 },
#                 {
#                     'Name': "custom:username",
#                     'Value': username
#                 }
#             ])
#
#     except client.exceptions.UsernameExistsException as e:
#         return {"error": False,
#                 "success": True,
#                 "message": "This username already exists",
#                 "data": None}
#     except client.exceptions.InvalidPasswordException as e:
#
#         return {"error": False,
#                 "success": True,
#                 "message": "Password should have Caps,\
#                           Special chars, Numbers",
#                 "data": None}
#     except client.exceptions.UserLambdaValidationException as e:
#         return {"error": False,
#                 "success": True,
#                 "message": "Email already exists",
#                 "data": None}
#
#     except Exception as e:
#         return {"error": False,
#                 "success": True,
#                 "message": str(e),
#                 "data": None}
#
#     return {"error": False,
#             "success": True,
#             "message": "Please confirm your signup, \
#                         check Email for validation code",
#             "data": None}
#
#
# @app.post("/confirm-signup")
# def confirm_sign_up(event, context):
#     try:
#         username = event['username']
#         password = event['password']
#         code = event['code']
#         response = client.confirm_sign_up(
#             ClientId=settings.user_pool_client_id,
#             SecretHash=get_secret_hash(username),
#             Username=username,
#             ConfirmationCode=code,
#             ForceAliasCreation=False,
#         )
#     except client.exceptions.UserNotFoundException:
#         # return {"error": True, "success": False, "message": "Username doesnt exists"}
#         return event
#     except client.exceptions.CodeMismatchException:
#         return {"error": True, "success": False, "message": "Invalid Verification code"}
#
#     except client.exceptions.NotAuthorizedException:
#         return {"error": True, "success": False, "message": "User is already confirmed"}
#
#     except Exception as e:
#         return {"error": True, "success": False, "message": f"Unknown error {e.__str__()} "}
#
#     return event
#
#
# @app.post("/resend-confirmation-code")
# def resend_confirmation_code(event, context):
#     try:
#         username = event['username']
#         response = client.resend_confirmation_code(
#             ClientId=settings.user_pool_client_id,
#             SecretHash=get_secret_hash(username),
#             Username=username,
#         )
#     except client.exceptions.UserNotFoundException:
#         return {"error": True, "success": False, "message": "Username doesnt exists"}
#
#     except client.exceptions.InvalidParameterException:
#         return {"error": True, "success": False, "message": "User is already confirmed"}
#
#     except Exception as e:
#         return {"error": True, "success": False, "message": f"Unknown error {e.__str__()} "}
#
#     return {"error": False, "success": True}
#
#
# @app.post("/reset-password")
# def reset_password(event, context):
#     try:
#         username = event['username']
#         response = client.forgot_password(
#             ClientId=settings.user_pool_client_id,
#             SecretHash=get_secret_hash(username),
#             Username=username,
#
#         )
#     except client.exceptions.UserNotFoundException:
#         return {"error": True,
#                 "data": None,
#                 "success": False,
#                 "message": "Username doesnt exists"}
#
#     except client.exceptions.InvalidParameterException:
#         return {"error": True,
#                 "success": False,
#                 "data": None,
#                 "message": f"User <{username}> is not confirmed yet"}
#
#     except client.exceptions.CodeMismatchException:
#         return {"error": True,
#                 "success": False,
#                 "data": None,
#                 "message": "Invalid Verification code"}
#
#     except client.exceptions.NotAuthorizedException:
#         return {"error": True,
#                 "success": False,
#                 "data": None,
#                 "message": "User is already confirmed"}
#
#     except Exception as e:
#         return {"error": True,
#                 "success": False,
#                 "data": None,
#                 "message": f"Uknown    error {e.__str__()} "}
#
#     return {
#         "error": False,
#         "success": True,
#         "message": f"Please check your Registered email id for validation code",
#         "data": None}
#
#
# @app.post("/confirm-reset-password")
# def confirm_reset_password(event, context):
#     try:
#         username = event['username']
#         password = event['password']
#         code = event['code']
#         client.confirm_forgot_password(
#             ClientId=settings.user_pool_client_id,
#             SecretHash=get_secret_hash(username),
#             Username=username,
#             ConfirmationCode=code,
#             Password=password,
#         )
#     except client.exceptions.UserNotFoundException as e:
#         return {"error": True,
#                 "success": False,
#                 "data": None,
#                 "message": "Username doesnt exists"}
#
#     except client.exceptions.CodeMismatchException as e:
#         return {"error": True,
#                 "success": False,
#                 "data": None,
#                 "message": "Invalid Verification code"}
#
#     except client.exceptions.NotAuthorizedException as e:
#         return {"error": True,
#                 "success": False,
#                 "data": None,
#                 "message": "User is already confirmed"}
#
#     except Exception as e:
#         return {"error": True,
#                 "success": False,
#                 "data": None,
#                 "message": f"Unknown error {e.__str__()} "}
#
#     return {"error": False,
#             "success": True,
#             "message": f"Password has been changed successfully",
#             "data": None}
#
#
# """inintiate auth flow and get login"""
# @app.post("/login")
# def sign_in(event, context):
#     for field in ["username", "password"]:
#         if event.get(field) is None:
#             return  {"error": True,
#                     "success": False,
#                     "message": f"{field} is required",
#                     "data": None}
#     username = event['username']
#     password = event['password']
#     resp, msg = initiate_auth(client, username, password)
#     if msg != None:
#       return {'message': msg,
#               "error": True, "success": False, "data": None}
#     if resp.get("AuthenticationResult"):
#       return {'message': "success",
#                "error": False,
#                "success": True,
#                "data": {
#                "id_token": resp["AuthenticationResult"]["IdToken"],
#       "refresh_token": resp["AuthenticationResult"]["RefreshToken"],
#       "access_token": resp["AuthenticationResult"]["AccessToken"],
#       "expires_in": resp["AuthenticationResult"]["ExpiresIn"],
#       "token_type": resp["AuthenticationResult"]["TokenType"]
#             }}
#     else: #this code block is relevant only when MFA is enabled
#         return {"error": True,
#            "success": False,
#            "data": None, "message": None}
#
# @app.get("/")
# def hello():
#     return {
#         "message": json.dumps({
#             "error": False,
#             "success": True,
#             "message": "Hello World"
#         })
#     }
