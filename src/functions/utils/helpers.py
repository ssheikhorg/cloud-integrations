import base64


def get_base64_string(string):
    """Encode a string to base64."""
    return base64.b64encode(string.encode("utf-8")).decode("utf-8")


def get_base64_decoded_string(string):
    """Decode a base64 string."""
    return base64.b64decode(string).decode("utf-8")
