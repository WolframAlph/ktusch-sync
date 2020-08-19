from multiprocessing import Process
from datetime import timedelta
import os
import logging

from flask import Flask, request
from flask_restful import Resource, Api
from flask_cors import CORS

from business.sync.entrypoint import run
from business.rest.statuses import HTTP
from business.rest.authorization import token_required, encode_token
from business.database.database_interface import cursor


app = Flask(__name__)
api = Api(app)
CORS(app)
sync_process = Process(name='sync-process', target=run)


class Synchronization(Resource):

    @token_required
    def get(self):
        return {'alive': sync_process.is_alive()}

    @token_required
    def post(self):
        global sync_process
        sync_alive = sync_process.is_alive()

        if sync_alive:
            return {'status': 'already running'}

        sync_process = Process(name='sync-process', target=run)
        sync_process.start()
        return {'status': 'started'}

    @token_required
    def delete(self):
        if sync_process.is_alive():
            sync_process.terminate()
            logging.info('Synchronization suspended')
        return {'status': 'stopped'}


class Authorization(Resource):

    def get(self):
        # TODO move data to payload insted of query parameters
        user = request.args.get('user')
        password = request.args.get('password')
        if user == os.getenv('USERNAME') and password == os.getenv('PASSWORD'):
            return {'token': encode_token(expires_after=timedelta(minutes=15), user=user)}
        return {'message': 'Bad username or password'}, HTTP.BAD_REQUEST


class Contacts(Resource):

    @token_required
    def get(self):
        cursor.execute('select count(*) from contacts')
        return {'contacts': cursor.fetchone()[0]}


api.add_resource(Synchronization, '/synchronization')
api.add_resource(Authorization, '/authorization')
api.add_resource(Contacts, '/contacts')


if __name__ == '__main__':
    sync_process.start()
    app.run(debug=False, host='0.0.0.0', port='5000')
