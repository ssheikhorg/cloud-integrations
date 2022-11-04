from constructs import Construct
from aws_cdk import (
    Stack,
    Duration,
    aws_lambda as lambda_,
    aws_lambda_python_alpha as lambda_python,
    aws_apigatewayv2_alpha as apigwv2,
    CfnOutput,
    aws_ec2 as ec2,
    aws_iam as iam,
)
from aws_cdk.aws_apigatewayv2_integrations_alpha import HttpLambdaIntegration


class Be3cloudApi(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.api = apigwv2.HttpApi(self, "Be3cloudApi")

        # create an admin iam role for lambda function
        self.admin_role = iam.Role(
            self,
            "AdminRole",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    "service-role/AWSLambdaBasicExecutionRole"
                ),
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    "service-role/AWSLambdaVPCAccessExecutionRole"
                ),
            ],
        )

        self.handler = lambda_python.PythonFunction(
            self, "Be3cloudHandler",
            entry="src",
            index="functions/apps.py",
            handler="handler",
            runtime=lambda_.Runtime.PYTHON_3_9,
            memory_size=512,
            timeout=Duration.minutes(1),
            layers=[lambda_python.PythonLayerVersion(self, "Be3cloudLayer", entry="src/layer",
                                                     compatible_runtimes=[lambda_.Runtime.PYTHON_3_9],
                                                     layer_version_name="be3cloud-layer")],
            role=self.admin_role,
            # vpc=ec2.Vpc.from_lookup(self, "VPC", vpc_id="vpc-08b1a7047fdf558f8"),
            # vpc_subnets=ec2.SubnetSelection(
            #     subnet_type=ec2.SubnetSelection(subnet_id="subnet-022239d5aaa99fff4"),
            #     security_groups=[ec2.SecurityGroup.from_security_group_id(self, "SecurityGroup",
            #                                                               security_group_id="sg-070a5e923f0520a43")]),
            environment={"DEBUG": "True"}
        )

        # add routes for mangum fastapi all routes
        self.api.add_routes(path="/{proxy+}", methods=[apigwv2.HttpMethod.ANY],
                            integration=HttpLambdaIntegration("Be3 proxy integration", self.handler))
        # print api url to console
        self.url_output = CfnOutput(self, "ApiUrl", value=self.api.api_endpoint)


'''
        # add jwt authorizer
        issuer = "https://cognito-idp.eu-west-2.amazonaws.com/eu-west-2_KnzhR3I2G"
        self.authorizer = apigwv2_auth.HttpJwtAuthorizer("Be3cloudAuthorizer",
                                                         issuer, jwt_audience=["5eco5npnchd9229rakb0s7mt3o"],
                                                         identity_source=["$request.header.Authorization"],
                                                         authorizer_name="be3cloud-authorizer")
'''
