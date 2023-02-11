from functools import lru_cache
from pathlib import Path

from pydantic import BaseSettings, Field


class ServerConfig(BaseSettings):
    env_state: str = Field(None, env="ENV_STATE")

    # """Server Config"""
    host: str = Field(None, env="HOST")
    port: int = Field(None, env="PORT")
    app_name: str = Field(None, env="APP_NAME")
    debug: bool = Field(None, env="DEBUG")

    # """iDrive Config"""
    reseller_api_key: str = Field(None, env="IDRIVE_RESELLER_API_KEY")
    reseller_base_url: str = Field(None, env="IDRIVE_RESELLER_BASE_URL")

    # """AWS Config"""
    aws_access_key: str = Field(None, env="AWS_ACCESS_KEY")
    aws_secret_key: str = Field(None, env="AWS_SECRET_KEY")
    aws_default_region: str = Field(None, env="AWS_DEFAULT_REGION")
    aws_account_id: str = Field(None, env="AWS_ACCOUNT_ID")

    # """VPC Config"""
    vpc_id: str = Field(None, env="VPC_ID")
    vpc_security_group_id: str = Field(None, env="SECURITY_GROUP_ID")

    # """USER-POOL CONFIG"""
    user_pool_id: str = Field(None, env="USER_POOL_ID")
    user_pool_client_id: str = Field(None, env="USER_POOL_CLIENT_ID")

    class Config:
        env_file = ".env" if Path(".env").exists() else "src/.env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings():
    return ServerConfig()


settings = get_settings()
