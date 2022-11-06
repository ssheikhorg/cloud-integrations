import base64

# base64 encoded string
def get_base64_string(string):
    return base64.b64encode(string.encode("utf-8")).decode("utf-8")


# base64 decoded string
def get_base64_decoded_string(string):
    return base64.b64decode(string).decode("utf-8")