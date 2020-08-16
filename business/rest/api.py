from functools import wraps
from multiprocessing import Process, Value

from flask import Flask, request
from flask_restful import Resource, Api

from business.sync.entrypoint import run


app = Flask(__name__)
api = Api(app)


def token_required(method):
    @wraps(method)
    def authenticate(*args, **kwargs):
        return method(*args, **kwargs)
    return authenticate


class GetSyncStatus(Resource):

    @token_required
    def get(self):
        return {'status': 'running' if running.value else 'stopped'}


class StartSync(Resource):

    @token_required
    def get(self):
        if not running.value:
            running.value = True
            start_sync_process()
            return {'status': 'started'}
        return {'status': 'already running'}


def start_sync_process():
    Process(target=run, args=(running,)).start()


api.add_resource(GetSyncStatus, '/getSyncStatus')
api.add_resource(StartSync, '/trigger')


if __name__ == '__main__':
    running = Value('b', True)
    start_sync_process()
    app.run(debug=False, host='0.0.0.0', port='5000')
