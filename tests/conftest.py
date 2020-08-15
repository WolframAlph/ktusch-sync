import pytest
import random
from time import sleep
import os.path

from tests import sync
from apis.hubspot import HubspotApiInterface
from tests.helpers import delete_all_contacts, generate_contacts
from apis.google import GoogleApiInterface


@pytest.fixture(scope='module')
def hubspot_client():
    return sync.hubspot_client


@pytest.fixture(scope='module')
def google_client():
    return sync.google_client


@pytest.fixture(scope='module', params=[GoogleApiInterface(), HubspotApiInterface()])
def created_contacts(request):
    client = request.param
    delete_all_contacts(client)
    new_contacts = generate_contacts(random.randint(1, 10))
    created_ids = set()

    for contact in new_contacts:
        contact_id = client.create_contact(**contact)
        created_ids.add(contact_id)

    sleep(15)
    all_contacts = client.get_all_contacts()
    return {
        "all_contacts": all_contacts,
        "created_contacts_ids": created_ids
    }
