from pathlib import Path
from aws_cdk import (
    Duration,
    Stack,
    CfnOutput,
    RemovalPolicy,
    aws_lambda as _lambda,
    aws_iam as _iam,
    aws_cognito as _cognito,
    BundlingOptions,
    DockerImage
)
from constructs import Construct
import aws_cdk.aws_apigatewayv2_alpha as _apigwv2
import aws_cdk.aws_apigatewayv2_integrations_alpha as _api_integrations
from aws_cdk.aws_apigatewayv2_authorizers_alpha import HttpUserPoolAuthorizer as _authorizer

from config import settings

LAMBDA_ASSET_PATH = Path(__file__).parent.parent.joinpath("api", "src")


class ApiGatewayStack(Stack):

    def __init__(self,
                 scope: Construct,
                 construct_id: str,
                 _apigw_domain_name: _apigwv2.DomainName,
                 **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.http_api = _apigwv2.HttpApi(
            self, "http_api_gateway",
            default_domain_mapping=_apigwv2.DomainMappingOptions(domain_name=_apigw_domain_name),
            create_default_stage=True)

        self.stage = self.http_api.add_stage("dev-stage", auto_deploy=True, stage_name="dev")

        lambda_handler: _lambda.Function = self.create_be3_api_lambda_handler()

        lambda_handler.add_permission(
            "be3_manage-user-api-lambda-permission",
            principal=_iam.ServicePrincipal("apigateway.amazonaws.com"),
            action="lambda:InvokeFunction",
            source_arn=self.http_api.http_api_id)

        _lambda_integration = _api_integrations.HttpLambdaIntegration(
            "be3_manage-user-api-lambda-integration",
            handler=lambda_handler,
        )
        # lambda_handler.grant_invoke(lambda_integration)
        self.http_api.add_routes(
            path="/api/v1/users",
            methods=[_apigwv2.HttpMethod.GET],
            integration=_lambda_integration
            # authorizer=_authorizer(
        )

    def create_be3_api_lambda_handler(self) -> _lambda.Function:
        func = _lambda.Function(
            self, "be3_manage-user-api-lambda",
            timeout=Duration.minutes(1),
            memory_size=512,
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler="index.handler",
            code=_lambda.Code.from_asset(
                path=LAMBDA_ASSET_PATH,
                bundling=BundlingOptions(
                    image=DockerImage.from_registry("amazon/aws-sam-cli-build-image-python3.9"),
                    command=["bash", "-c",
                             "pip install -r requirements.txt -t /asset-output && cp -au . /asset-output"],
                )
            ),
            environment={"ENVIRONMENT": "DEV", "REGION": settings.aws_region, "ACCOUNT_ID": settings.aws_acc_id}
        )
        func.role.attach_inline_policy(
            policy=_iam.Policy(
                self, "be3_manage-user-api-lambda-policy",
                document=_iam.PolicyDocument.from_json(
                    {
                        "Version": "2012-10-17",
                        "Statement": [
                            {
                                "Action": [
                                    "quicksight:GenerateEmbedUrlForRegisteredUser",
                                    "quicksight:SearchDashboards",
                                    "quicksight:DescribeUser",
                                    "quicksight:RegisterUser",
                                    "quicksight:CreateGroup",
                                    "quicksight:CreateGroupMembership",
                                ],
                                "Resource": "*",
                                "Effect": "Allow",
                            },
                            {
                                "Action": [
                                    "logs:CreateLogGroup",
                                    "logs:CreateLogStream",
                                    "logs:PutLogEvents",
                                ],
                                "Resource": "*",
                                "Effect": "Allow",
                            },
                        ],
                    }
                ),
            )
        )
        return func