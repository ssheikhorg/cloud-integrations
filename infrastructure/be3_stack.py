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
    aws_cognito as cognito
)
from aws_cdk.aws_apigatewayv2_integrations_alpha import HttpLambdaIntegration

from src.functions.core.config import settings as c


class Be3cloudApi(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        """create a dynamodb table"""
        self.table = self.create_table("be3-dynamo-table")

        """create all GSI for table"""
        self.create_gsi("role", "role-index")
        self.create_gsi("username", "username-index")
        self.create_gsi("email", "email-index")

        """create a cognito user pool"""
        self.user_pool = self.create_cognito_user_pool("be3-user-pool")
        self.user_pool_client = self.create_cognito_user_pool_client("be3-user-pool-client")

        """create a cognito user pool group"""
        admin_group = cognito.CfnUserPoolGroup(self, f"{c.env_state}-admin-user-group", group_name="admin",
                                               user_pool_id=self.user_pool.user_pool_id, description="admin group")
        retailer_group = cognito.CfnUserPoolGroup(self, f"{c.env_state}-retailer-user-group", group_name="retailer",
                                                  user_pool_id=self.user_pool.user_pool_id,
                                                  description="retailer group")
        user_group = cognito.CfnUserPoolGroup(self, f"{c.env_state}-user-user-group", group_name="user",
                                              user_pool_id=self.user_pool.user_pool_id, description="user group")

        """create base api gateway"""
        self.api = apigwv2.HttpApi(self, f"{c.env_state}-be3-api")

        """create an admin iam role for lambda function"""
        self.admin_role = self.create_iam_role("be3-lambda-base-role")

        """lambda layers"""
        self.be3_lambda_layer = self.create_lambda_layer("be3-layer")

        """lambda function settings"""
        self.base_handler = self.create_lambda_handler(name="base-lambda")


        """add routes for mangum fastapi all routes"""
        self.api.add_routes(path="/{proxy+}", methods=[apigwv2.HttpMethod.ANY],
                            integration=HttpLambdaIntegration(f"{c.env_state}-be3 proxy integration",
                                                              self.base_handler))

        """output"""
        CfnOutput(self, f"{c.env_state}-api-url", value=self.api.api_endpoint)

    def create_lambda_handler(self, name: str) -> lambda_python.PythonFunction:
        """create a lambda function"""
        # look up the vpc
        self.vpc = ec2.Vpc.from_lookup(self, f"{c.env_state}-{name}-vpc", vpc_id=c.vpc_id)

        """subnets resources should use"""
        self.private_subnets = []
        for idx, subnet in enumerate(self.vpc.private_subnets):
            self.private_subnets.append(
                ec2.Subnet.from_subnet_id(self, f"{c.env_state}-{name}-private-subnet-{idx}", subnet.subnet_id))

        """base default security group"""
        self.security_group = ec2.SecurityGroup.from_security_group_id(
            self, f"{c.env_state}-{name}-security-group", security_group_id=c.vpc_security_group_id)

        return lambda_python.PythonFunction(
            self, f"{c.env_state}-{name}",
            function_name=f"{c.env_state}-{name}",
            entry="src", index="functions/apps.py",
            handler="handler",
            runtime=lambda_.Runtime.PYTHON_3_9,
            memory_size=512, timeout=Duration.minutes(1),
            layers=[self.be3_lambda_layer],
            role=self.admin_role, vpc=self.vpc,
            vpc_subnets=ec2.SubnetSelection(subnets=self.private_subnets),
            security_groups=[self.security_group]
        )

    def create_lambda_layer(self, name: str) -> lambda_python.PythonLayerVersion:
        """create a lambda layer for lambda function"""
        return lambda_python.PythonLayerVersion(
            self, f"{c.env_state}-{name}", entry="src/layer", compatible_runtimes=[lambda_.Runtime.PYTHON_3_9],
            layer_version_name=f"{c.env_state}-be3-lambda-base-layer")

    def create_cognito_user_pool(self, name: str) -> cognito.UserPool:
        """create a cognito user pool"""
        return cognito.UserPool(
            self, f"{c.env_state}-{name}",
            user_pool_name=f"{c.env_state}-{name}",
            sign_in_aliases=cognito.SignInAliases(email=True, username=True),
            self_sign_up_enabled=True,
            auto_verify=cognito.AutoVerifiedAttrs(email=True),
            user_verification=cognito.UserVerificationConfig(
                email_subject="You need to verify your email",
                email_body="Thanks for signing up Your verification code is {####}",
                email_style=cognito.VerificationEmailStyle.CODE
            ),
            standard_attributes={
                "email": cognito.StandardAttribute(required=True, mutable=True),
            },
            custom_attributes={
                "role": cognito.StringAttribute(mutable=True),
                "username": cognito.StringAttribute(mutable=False),
            },
            password_policy=cognito.PasswordPolicy(
                min_length=8, require_digits=True, require_lowercase=True, require_uppercase=True,
                require_symbols=True, temp_password_validity=Duration.days(3)
            ),
            account_recovery=cognito.AccountRecovery.EMAIL_ONLY,
            removal_policy=RemovalPolicy.DESTROY,
        )

    def create_cognito_user_pool_client(self, name: str) -> cognito.UserPoolClient:
        """create a cognito user pool client"""
        return self.user_pool.add_client(
            f"{c.env_state}-{name}", user_pool_client_name=f"{c.env_state}-{name}",
            auth_flows=cognito.AuthFlow(
                admin_user_password=True, user_password=True, user_srp=True, custom=True
            ),
            generate_secret=False, prevent_user_existence_errors=True,
            access_token_validity=Duration.days(1), id_token_validity=Duration.days(1),
            refresh_token_validity=Duration.days(60), auth_session_validity=Duration.minutes(15),
        )

    def create_table(self, name: str) -> dynamodb.Table:
        """create a dynamodb table with cdk"""
        return dynamodb.Table(
            self, f"{c.env_state}-{name}", table_name=f"{c.env_state}-be3-table",
            partition_key=dynamodb.Attribute(name="pk", type=dynamodb.AttributeType.STRING),
            sort_key=dynamodb.Attribute(name="sk", type=dynamodb.AttributeType.STRING),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY
        )

    def create_gsi(self, pk: str, index_name: str) -> None:
        """create a global secondary index for dynamodb table"""
        self.table.add_global_secondary_index(
            partition_key=dynamodb.Attribute(name=pk, type=dynamodb.AttributeType.STRING),
            index_name=index_name
        )

    def create_iam_role(self, name: str) -> iam.Role:
        """create an iam role for lambda function"""
        return iam.Role(
            self, f"{c.env_state}-{name}", assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            role_name=f"{c.env_state}-{name}", managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaBasicExecutionRole"),
                iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaVPCAccessExecutionRole"),
                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonDynamoDBFullAccess"),
            ])
