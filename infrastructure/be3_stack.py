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
        admin_group = cognito.CfnUserPoolGroup(self, f"admin-user-group-{c.env_state}", group_name="admin",
                                               user_pool_id=self.user_pool.user_pool_id, description="admin group")
        retailer_group = cognito.CfnUserPoolGroup(self, f"retailer-user-group-{c.env_state}", group_name="retailer",
                                                  user_pool_id=self.user_pool.user_pool_id,
                                                  description="retailer group")
        user_group = cognito.CfnUserPoolGroup(self, f"user-user-group-{c.env_state}", group_name="user",
                                              user_pool_id=self.user_pool.user_pool_id, description="user group")

        """create base api gateway"""
        self.api = apigwv2.HttpApi(self, f"be3-api-{c.env_state}")

        """create an admin iam role for lambda function"""
        self.admin_role = self.create_iam_role("be3-lambda-base-role")

        """lambda layers"""
        self.be3_lambda_layer = self.create_lambda_layer("be3-layer")

        """lambda function settings"""
        self.user_handler = self.create_lambda_handler(name="user-handler", handler="handler_user")
        self.user_handler.add_environment("USER_POOL_ID", self.user_pool.user_pool_id)
        self.user_handler.add_environment("USER_POOL_CLIENT_ID", self.user_pool_client.user_pool_client_id)

        self.idrive_handler = self.create_lambda_handler(name="idrive-handler", handler="handler_idrive")

        """add routes for mangum fastapi all routes"""
        self.api.add_routes(path="/{proxy+}", methods=[apigwv2.HttpMethod.ANY],
                            integration=HttpLambdaIntegration("Be3 proxy integration", self.user_handler))
        self.api.add_routes(path="/idrive/{proxy+}", methods=[apigwv2.HttpMethod.ANY],
                            integration=HttpLambdaIntegration("Be3 proxy integration", self.idrive_handler))

        """output"""
        CfnOutput(self, f"ApiUrl-{c.env_state}", value=self.api.api_endpoint)

    def create_lambda_handler(self, name: str, handler: str):
        """create a lambda function"""
        # look up the vpc
        self.vpc = ec2.Vpc.from_lookup(self, f"Vpc-{name}", vpc_id=c.vpc_id)

        """subnets resources should use"""
        self.private_subnets = []
        for idx, subnet in enumerate(self.vpc.private_subnets):
            self.private_subnets.append(ec2.Subnet.from_subnet_id(self, f"PrivateSubnet{idx}-{name}", subnet.subnet_id))

        """base default security group"""
        self.security_group = ec2.SecurityGroup.from_security_group_id(
            self, f"Be3SecurityGroup-{name}", security_group_id=c.vpc_security_group_id)

        return lambda_python.PythonFunction(
            self, f"{name}-{c.env_state}",
            function_name=f"{name}-{c.env_state}",
            entry="src", index="functions/lambdas.py",
            handler=handler,
            runtime=lambda_.Runtime.PYTHON_3_9,
            memory_size=512, timeout=Duration.minutes(1),
            layers=[self.be3_lambda_layer],
            role=self.admin_role, vpc=self.vpc,
            vpc_subnets=ec2.SubnetSelection(subnets=self.private_subnets),
            security_groups=[self.security_group]
        )

    def create_lambda_layer(self, name):
        """create a lambda layer for lambda function"""
        return lambda_python.PythonLayerVersion(
            self, f"{name}-{c.env_state}", entry="src/layer", compatible_runtimes=[lambda_.Runtime.PYTHON_3_9],
            layer_version_name=f"be3-lambda-base-layer-{c.env_state}")

    def create_cognito_user_pool(self, name):
        """create a cognito user pool"""
        return cognito.UserPool(
            self, f"{name}-{c.env_state}",
            user_pool_name=f"{name}-{c.env_state}",
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

    def create_cognito_user_pool_client(self, name):
        """create a cognito user pool client"""
        return self.user_pool.add_client(
            f"{name}-{c.env_state}", user_pool_client_name=f"{name}-{c.env_state}",
            auth_flows=cognito.AuthFlow(
                admin_user_password=True, user_password=True, user_srp=True, custom=True
            ),
            generate_secret=False, prevent_user_existence_errors=True,
            access_token_validity=Duration.days(1), id_token_validity=Duration.days(1),
            refresh_token_validity=Duration.days(60), auth_session_validity=Duration.minutes(15),
        )

    def create_table(self, name):
        """create a dynamodb table with cdk"""
        return dynamodb.Table(
            self, f"{name}-{c.env_state}", table_name=f"be3-table-{c.env_state}",
            partition_key=dynamodb.Attribute(name="pk", type=dynamodb.AttributeType.STRING),
            sort_key=dynamodb.Attribute(name="sk", type=dynamodb.AttributeType.STRING),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY
        )

    def create_gsi(self, pk, index_name):
        """create a global secondary index for dynamodb table"""
        self.table.add_global_secondary_index(
            partition_key=dynamodb.Attribute(name=pk, type=dynamodb.AttributeType.STRING),
            index_name=index_name
        )

    def create_iam_role(self, name):
        """create an iam role for lambda function"""
        return iam.Role(
            self, "AdminRole", assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            role_name=f"{name}-{c.env_state}", managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaBasicExecutionRole"),
                iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaVPCAccessExecutionRole"),
                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonDynamoDBFullAccess"),
            ])
