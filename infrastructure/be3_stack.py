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

from config import settings

LAMBDA_ASSET_PATH = str(Path(__file__).parent.parent.joinpath("api", "src"))
LAMBDA_LAYER_ASSET_PATH = str(Path(__file__).parent.parent.joinpath("api", "layers"))


class CdkStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # sign up lambda & lambda layer
        _sign_up_function = self._create_lambda_handler("CreateDataFunction", "app.sign_up")
        _sign_up_layer = self._create_lambda_layer("SignUpLayer", LAMBDA_LAYER_ASSET_PATH)
        _sign_up_function.add_layers(_sign_up_layer)

        _confirm_sign_up_function = self._create_lambda_handler("ConfirmSignUpFunction", "app.confirm_sign_up")
        _confirm_sign_up_layer = self._create_lambda_layer("ConfirmSignUpLayer", LAMBDA_LAYER_ASSET_PATH)
        _confirm_sign_up_function.add_layers(_confirm_sign_up_layer)

        _resend_confirmation_code_function = self._create_lambda_handler("ResendConfirmationCodeFunction", "app.resend_confirmation_code")
        _resend_confirmation_code_layer = self._create_lambda_layer("ResendConfirmationCodeLayer", LAMBDA_LAYER_ASSET_PATH)
        _resend_confirmation_code_function.add_layers(_resend_confirmation_code_layer)

        _forget_password_function = self._create_lambda_handler("ForgetPasswordFunction", "app.forget_password")
        _forget_password_layer = self._create_lambda_layer("ForgetPasswordLayer", LAMBDA_LAYER_ASSET_PATH)
        _forget_password_function.add_layers(_forget_password_layer)

        _reset_password_function = self._create_lambda_handler("ResetPasswordFunction", "app.reset_password")
        _reset_password_layer = self._create_lambda_layer("ResetPasswordLayer", LAMBDA_LAYER_ASSET_PATH)
        _reset_password_function.add_layers(_reset_password_layer)

        _confirm_reset_password_function = self._create_lambda_handler("ConfirmResetPasswordFunction", "app.confirm_reset_password")
        _confirm_reset_password_layer = self._create_lambda_layer("ConfirmResetPasswordLayer", LAMBDA_LAYER_ASSET_PATH)
        _confirm_reset_password_function.add_layers(_confirm_reset_password_layer)

        _sign_in_function = self._create_lambda_handler("SignInFunction", "app.sign_in")
        _sign_in_layer = self._create_lambda_layer("SignInLayer", LAMBDA_LAYER_ASSET_PATH)
        _sign_in_function.add_layers(_sign_in_layer)


        _authorizer = HttpUserPoolAuthorizer("UserPoolAuthorizer", pool=settings.user_pool_id,
                                            user_pool_clients=[settings.user_pool_client_id])

        _http_api = apigatewayv2.HttpApi(self, "Be3Api", default_authorizer=_authorizer)

        _http_api.add_routes(
            path="/data",
            methods=[apigatewayv2.HttpMethod.POST],
            integration=HttpLambdaIntegration(
                "CreateDataIntegration", _sign_up_function
            ),
        )

        CfnOutput(self, "OutputApiUrl", value=_http_api.url)

    # create lambda handler global function
    def _create_lambda_handler(self, name, handler):
        return lambda_.Function(
            self, name,
            code=lambda_.Code.from_asset(LAMBDA_ASSET_PATH),
            runtime=lambda_.Runtime.PYTHON_3_9,
            handler=handler,
            timeout=Duration.minutes(2),
        )

    # create global lambda layer
    def _create_lambda_layer(self, name, path):
        return lambda_.LayerVersion(
            self, name,
            code=lambda_.Code.from_asset(path),
            compatible_runtimes=[lambda_.Runtime.PYTHON_3_9],
            license="Apache-2.0",
            description="Global lambda layer",
        )
