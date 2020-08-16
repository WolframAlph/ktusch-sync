from functools import wraps
from multiprocessing import Process

from flask import Flask
from flask_restful import Resource, Api

from business.sync.entrypoint import run


app = Flask(__name__)
api = Api(app)
sync_process = Process(name='sync-process', target=run)


def token_required(method):
    @wraps(method)
    def authenticate(*args, **kwargs):
        return method(*args, **kwargs)
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


api.add_resource(GetSyncStatus, '/getSyncStatus')
api.add_resource(StartSync, '/trigger')


if __name__ == '__main__':
    sync_process.start()
    app.run(debug=False, host='0.0.0.0', port='5000')
