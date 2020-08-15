import os
import configparser
from sync.interfaces import Service


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


class Hubspot(Service):
    name = 'hubspot'
    domain = hubspot_config['domain']['url']
    endpoints = hubspot_config['endpoints']
    delete_contact_url = domain + endpoints['delete_contact']
    get_all_contacts_url = domain + endpoints['get_all_contacts']
    create_contact_url = domain + endpoints['create_contact']
    update_contact_url = domain + endpoints['update_contact']
