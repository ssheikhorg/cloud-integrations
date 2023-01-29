from time import time
from datetime import datetime

import boto3

from ..models.users import UserModel
from ..core.config import settings as c
from ..core.database import DynamoDB
from ..utils.response import Response as Rs

db = DynamoDB(UserModel)


class Be3UserAdmin:
    def __init__(self):
        self.c_idp = boto3.client("cognito-idp", region_name=c.aws_default_region,
                                  aws_access_key_id=c.aws_access_key, aws_secret_access_key=c.aws_secret_key)
        self.user_pool_id = c.up_id
        self.user_pool_client_id = c.up_client_id

    async def add_user_to_group(self, email, role):
        self.c_idp.admin_add_user_to_group(
            UserPoolId=self.user_pool_id,
            Username=email,
            GroupName=role
        )

    async def sign_up(self, body):
        try:
            _username = await db.count(pk=body["username"], index_name="username_index")
            if _username > 0:
                return Rs.confict(msg="Username already exists")

            body["password"] = body["password"].get_secret_value()
            name = body["first_name"] + " " + body["last_name"]
            resp = self.c_idp.sign_up(
                ClientId=self.user_pool_client_id,
                Username=body["email"],
                Password=body["password"],
                UserAttributes=[{"Name": "name", "Value": name},
                                {"Name": "email", "Value": body["email"]}])

            # add user to specific group
            await self.add_user_to_group(body["email"], body["role"])

            # save user in dynamo
            body["pk"] = resp["UserSub"]
            body["user_confirmed"] = resp["UserConfirmed"]
            body["created_at"] = str(datetime.today().replace(microsecond=0))

            # save user in dynamo
            await db.create(**body)
            return Rs.created(msg="User created successfully")
        except Exception as e:
            return Rs.server_error(e.__str__())

    async def confirm_signup(self, body):
        try:
            response = self.c_idp.confirm_sign_up(
                ClientId=self.user_pool_client_id,
                Username=body["email"],
                ConfirmationCode=body["code"],
                ForceAliasCreation=False
            )
            if response["ResponseMetadata"]["HTTPStatusCode"] == 200:
                # get user from dynamo with email index
                user = await db.query(pk=body["email"], index_name="email_index")
                user[0]["user_confirmed"] = True
                await db.update(user[0])
                return Rs.success(msg="User confirmed")
            return Rs.error(msg="User not confirmed")
        except Exception as e:
            return Rs.server_error(e.__str__())

    async def _initiate_auth(self, body):
        return self.c_idp.initiate_auth(ClientId=self.user_pool_client_id, **body)

    async def sign_in(self, body):
        """Get a user by their username and password."""
        try:
            user = await db.query(pk=body["username"], index_name="username_index")
            if not user:
                return {"success": False, "msg": "User not found"}
            user = user[0]
            password = body["password"].get_secret_value()

            # check password
            if user["password"] != password:
                return Rs.error(msg="Incorrect password")

            user["access_tokens"] = user["access_tokens"].attribute_values
            if user["access_tokens"]:
                # check if access_token is expired
                if user["access_tokens"]["ExpiresIn"] < int(time()):
                    # refresh token
                    payload = dict(AuthFlow="REFRESH_TOKEN_AUTH",
                                   AuthParameters={"REFRESH_TOKEN": user["access_tokens"]["RefreshToken"]})
                    _init_auth = await self._initiate_auth(payload)
                    if _init_auth["ResponseMetadata"]["HTTPStatusCode"] == 200:
                        _init_auth["AuthenticationResult"]["ExpiresIn"] = _init_auth["AuthenticationResult"][
                                                                              "ExpiresIn"] + int(time())
                        # update tokens in dynamodb
                        user["access_tokens"] = _init_auth["AuthenticationResult"]
                        await db.update(**user)
                        return Rs.success(data=user["access_tokens"], msg="User logged in successfully")
                    return Rs.error(msg="User not logged in")
                else:
                    return Rs.success(data=user["access_tokens"], msg="User logged in successfully")
            else:
                payload = dict(AuthFlow="USER_PASSWORD_AUTH",
                               AuthParameters={"USERNAME": user["email"], "PASSWORD": password})
                _init_auth = await self._initiate_auth(payload)

                if _init_auth["ResponseMetadata"]["HTTPStatusCode"] == 200:
                    _init_auth["AuthenticationResult"]["ExpiresIn"] = _init_auth["AuthenticationResult"][
                                                                          "ExpiresIn"] + int(time())
                    # update tokens in dynamo
                    user["access_tokens"] = _init_auth["AuthenticationResult"]
                    await db.update(user)
                    return Rs.success(data=user["access_tokens"], msg="User logged in successfully")
                return Rs.error(msg="User not logged in")
        except Exception as e:
            return Rs.server_error(e.__str__())

    async def resend_confirmation_code(self, email):
        try:
            return self.c_idp.resend_confirmation_code(
                ClientId=self.user_pool_client_id,
                Username=email
            )
        except Exception as e:
            return Rs.server_error(e.__str__())

    async def forgot_password(self, email):
        try:
            return self.c_idp.forgot_password(
                ClientId=self.user_pool_client_id,
                Username=email)
        except Exception as e:
            return Rs.server_error(e.__str__())

    async def confirm_forgot_password(self, body):
        try:
            user = await db.query(pk=body["email"], index_name="email_index")
            if not user:
                return Rs.not_found(msg="User not found")
            user = user[0]

            password = body["password"].get_secret_value()

            response = self.c_idp.confirm_forgot_password(
                ClientId=self.user_pool_client_id, Username=body["email"], ConfirmationCode=body["code"],
                Password=password
            )
            if response["ResponseMetadata"]["HTTPStatusCode"] == 200:
                # update password in dynamodb
                user["password"] = password
                await db.update(user)
                # get tokens from dynamodb
                user["access_tokens"] = user["access_tokens"].attribute_values
                return Rs.success(data=user["access_tokens"], msg="Password changed successfully")

            return Rs.error(msg="Password not changed")
        except Exception as e:
            return Rs.server_error(e.__str__())


