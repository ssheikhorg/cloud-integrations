import boto3
from .helpers import get_secret_hash
from ..core.configs import settings as c


class Be3CloudUser:
    def __init__(self):
        self.c_idp = boto3.client('cognito-idp', region_name=c.aws_default_region,
                                  aws_access_key_id=c.aws_access_key, aws_secret_access_key=c.aws_secret_key)
        self.dynamo = boto3.resource('dynamodb', region_name=c.aws_default_region,
                                     aws_access_key_id=c.aws_access_key, aws_secret_access_key=c.aws_secret_key)
        self.table = self.dynamo.Table("be3cloud-table")

        # user pool
        self.user_pool_id = c.up_id
        self.user_pool_client_id = c.up_client_id

    def add_user_to_group(self, email, role):
        self.c_idp.admin_add_user_to_group(
            UserPoolId=self.user_pool_id,
            Username=email,
            GroupName=role
        )

    def get_users(self):
        # get all users from dynamo
        response = self.table.scan()
        return response['Items']

    def sign_up(self, data):
        try:
            name = data['first_name'] + " " + data['last_name']
            resp = self.c_idp.sign_up(
                ClientId=self.user_pool_client_id,
                SecretHash=get_secret_hash(data['email']),
                Username=data['email'],
                Password=data['password'],
                UserAttributes=[{'Name': 'name', 'Value': name},
                                {'Name': 'email', 'Value': data['email']}
                                ])
            # add user to specific group
            self.add_user_to_group(data['email'], data['role'])

            # save user in dynamo
            data['user_id'] = resp['UserSub']
            data["status"] = resp['UserConfirmed']
            data['pk'] = data.pop('email')
            data['sk'] = data.pop('role')
            # put data in table with pk as hash key and sk as range key
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
            ClientId=self.user_pool_client_id,
            SecretHash=get_secret_hash(data["email"]),
            Username=data["email"],
            ConfirmationCode=data["code"],
            ForceAliasCreation=False
        )
        if response['ResponseMetadata']['HTTPStatusCode'] == 200:
            # update user status in dynamo
            query = {'pk': data['email'], 'sk': data['role']}
            self.table.update_item(
                Key=query,
                UpdateExpression="set #status = :status",
                ExpressionAttributeNames={'#status': 'status'},
                ExpressionAttributeValues={':status': True}
            )
            return {"success": True}
        return {"success": False}

    def sign_in(self, data):
        response = self.c_idp.initiate_auth(
            AuthFlow='USER_PASSWORD_AUTH',
            AuthParameters={"USERNAME": data['email'], "PASSWORD": data['password'],
                            "SECRET_HASH": get_secret_hash(data['email'])},
            ClientId=self.user_pool_client_id
        )
        tokens = {
            "access_token": response['AuthenticationResult']['AccessToken'],
            "refresh_token": response['AuthenticationResult']['RefreshToken']
        }
        return tokens

    def resend_confirmation_code(self, email):
        response = self.c_idp.resend_confirmation_code(
            ClientId=self.user_pool_client_id,
            SecretHash=get_secret_hash(email),
            Username=email
        )
        return response

    # remove user from cognito
    def delete_user(self, email, role):
        query = {'pk': email, 'sk': role}
        response = self.table.get_item(Key=query)
        if 'Item' in response:
            # delete user from cognito
            self.c_idp.admin_delete_user(
                UserPoolId=self.user_pool_id,
                Username=email
            )
            # delete user from dynamo
            self.table.delete_item(Key=query)
            return {"success": True}

        return {"success": False}


'''
    def get_user_info(self, access_token):
        response = self.c_idp.get_user(
            AccessToken=access_token
        )
        return response
'''
