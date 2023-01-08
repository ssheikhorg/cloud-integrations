from time import time
from datetime import datetime

import boto3

from .models import CognitoModel
from .helpers import get_secret_hash
from ..config import settings as c
from ..database import DynamoDBCRUD


class Be3UserAdmin:
    def __init__(self):
        self.c_idp = boto3.client('cognito-idp', region_name=c.aws_default_region,
                                  aws_access_key_id=c.aws_access_key, aws_secret_access_key=c.aws_secret_key)
        self.user_pool_id = c.up_id
        self.user_pool_client_id = c.up_client_id

    def add_user_to_group(self, email, role):
        self.c_idp.admin_add_user_to_group(
            UserPoolId=self.user_pool_id,
            Username=email,
            GroupName=role
        )

    def sign_up(self, data):
        try:
            name = data['first_name'] + " " + data['last_name']
            data['password'] = data['password'].get_secret_value()
            resp = self.c_idp.sign_up(
                ClientId=self.user_pool_client_id,
                Username=data['email'],
                Password=data['password'],
                UserAttributes=[{'Name': 'name', 'Value': name},
                                {'Name': 'email', 'Value': data['email']}
                                ])

            # add user to specific group
            self.add_user_to_group(data['email'], data['role'])

            # save user in dynamo
            data["pk"] = data.pop("email")
            data['user_id'] = resp['UserSub']
            data["user_confirmed"] = resp['UserConfirmed']
            data['created_at'] = str(datetime.today().replace(microsecond=0))
            # save user in dynamo
            DynamoDBCRUD(CognitoModel).create(**data)
            return {"success": True}
        except self.c_idp.exceptions.UsernameExistsException:
            return {"success": False, "message": "User already exists"}
        except Exception as e:
            return {"success": False, "message": e.__str__()}

    def confirm_signup(self, data):
        response = self.c_idp.confirm_sign_up(
            ClientId=self.user_pool_client_id,
            Username=data["email"],
            ConfirmationCode=data["code"],
            ForceAliasCreation=False
        )
        if response['ResponseMetadata']['HTTPStatusCode'] == 200:
            user = DynamoDBCRUD(CognitoModel).get(data['email'], "cognito")
            user["user_confirmed"] = True
            # update user_confirmed in dynamo
            DynamoDBCRUD(CognitoModel).update(data["email"], "cognito", user)
            tokens = user["access_tokens"].attribute_values
            return {"success": True, "body": tokens}
        return {"success": False, "msg": "User not found"}

    def _initiate_auth(self, data):
        return self.c_idp.initiate_auth(ClientId=self.user_pool_client_id, **data)

    def sign_in(self, data):
        user = DynamoDBCRUD(CognitoModel).get(data['email'], "cognito")
        if not user:
            return {"success": False, "msg": "User not found"}
        password = data['password'].get_secret_value()
        user["access_tokens"] = user["access_tokens"].attribute_values
        if len(user["access_tokens"]) > 0:
            # check if access_token is expired
            if user["access_tokens"]["ExpiresIn"] > int(time()):
                # refresh token
                payload = dict(AuthFlow="REFRESH_TOKEN_AUTH",
                               AuthParameters={'REFRESH_TOKEN': user["access_tokens"]["RefreshToken"]})
                auth_login = self._initiate_auth(payload)
                if auth_login['ResponseMetadata']['HTTPStatusCode'] == 200:
                    auth_login['AuthenticationResult']["ExpiresIn"] = auth_login['AuthenticationResult'][
                                                                          "ExpiresIn"] + int(time())
                    # update tokens in dynamodb
                    user["access_tokens"]["AccessToken"] = auth_login['AuthenticationResult']["AccessToken"]
                    user["access_tokens"]["ExpiresIn"] = auth_login['AuthenticationResult']["ExpiresIn"]
                    DynamoDBCRUD(CognitoModel).update(data['email'], "cognito", user)
                    return {"success": True, "body": user}
                return {"success": False, "msg": "User not found"}
            return {"success": True, "body": user}
        else:
            payload = dict(AuthFlow="USER_PASSWORD_AUTH",
                           AuthParameters={"USERNAME": data['email'], "PASSWORD": password})
            auth_login = self._initiate_auth(payload)

            if auth_login['ResponseMetadata']['HTTPStatusCode'] == 200:
                auth_login['AuthenticationResult']["ExpiresIn"] = auth_login['AuthenticationResult'][
                                                                      "ExpiresIn"] + int(time())
                user["access_tokens"] = auth_login['AuthenticationResult']
                # update tokens in dynamo
                DynamoDBCRUD(CognitoModel).update(data['email'], "cognito", user)
                return {"success": True, "body": user}
            return {"success": False, "msg": "User not found"}

    def resend_confirmation_code(self, email):
        response = self.c_idp.resend_confirmation_code(
            ClientId=self.user_pool_client_id,
            Username=email
        )
        return response

    def forgot_password(self, email):
        response = self.c_idp.forgot_password(
            ClientId=self.user_pool_client_id,
            Username=email
        )
        return response

    def confirm_forgot_password(self, data):
        password = data['password'].get_secret_value()

        response = self.c_idp.confirm_forgot_password(
            ClientId=self.user_pool_client_id, Username=data['email'], ConfirmationCode=data['code'], Password=password
        )
        if response['ResponseMetadata']['HTTPStatusCode'] == 200:
            user = DynamoDBCRUD(CognitoModel).get(data['email'], "cognito")
            # update password in dynamodb
            user["password"] = password
            DynamoDBCRUD(CognitoModel).update(data['email'], "cognito", user)
            # get tokens from dynamodb
            user["access_tokens"] = user["access_tokens"].attribute_values
            return {"success": True, "body": user}
        return {"success": False, "msg": "User not found"}


class Be3UserDashboard(Be3UserAdmin):
    # remove user from cognito
    def delete_user(self, email):
        user = DynamoDBCRUD(CognitoModel).get(email, "cognito")
        if user:
            self.c_idp.admin_delete_user(
                UserPoolId=self.user_pool_id,
                Username=email
            )
            DynamoDBCRUD(CognitoModel).delete(email, "cognito")
            return {"success": True}
        return {"success": False, "msg": "User not found"}

    def get_user_info(self, access_token):
        response = self.c_idp.get_user(
            AccessToken=access_token
        )
        return response

    def sign_out(self, access_token):
        self.c_idp.global_sign_out(
            AccessToken=access_token
        )
        return {"success": True}

    def change_password(self, data):
        response = self.c_idp.change_password(
            PreviousPassword=data['old_password'].get_secret_value(),
            ProposedPassword=data['new_password'].get_secret_value(),
            AccessToken=data['access_token']
        )
        return response

    def get_user_by_email(self, email):
        user = DynamoDBCRUD(CognitoModel).get(email, "cognito")
        user["access_tokens"] = user["access_tokens"].attribute_values
        if user:
            return {"success": True, "body": user}
        return {"success": False, "msg": "User not found"}
