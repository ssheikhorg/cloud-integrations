def get_success(data, status_code=200):
    return {"status": "success", "data": data, "status_code": status_code}


def get_error(msg, status_code=400):
    return {"status": "error", "msg": msg, "status_code": status_code}


def get_not_found(msg, status_code=404):
    return {"status": "error", "msg": msg, "status_code": status_code}


def get_server_error(msg, status_code=500):
    return {"status": "error", "msg": msg, "status_code": status_code}
