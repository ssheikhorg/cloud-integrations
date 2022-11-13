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
    aws_dynamodb as dynamodb, RemovalPolicy,
)
from aws_cdk.aws_apigatewayv2_integrations_alpha import HttpLambdaIntegration

from src.functions.config import settings as c


class Be3cloudApi(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        """create a dynamodb table"""
        self.table = self.create_table()

        """create base api gateway"""
        self.api = apigwv2.HttpApi(self, "Be3Api")

        """create an admin iam role for lambda function"""
        self.admin_role = self.create_iam_role()

        """lambda layers"""
        self.be3_lambda_layer = self.create_lambda_layer()

        """lambda function settings"""
        self.handler = self.create_lambda_handler()

        """add routes for mangum fastapi all routes"""
        self.api.add_routes(path="/{proxy+}", methods=[apigwv2.HttpMethod.ANY],
                            integration=HttpLambdaIntegration("Be3 proxy integration", self.handler))

        """output"""
        CfnOutput(self, "ApiUrl", value=self.api.api_endpoint)

    def create_lambda_handler(self):
        """create a lambda function"""
        # look up the vpc
        self.vpc = ec2.Vpc.from_lookup(self, "VPC", vpc_id=c.vpc_id)

        """subnets resources should use"""
        self.private_subnets = []
        for idx, subnet in enumerate(self.vpc.private_subnets):
            self.private_subnets.append(ec2.Subnet.from_subnet_id(self, f"PrivateSubnet{idx}", subnet.subnet_id))

        """base default security group"""
        self.security_group = ec2.SecurityGroup.from_security_group_id(
            self, "Be3SecurityGroup", security_group_id=c.vpc_security_group_id)

        return lambda_python.PythonFunction(
            self, "Be3Handler", function_name="be3-lambda-base-handler",
            entry="src", index="functions/apps.py", handler="handler", runtime=lambda_.Runtime.PYTHON_3_9,
            memory_size=512, timeout=Duration.minutes(1), layers=[self.be3_lambda_layer],
            role=self.admin_role, vpc=self.vpc, vpc_subnets=ec2.SubnetSelection(subnets=self.private_subnets),
            security_groups=[self.security_group]
        )

    def create_table(self):
        """create a dynamodb table with cdk"""
        return dynamodb.Table(
            self, "Be3Table", table_name="be3Table",
            partition_key=dynamodb.Attribute(name="pk", type=dynamodb.AttributeType.STRING),
            sort_key=dynamodb.Attribute(name="sk", type=dynamodb.AttributeType.STRING),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.RETAIN
        )

    def create_lambda_layer(self):
        """create a lambda layer for lambda function"""
        return lambda_python.PythonLayerVersion(
            self, "Be3Layer", entry="src/layer", compatible_runtimes=[lambda_.Runtime.PYTHON_3_9],
            layer_version_name="be3-lambda-base-layer")

    def create_iam_role(self):
        """create an iam role for lambda function"""
        return iam.Role(
            self, "AdminRole", assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            role_name="be3-lambda-base-role", managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaBasicExecutionRole"),
                iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaVPCAccessExecutionRole"),
                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonDynamoDBFullAccess"),
            ])