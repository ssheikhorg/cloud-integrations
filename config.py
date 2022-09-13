import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

class Config(object):
    idrive_ak = os.environ.get("IDRIVE_ACCESS_KEY")
    idrive_sk = os.environ.get("IDRIVE_SECRET_KEY")
    idrive_endpoint = os.environ.get("IDRIVE_ENDPOINT_URL")

    aws_acc_id = os.environ.get("AWS_ACCOUNT_ID")
    aws_ak = os.environ.get("AWS_ACCESS_KEY")
    aws_sk = os.environ.get("AWS_SECRET_KEY")
    aws_region = os.environ.get("AWS_REGION")

    cognito_cb_url = os.environ.get("COGNITO_CALLBACK_URL")
    cognito_logout_url = os.environ.get("COGNITO_LOGOUT_URL")


settings = Config()
