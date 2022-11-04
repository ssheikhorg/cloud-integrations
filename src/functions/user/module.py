import boto3

from .helpers import get_secret_hash
from ..core.configs import settings as c


class CognitoUser:
    def __init__(self):
        self.c_idp = boto3.client('cognito-idp', region_name=c.aws_default_region,
                                  aws_access_key_id=c.aws_access_key, aws_secret_access_key=c.aws_secret_key)
        self.dynamo = boto3.resource('dynamodb', region_name=c.aws_default_region,
                                     aws_access_key_id=c.aws_access_key, aws_secret_access_key=c.aws_secret_key)
        self.table = self.dynamo.Table("be3-table")

    def add_user_to_group(self, data):
        self.c_idp.admin_add_user_to_group(
            UserPoolId=c.up_id,
            Username=data['email'],
            GroupName=data['role']
        )

    def get_users(self):
        # get all users from dynamo
        response = self.table.scan()
        return response['Items']

    def sign_up(self, data):
        try:
            name = data['first_name'] + " " + data['last_name']
            resp = self.c_idp.sign_up(
                ClientId=c.up_client_id,
                SecretHash=get_secret_hash(data['email']),
                Username=data['email'],
                Password=data['password'],
                UserAttributes=[{'Name': 'name', 'Value': name},
                                {'Name': 'email', 'Value': data['email']}
                                ])
            # add user to specific group
            self.add_user_to_group(data)

            # save user in dynamo
            data['user_id'] = resp['UserSub']
            self.table.put_item(Item=data)
            return {"success": True}
        except self.c_idp.exceptions.UsernameExistsException:
            return {"success": False, "message": "User already exists"}
        except Exception as e:
            return {"success": False, "message": e.__str__()}

    def sign_out(self, access_token):
        self.c_idp.global_sign_out(
            AccessToken=access_token
        )
        return {"success": True}

    def confirm_signup(self, data):
        response = self.c_idp.confirm_sign_up(
            ClientId=c.up_client_id,
            SecretHash=get_secret_hash(data["email"]),
            Username=data["email"],
            ConfirmationCode=data["code"],
            ForceAliasCreation=False
        )
        return response

    def sign_in(self, data):
        response = self.c_idp.initiate_auth(
            AuthFlow='USER_PASSWORD_AUTH',
            AuthParameters={"USERNAME": data['email'], "PASSWORD": data['password'],
                            "SECRET_HASH": get_secret_hash(data['email'])},
            ClientId=c.up_client_id
        )
        tokens = {
            "access_token": response['AuthenticationResult']['AccessToken'],
            "refresh_token": response['AuthenticationResult']['RefreshToken']
        }
        return tokens

    def resend_confirmation_code(self, data):
        response = self.c_idp.resend_confirmation_code(
            ClientId=c.up_client_id,
            SecretHash=get_secret_hash(data["email"]),
            Username=data["email"]
        )
        return response

    def get_user_info(self, access_token):
        response = self.c_idp.get_user(
            AccessToken=access_token
        )
        return response
