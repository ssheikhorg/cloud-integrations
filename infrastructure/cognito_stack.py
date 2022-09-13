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
from aws_cdk.aws_apigatewayv2_authorizers_alpha import HttpUserPoolAuthorizer as _authorizer

from config import settings


class CognitoStack(Stack):
    def __init__(
            self,
            scope: Construct,
            construct_id: str,
            **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.user_pool = _cognito.UserPool(
            self, "be3_user_pool",
            user_pool_name="be3_user_pool",
            self_sign_up_enabled=True,
            standard_attributes=_cognito.StandardAttributes(
                email=_cognito.StandardAttribute(required=True, mutable=True),
                phone_number=_cognito.StandardAttribute(required=False)
            ),
            auto_verify=_cognito.AutoVerifiedAttrs(email=True),
            sign_in_case_sensitive=False,
            sign_in_aliases=_cognito.SignInAliases(email=True, phone=False, username=False),
            account_recovery=_cognito.AccountRecovery.EMAIL_ONLY,
            password_policy=_cognito.PasswordPolicy(
                min_length=8,
                require_digits=True,
                require_lowercase=True,
                require_uppercase=True,
                require_symbols=False
            ),
            user_invitation=_cognito.UserInvitationConfig(
                email_subject="Welcome to be3",
                email_body="Your username is {username} and temporary password is {####}"
            ),
            removal_policy=RemovalPolicy.DESTROY
        )
        self.user_pool_domain = self.user_pool.add_domain(
            "be3_user_pool_domain",
            cognito_domain=_cognito.CognitoDomainOptions(domain_prefix="be3-cdk")
        )
        self.user_pool_client: _cognito.UserPoolClient = self.user_pool.add_client(
            "be3_user_pool_client",
            auth_flows=_cognito.AuthFlow(
                user_password=True,
                user_srp=True,
                admin_user_password=True,
                custom=True
            ),
            prevent_user_existence_errors=True,
            o_auth=_cognito.OAuthSettings(
                flows=_cognito.OAuthFlows(
                    implicit_code_grant=True,
                ),
                scopes=[_cognito.OAuthScope.EMAIL, _cognito.OAuthScope.OPENID, _cognito.OAuthScope.PROFILE],
                callback_urls=[settings.cognito_cb_url],
                logout_urls=[settings.cognito_logout_url]
            )
        )

        self.user_pool.add_resource_server(
            "be3_user_pool_resource_server",
            identifier="be3_user_pool_resource_server",
            scopes=[
                _cognito.ResourceServerScope(
                    scope_name="admin",
                    scope_description="Gives the user elevated access for their organization."
                ),
                _cognito.ResourceServerScope(
                    scope_name="user",
                    scope_description="Gives the user access to their own data."
                )
            ]
        )

        openid_connect_iam_provider = _iam.OpenIdConnectProvider(
            self, "be3_openid_connect_provider",
            url=self.user_pool.user_pool_provider_url,
            client_ids=[self.user_pool_client.user_pool_client_id]
        )

        self.be3_role_assumed_by_cognito_users = _iam.Role(
            self, "be3_role_assumed_by_cognito_users",
            assumed_by=_iam.FederatedPrincipal(
                federated=openid_connect_iam_provider.open_id_connect_provider_arn,
                assume_role_action="sts:AssumeRoleWithWebIdentity",
                conditions={
                    "StringEquals": {
                        "cognito-identity.amazonaws.com:aud": self.user_pool.user_pool_id,
                    },
                    "ForAnyValue:StringLike": {
                        "cognito-identity.amazonaws.com:amr": "unauthenticated"
                    },
                },
            ),
        )

        self.be3_role_assumed_by_cognito_users.attach_inline_policy(
            policy=_iam.Policy(
                self,
                "read-quicksight-embed-url-policy",
                document=_iam.PolicyDocument(
                    statements=[
                        _iam.PolicyStatement(
                            actions=["quicksight:GetDashboardEmbedUrl"],
                            resources=["*"],
                            effect=_iam.Effect.ALLOW,
                        )
                    ]
                ),
            )
        )

        CfnOutput(
            self, "user-pool-id",
            value=self.user_pool.user_pool_id,
            export_name="user-pool-id",
            description="The ID of the Cognito User Pool"
        )
        CfnOutput(
            scope=self,
            id="user-pool-web-client-id",
            value=self.user_pool_client.user_pool_client_id,
            description="ID of the user pool web client.",
            export_name="user-pool-web-client-id",
        )
        CfnOutput(
            scope=self,
            id="hosted-ui-base-url",
            value=self.user_pool_domain.base_url(),
            description="Base URL of the Hosted UI.",
            export_name="hosted-ui-fqdn",
        )
        CfnOutput(
            scope=self,
            id="hosted-ui-signin-url",
            value=self.user_pool_domain.sign_in_url(
                client=self.user_pool_client, redirect_uri=embed_sample_route_url
            ),
            description="Sign in URL of the Hosted UI.",
            export_name="hosted-ui-signin-url",
        )
