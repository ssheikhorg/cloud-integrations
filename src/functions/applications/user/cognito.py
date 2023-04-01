from time import time
from datetime import datetime
from typing import Any
import boto3
from fastapi import status as s

from ...models.users import UserModel
from ...core.config import settings as c
from ...core.database import DynamoDB
from ...utils.response import HttpResponse as Rs

db = DynamoDB(UserModel)


class Be3UserAdmin:
    def __init__(self) -> None:
        self.c_idp = boto3.client("cognito-idp", region_name=c.aws_default_region,
                                  aws_access_key_id=c.aws_access_key, aws_secret_access_key=c.aws_secret_key)
        self.user_pool_id = c.user_pool_id
        self.user_pool_client_id = c.user_pool_client_id

    async def add_user_to_group(self, username: str, role: str) -> None:
        self.c_idp.admin_add_user_to_group(
            UserPoolId=self.user_pool_id,
            Username=username,
            GroupName=role
        )

    async def sign_up(self, body: dict) -> Any:
        try:
            _username = await db.count(pk=body["username"], index_name="username_index")
            if _username > 0:
                return Rs.conflict(msg="Username already exists")

            body["password"] = body["password"].get_secret_value()
            name = body["first_name"] + " " + body["last_name"]
            resp = self.c_idp.sign_up(
                ClientId=self.user_pool_client_id,
                Username=body["username"],
                Password=body["password"],
                UserAttributes=[{"Name": "name", "Value": name},
                                {"Name": "email", "Value": body["email"]}])

            # add user to specific group
            await self.add_user_to_group(body["username"], body["role"])

            # save user in dynamo
            body["pk"] = resp["UserSub"]
            body["email_verified"] = resp["UserConfirmed"]
            body["created_at"] = str(datetime.today().replace(microsecond=0))

            # save user in dynamo
            await db.create(body)
            return Rs.created(msg="User created successfully")
        except Exception as e:
            return Rs.server_error(e.__str__())

    async def update_user(self, body: dict) -> Any:
        try:
            user = await db.get(pk=body["pk"], sk="user")
            if not user:
                return Rs.not_found(msg="User not found")

            name = body["first_name"] + " " + body["last_name"]
            # update user in cognito
            result = self.c_idp.admin_update_user_attributes(
                UserPoolId=self.user_pool_id,
                Username=user["username"],
                UserAttributes=[
                    {
                        "Name": "name", "Value": name
                    }
                ]
            )
            if result["ResponseMetadata"]["HTTPStatusCode"] == s.HTTP_200_OK:
                # update user in dynamo
                user["first_name"] = body["first_name"]
                user["last_name"] = body["last_name"]
                user["updated_at"] = str(datetime.today().replace(microsecond=0))
                await db.update(user)
                return Rs.success(msg="User updated successfully")
        except Exception as e:
            return Rs.server_error(e.__str__())

    async def confirm_signup(self, body: dict) -> Any:
        try:
            response = self.c_idp.confirm_sign_up(
                ClientId=self.user_pool_client_id,
                Username=body["username"],
                ConfirmationCode=body["code"],
                ForceAliasCreation=False
            )
            if response["ResponseMetadata"]["HTTPStatusCode"] == s.HTTP_200_OK:
                # get user from dynamo with email index
                user = await db.query(pk=body["username"], index_name="username_index")
                user[0]["email_verified"] = True
                await db.update(user[0])
                return Rs.success(msg="User confirmed")
            return Rs.bad_request(msg="User not confirmed")
        except Exception as e:
            return Rs.server_error(msg="Invalid code provided, please request a new one")

    async def _initiate_auth(self, body: dict) -> Any:
        return self.c_idp.initiate_auth(ClientId=self.user_pool_client_id, **body)

    async def sign_in(self, body: dict) -> Any:
        """Get a user by their username and password."""
        try:
            results = await db.query(pk=body["username"], index_name="username_index")
            if not results:
                return Rs.not_found(msg="User not found")
            user = results[0]
            password = body["password"].get_secret_value()

            # check if user is confirmed
            if not user.get("email_verified"):
                return Rs.bad_request(
                    data={"email": user.get("email"), "username": user.get("username")},
                    msg="User not confirmed, please confirm your email address")

            # check password
            if user.get("password") != password:
                return Rs.bad_request(msg="Incorrect password")

            user["access_tokens"] = user["access_tokens"].attribute_values
            if user["access_tokens"]:
                # check if access_token is expired
                if user["access_tokens"]["ExpiresIn"] < int(time()):
                    refresh_token = user["access_tokens"].get("RefreshToken")
                    if refresh_token:
                        payload = dict(AuthFlow="REFRESH_TOKEN_AUTH",
                                       AuthParameters={"REFRESH_TOKEN": refresh_token})
                        _init_auth = await self._initiate_auth(payload)
                        if _init_auth["ResponseMetadata"]["HTTPStatusCode"] == s.HTTP_200_OK:
                            _init_auth["AuthenticationResult"]["ExpiresIn"] = _init_auth["AuthenticationResult"][
                                                                                  "ExpiresIn"] + int(time())
                            # update tokens in dynamodb
                            user["access_tokens"] = _init_auth["AuthenticationResult"]
                            await db.update(user)
                            return Rs.success(data=user["access_tokens"], msg="User logged in successfully")
                        return Rs.bad_request(msg="User not logged in")
                    else:
                        user["access_tokens"] = {}
                        await db.update(user)
                        return Rs.bad_request(msg="User not logged in, please login again")
                else:
                    return Rs.success(data=user["access_tokens"], msg="User logged in successfully")
            else:
                payload = dict(AuthFlow="USER_PASSWORD_AUTH",
                               AuthParameters={"USERNAME": body["username"], "PASSWORD": password})
                _init_auth = await self._initiate_auth(payload)

                if _init_auth["ResponseMetadata"]["HTTPStatusCode"] == s.HTTP_200_OK:
                    _init_auth["AuthenticationResult"]["ExpiresIn"] = _init_auth["AuthenticationResult"][
                                                                          "ExpiresIn"] + int(time())
                    # update tokens in dynamo
                    user["access_tokens"] = _init_auth["AuthenticationResult"]
                    await db.update(user)
                    return Rs.success(data=user["access_tokens"], msg="User logged in successfully")
                return Rs.bad_request(msg="User not logged in")
        except Exception as e:
            return Rs.server_error(e.__str__())

    async def resend_confirmation_code(self, email: str) -> Any:
        try:
            return self.c_idp.resend_confirmation_code(
                ClientId=self.user_pool_client_id,
                Username=email
            )
        except Exception as e:
            return Rs.server_error(e.__str__())

    async def forgot_password(self, email: str) -> Any:
        try:
            response = self.c_idp.forgot_password(
                ClientId=self.user_pool_client_id,
                Username=email)
            if response["ResponseMetadata"]["HTTPStatusCode"] == s.HTTP_200_OK:
                return Rs.success(msg="Code sent successfully")
            return Rs.bad_request(msg="Code not sent")
        except Exception as e:
            return Rs.server_error(e.__str__())

    async def confirm_forgot_password(self, body: dict) -> Any:
        try:
            users = await db.query(pk=body["username"], index_name="username_index")
            if not users:
                return Rs.not_found(msg="User not found")
            user = users[0]

            password = body["password"].get_secret_value()

            response = self.c_idp.confirm_forgot_password(
                ClientId=self.user_pool_client_id, Username=body["username"], ConfirmationCode=body["code"],
                Password=password
            )
            if response["ResponseMetadata"]["HTTPStatusCode"] == s.HTTP_200_OK:
                # update password in dynamodb
                user["password"] = password
                await db.update(user)
                # get tokens from dynamodb
                user["access_tokens"] = user["access_tokens"].attribute_values
                return Rs.success(data=user["access_tokens"], msg="Password changed successfully")
            return Rs.bad_request(msg="Password not changed")
        except Exception as e:
            return Rs.server_error(e.__str__())


