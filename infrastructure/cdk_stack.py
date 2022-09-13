from pathlib import Path
from unittest import defaultTestLoader
from aws_cdk import (
    Duration,
    CfnOutput,
    Duration,
    RemovalPolicy,
    Stack,
    aws_cognito as cognito,
    aws_lambda as lambda_,
    aws_apigatewayv2_alpha as apigatewayv2,
)
from aws_cdk.aws_apigatewayv2_integrations_alpha import HttpLambdaIntegration
from constructs import Construct
from aws_cdk.aws_apigatewayv2_authorizers_alpha import HttpUserPoolAuthorizer


LAMBDA_ASSET_PATH = str(Path(__file__).parent.parent.joinpath("api", "src"))

class CdkStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        user_pool = cognito.UserPool(
            self,
            "UserPool",
            self_sign_up_enabled=True,
            standard_attributes=cognito.StandardAttributes(
                email=cognito.StandardAttribute(required=True, mutable=True),
                phone_number=cognito.StandardAttribute(required=False),
            ),
            sign_in_case_sensitive=False,
            auto_verify=cognito.AutoVerifiedAttrs(email=True),
            sign_in_aliases=cognito.SignInAliases(email=True, username=False),
            account_recovery=cognito.AccountRecovery.EMAIL_ONLY,
            removal_policy=RemovalPolicy.DESTROY,
        )
        user_pool_domain = user_pool.add_domain(
            "Domain",
            cognito_domain=cognito.CognitoDomainOptions(domain_prefix="be3-cdk"),
        )
        user_pool_client = user_pool.add_client(
            "Client",
            o_auth=cognito.OAuthSettings(
                flows=cognito.OAuthFlows(implicit_code_grant=True),
                callback_urls=["https://www.example.com/cb"],
                logout_urls=["https://www.example.com/signout"],
                scopes=[
                    cognito.OAuthScope.EMAIL,
                    cognito.OAuthScope.OPENID,
                    cognito.OAuthScope.PROFILE,
                ],
            ),
        )

        function_asset = lambda_.Code.from_asset(LAMBDA_ASSET_PATH)

        get_data_function = lambda_.Function(
            self,
            "GetDataFunction",
            code=function_asset,
            runtime=lambda_.Runtime.PYTHON_3_9,
            handler="app.get_data",
            timeout=Duration.seconds(5),
        )

        create_data_function = lambda_.Function(
            self,
            "CreateDataFunction",
            code=function_asset,
            runtime=lambda_.Runtime.PYTHON_3_9,
            handler="app.create_data",
            timeout=Duration.seconds(5),
        )

        authorizer = HttpUserPoolAuthorizer(
            "UserPoolAuthorizer", pool=user_pool, user_pool_clients=[user_pool_client]
        )

        api = apigatewayv2.HttpApi(
            self,
            "Api",
            default_authorizer=authorizer,
        )
        api.add_routes(
            path="/data",
            methods=[apigatewayv2.HttpMethod.GET],
            integration=HttpLambdaIntegration("GetDataIntegration", get_data_function),
        )
        api.add_routes(
            path="/data",
            methods=[apigatewayv2.HttpMethod.POST],
            integration=HttpLambdaIntegration(
                "CreateDataIntegration", create_data_function
            ),
        )

        CfnOutput(self, "OutputApiUrl", value=api.url)
        CfnOutput(self, "OutputUserPoolDomain", value=user_pool_domain.domain_name)
