from flask import jsonify
from werkzeug.http import HTTP_STATUS_CODES

from . import api_v1


class ValidationError(ValueError):
    def __init__(self, message="参数错误", *args):
        self.message = message
        super(ValidationError, self).__init__(*args)


@api_v1.errorhandler(ValidationError)
def validation_error(e):
    return api_abort(400, e.message)


def api_abort(code, message=None, **kwargs):
    if message is None:
        message = HTTP_STATUS_CODES.get(code, '')
    response = jsonify(code=code, message=message, **kwargs)
    response.status_code = code
    return response


def invalid_token():
    response = api_abort(400, error='invalid_token', error_description='Either the token was expired or invalid.')
    response.headers['WWW-Authenticate'] = 'Bearer'
    return response


def token_missing():
    response = api_abort(400)
    response.headers['WWW-Authenticate'] = 'Bearer'
    return response
