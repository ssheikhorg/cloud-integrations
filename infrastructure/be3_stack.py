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

        # lambda layers
        self.be3_lambda_layer = lambda_python.PythonLayerVersion(
            self, "Be3cloudLayer", entry="src/layer", compatible_runtimes=[lambda_.Runtime.PYTHON_3_9],
            layer_version_name="be3cloud-layer")

        # look up the vpc
        self.vpc = ec2.Vpc.from_lookup(self, "VPC", vpc_id="vpc-08b1a7047fdf558f8")

        # subnets resources should use

        self.private_subnets = []
        for idx, subnet in enumerate(self.vpc.private_subnets):
            self.private_subnets.append(ec2.Subnet.from_subnet_id(self, f"PrivateSubnet{idx}", subnet.subnet_id))

        # base default security group
        self.security_group = ec2.SecurityGroup.from_security_group_id(
            self, "Be3cloudSecurityGroup", security_group_id="sg-070a5e923f0520a43")

        # lambda function settings
        self.handler = lambda_python.PythonFunction(
            self, "Be3cloudHandler",
            function_name="be3cloud-base-lambda-handler",
            entry="src",
            index="functions/apps.py",
            handler="handler",
            runtime=lambda_.Runtime.PYTHON_3_9,
            memory_size=512,
            timeout=Duration.minutes(1),
            layers=[self.be3_lambda_layer],
            role=self.admin_role,

            vpc=self.vpc,
            # vpc_subnets=self.private_subnets,
            vpc_subnets=ec2.SubnetSelection(subnets=self.private_subnets),
            security_groups=[self.security_group],
        )

        # add routes for mangum fastapi all routes
        self.api.add_routes(path="/{proxy+}", methods=[apigwv2.HttpMethod.ANY],
                            integration=HttpLambdaIntegration("Be3 proxy integration", self.handler))
        # print api url to console
        self.url_output = CfnOutput(self, "ApiUrl", value=self.api.api_endpoint)
