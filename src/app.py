import json

from src import user


# lambda handler for without cognito
def lambda_handler(event, context):
    # create dict mapping of event path to function
    path_to_function = {
        "/user/signup": user.sign_up,
        "/user/login": user.login,
        "/user/confirm": user.confirm_sign_up
        "/user/reset": user.reset_password,
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
