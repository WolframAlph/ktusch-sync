from functools import wraps
from multiprocessing import Process
from datetime import datetime, timedelta
import os
import logging

from flask import Flask, request
from flask_restful import Resource, Api
from flask_cors import CORS

from business.sync.entrypoint import run
import jwt

app = Flask(__name__)
CORS(app)
api = Api(app)
sync_process = Process(name='sync-process', target=run)


def token_required(method):

    @wraps(method)
    def authenticate(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return {'message': 'Missing token'}, 401

        try:
            jwt.decode(token, 'secret')
        except jwt.exceptions.InvalidSignatureError:
            return {'message': 'Invalid token'}, 401

        except jwt.exceptions.ExpiredSignatureError:
            return {'message': 'Token expired'}, 401

        return method(*args, **kwargs), 200

    return authenticate


class GetSyncStatus(Resource):

    @token_required
    def get(self):
        return {'alive': sync_process.is_alive()}


class StartSync(Resource):

    @token_required
    def get(self):
        global sync_process
        sync_alive = sync_process.is_alive()

        if sync_alive:
            return {'status': 'already running'}

        sync_process = Process(name='sync-process', target=run)
        sync_process.start()
        return {'status': 'started'}


class StopSync(Resource):

    @token_required
    def post(self):
        if sync_process.is_alive():
            sync_process.terminate()
            logging.info('Synchronization suspended')
        return {'status': 'stopped'}


class Authorization(Resource):

    def get(self):
        user = request.args.get('user')
        password = request.args.get('password')
        if user == os.getenv('USERNAME') and password == os.getenv('PASSWORD'):
            return {'token': jwt.encode({'user': user,
                                         'exp': datetime.utcnow() + timedelta(minutes=15)}, 'secret').decode('UTF-8')}
        return {'message': 'Bad username or password'}, 400


api.add_resource(GetSyncStatus, '/status')
api.add_resource(StartSync, '/start')
api.add_resource(Authorization, '/authorization')
api.add_resource(StopSync, '/stop')


if __name__ == '__main__':
    sync_process.start()
    app.run(debug=False, host='0.0.0.0', port='5000')