class Be3UserDashboard(Be3UserAdmin):
    async def delete_user(self, pk: str) -> Any:
        """remove user from cognito"""
        try:
            user = await db.get(pk, "user")
            if not user:
                return Rs.not_found(msg="User not found")
            username = user["username"]
            self.c_idp.admin_delete_user(
                UserPoolId=self.user_pool_id,
                Username=username
            )
            await db.delete(pk, "user")
            return Rs.success(msg="User deleted successfully")
        except Exception as e:
            return Rs.server_error(e.__str__())

    def get_user_info(self, access_token: str) -> Any:
        return self.c_idp.get_user(AccessToken=access_token)

    async def sign_out(self, _token: str) -> Any:
        try:
            user = self.get_user_info(_token)
            pk = user["UserAttributes"][0]["Value"]
            user = await db.get(pk, "user")
            if not user:
                return Rs.not_found(msg="User not found")

            self.c_idp.global_sign_out(
                AccessToken=_token
            )
            # remove tokens from dynamodb
            user["access_tokens"] = {}
            await db.update(user)

            return Rs.success(msg="User signed out successfully")
        except Exception as e:
            return Rs.server_error(e.__str__())

    async def change_password(self, token: str, body: dict) -> Any:
        try:
            user = self.get_user_info(token)
            pk = user["UserAttributes"][0]["Value"]
            user = await db.get(pk, "user")
            if not user:
                return Rs.not_found(msg="User not found")

            response = self.c_idp.change_password(
                PreviousPassword=body["old_password"].get_secret_value(),
                ProposedPassword=body["new_password"].get_secret_value(),
                AccessToken=token
            )
            if response["ResponseMetadata"]["HTTPStatusCode"] == s.HTTP_200_OK:
                user["password"] = body["new_password"].get_secret_value()
                await db.update(user)
                return Rs.success(msg="Password changed successfully")
            return Rs.bad_request(msg="Password not changed")
        except Exception as e:
            return Rs.server_error(e.__str__())

    async def get_user_details(self, token: str) -> Any:
        try:
            user = self.get_user_info(token)
            pk = user["UserAttributes"][0]["Value"]
            user = await db.get(pk, "user")
            idrive = await db.get(pk, "idrive")
            if not user:
                return Rs.not_found(msg="User not found")
            user["access_tokens"] = user["access_tokens"].attribute_values
            user["idrive"] = idrive
            return Rs.success(data=user)
        except Exception as e:
            return Rs.server_error(e.__str__())

    @staticmethod
    async def get_all_users(limit: int, offset: int) -> Any:
        try:
            users = await db.scan(limit, offset)
            for x in users:
                x["access_tokens"] = x["access_tokens"].attribute_values
            return Rs.success(data=users, msg="Users fetched successfully")
        except Exception as e:
            return Rs.server_error(e.__str__())


cognito = Be3UserDashboard()
