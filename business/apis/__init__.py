import os
import configparser
from functools import wraps
import logging

from google.auth.transport.requests import Request

from business.sync.interfaces import Service
from business.sync.auth import OAuth


GOOGLE_CONFIG = os.path.abspath(os.path.join(os.path.dirname(__file__), '../config/google.cfg'))
HUBSPOT_CONFIG = os.path.abspath(os.path.join(os.path.dirname(__file__), '../config/hubspot.cfg'))

google_config = configparser.ConfigParser()
hubspot_config = configparser.ConfigParser()

google_config.read(GOOGLE_CONFIG)
hubspot_config.read(HUBSPOT_CONFIG)


class Google(Service):
    name = 'google'
    domain = google_config['domain']['url']
    endpoints = google_config['endpoints']
    get_all_contacts_url = domain + endpoints['get_all_contacts']
    delete_contact_url = domain + endpoints['delete_contact']
    create_contact_url = domain + endpoints['create_contact']
    update_contact_url = domain + endpoints['update_contact']

    def __init__(self):
        self.credentials = OAuth().credentials

    def keep_token_alive(self, http_session, method):
        @wraps(method)
        def wrapper(*args, **kwargs):
            if self.credentials.expired:
                logging.info('Google credentials expired, fetching refresh token')
                self.credentials.refresh(Request())
                http_session.update_token(self.credentials.token)
            return method(*args, **kwargs)
        return wrapper

    def authenticate(self, http_session):
        http_session.request = self.keep_token_alive(http_session, http_session.request)


class Hubspot(Service):
    name = 'hubspot'
    domain = hubspot_config['domain']['url']
    endpoints = hubspot_config['endpoints']
    delete_contact_url = domain + endpoints['delete_contact']
    get_all_contacts_url = domain + endpoints['get_all_contacts']
    create_contact_url = domain + endpoints['create_contact']
    update_contact_url = domain + endpoints['update_contact']

    def authenticate(self, http_session):
        http_session.params.update({'hapikey': os.getenv('HUBSPOT_API_KEY')})
