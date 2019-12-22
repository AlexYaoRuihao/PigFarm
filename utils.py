from flask import make_response

def json_response(data = "", status = 200, headers = None):
    headers = headers or {}
    return make_response(data, status, headers)