class Be3UserDashboard(Be3UserAdmin):
    async def delete_user(self, _token):
        """remove user from cognito"""
        try:
            details = self.get_user_info(_token)
            pk = details["UserAttributes"][0]["Value"]
            email = details["UserAttributes"][3]["Value"]
            self.c_idp.admin_delete_user(
                UserPoolId=self.user_pool_id,
                Username=email
            )
            await db.delete(pk)
            return Rs.success(msg="User deleted successfully")
        except Exception as e:
            return Rs.server_error(e.__str__())

    def get_user_info(self, access_token):
        return self.c_idp.get_user(AccessToken=access_token)

    async def sign_out(self, access_token, pk):
        try:
            self.c_idp.global_sign_out(
                AccessToken=access_token
            )
            # remove tokens from dynamodb
            user = await db.get(pk)
            user["access_tokens"] = {}
            await db.update(user)

            return Rs.success(msg="User signed out successfully")
        except Exception as e:
            return Rs.server_error(e.__str__())

    async def change_password(self, token, body):
        try:
            user = self.get_user_info(token)
            pk = user["UserAttributes"][0]["Value"]
            user = await db.get(pk)
            if not user:
                return Rs.not_found(msg="User not found")

            response = self.c_idp.change_password(
                PreviousPassword=body["old_password"].get_secret_value(),
                ProposedPassword=body["new_password"].get_secret_value(),
                AccessToken=token
            )
            if response["ResponseMetadata"]["HTTPStatusCode"] == 200:
                user["password"] = body["new_password"].get_secret_value()
                await db.update(user)
                return Rs.success(msg="Password changed successfully")
            return Rs.error(msg="Password not changed")
        except Exception as e:
            return Rs.server_error(e.__str__())

    async def get_user_details(self, token):
        try:
            user = self.get_user_info(token)
            pk = user["UserAttributes"][0]["Value"]
            user = await db.get(pk)
            if not user:
                return Rs.not_found(msg="User not found")
            user["access_tokens"] = user["access_tokens"].attribute_values
            return Rs.success(data=user)
        except Exception as e:
            return Rs.server_error(e.__str__())
