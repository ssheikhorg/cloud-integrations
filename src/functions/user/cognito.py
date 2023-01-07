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
            # update user_confirmed in dynamo
            u_set = {"user_confirmed": True}
            DynamoDBCRUD(CognitoModel).update(data["email"], "cognito", u_set)
            return {"success": True}
        return {"success": False, "msg": "User not found"}

    def sign_in(self, data):
        user = DynamoDBCRUD(CognitoModel).get(data['email'], "cognito")
        passwd = data['password'].get_secret_value()
        tokens = user["access_tokens"].attribute_values
        if len(tokens) > 0:
            # check if access_token is expired
            if tokens["ExpiresIn"] < int(time()):
                # refresh token
                response = self.c_idp.initiate_auth(
                    ClientId=self.user_pool_client_id,
                    AuthFlow='REFRESH_TOKEN_AUTH',
                    AuthParameters={'REFRESH_TOKEN': tokens["RefreshToken"]})
            else:
                response = tokens
            return {"success": True, "body": response}
        else:
            login = self.c_idp.initiate_auth(
                AuthFlow='USER_PASSWORD_AUTH',
                AuthParameters={"USERNAME": data['email'], "PASSWORD": passwd,
                                # "SECRET_HASH": get_secret_hash(data['email'])
                                },
                ClientId=self.user_pool_client_id
            )
            if login['ResponseMetadata']['HTTPStatusCode'] == 200:
                login['AuthenticationResult']["ExpiresIn"] = login['AuthenticationResult']["ExpiresIn"] + int(time())
                u_set = {"access_tokens": login['AuthenticationResult']}
                # update tokens in dynamo
                DynamoDBCRUD(CognitoModel).update(data['email'], "cognito", u_set)
                return {"success": True, "body": login['AuthenticationResult']}
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
        response = self.c_idp.confirm_forgot_password(
            ClientId=self.user_pool_client_id,
            Username=data['email'],
            ConfirmationCode=data['code'],
            Password=data['password'].get_secret_value()
        )
        return response


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
        if user:
            return {"success": True, "body": user}
        return {"success": False, "msg": "User not found"}
