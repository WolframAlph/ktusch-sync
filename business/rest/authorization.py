from functools import wraps
from datetime import datetime

import jwt
from flask import request

from business.rest.statuses import HTTP


def token_required(method):

    @wraps(method)
    def authenticate(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return {'message': 'Missing token'}, HTTP.NOT_AUTHORIZED

        try:
            # TODO set secret as environment variable
            jwt.decode(token, 'secret')
        except jwt.exceptions.InvalidSignatureError:
            return {'message': 'Invalid token'}, HTTP.NOT_AUTHORIZED

        except jwt.exceptions.ExpiredSignatureError:
            return {'message': 'Token expired'}, HTTP.NOT_AUTHORIZED

        return method(*args, **kwargs), HTTP.SUCCESS

    return authenticate


def encode_token(expires_after, **data):
    return jwt.encode({'exp': datetime.utcnow() + expires_after, **data}, 'secret').decode('UTF-8')
