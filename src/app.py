import json
from user import module


def handler(event, context):
    print("Received event: " + json.dumps(event, indent=2))
    # create dict mapping of event path to function
    path_to_function = {
        "/user/signup": module.cognito_signup,
        "/user/signup-confirm": module.cognito_confirm_signup,
        "/user/resend-confirmation-code": module.cognito_resend_confirmation_code,
        "/user/login": module.cognito_sign_in,
        # admin sign in
        "/user/admin-login": module.cognito_admin_sign_in,
        "/user/forgot-password": module.cognito_forgot_password,
        "/user/confirm-forgot-password": module.cognito_confirm_forgot_password,
        # endpoints with auth
        "/users": module.cognito_get_user,
        "/user/change-password": module.cognito_change_password,
        "/user/sign-out": module.cognito_sign_out,
        "/user/delete": module.cognito_delete_user,
    }
    # get the function from the path
    func = path_to_function.get(event["path"])
    # if function is not found return 404
    if not func:
        return {
            "statusCode": 404,
            "body": json.dumps({
                "error": True,
                "success": False,
                "message": "Not Found",
                "data": None
            })
        }
    # call the function with event and context
    return func(event, context)
