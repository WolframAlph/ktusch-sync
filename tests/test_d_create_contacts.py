import random
from time import sleep

import pytest

from apis.google import GoogleApiInterface
from apis.hubspot import HubspotApiInterface
from tests import sync
from tests.helpers import generate_contacts
from database.database_interface import cursor


class TestCreateContacts:

    @pytest.mark.parametrize('client', [HubspotApiInterface(), GoogleApiInterface()])
    def test_create_contacts(self, client):
        new_contacts = generate_contacts(random.randint(1, 10))
        contacts_ids = set()

        for contact in new_contacts:
            contact_id = client.create_contact(**contact)
            contacts_ids.add(contact_id)

        sleep(30)

        all_contacts = client.get_all_contacts()

        sync.watch()
        sleep(30)

        mirror_client = HubspotApiInterface() if isinstance(client, GoogleApiInterface) else GoogleApiInterface()
        mirrored_contacts = mirror_client.get_all_contacts()

        assert len(all_contacts) == len(mirrored_contacts)

        all_contacts_sorted = sorted(list(all_contacts), key=lambda c: c.contact_hash)
        mirrored_contacts_sorted = sorted(list(mirrored_contacts), key=lambda c: c.contact_hash)

        for contact, mirror_contact in zip(all_contacts_sorted, mirrored_contacts_sorted):
            assert contact.contact_hash == mirror_contact.contact_hash

        for contact_id in contacts_ids:
            assert any(contact_id == contact.id for contact in all_contacts)

        l = f"{mirror_client.name}_id"
        f = f"{client.name}_id"

        ids = ", ".join(f"'{contact_id}'" for contact_id in contacts_ids)
        cursor.execute(f'select {l} from contacts where {f} in ({ids})')
        mirror_ids = [n[0] for n in cursor.fetchall()]
        print(mirrored_contacts)
        print(mirror_ids)
        for contact_id in mirror_ids:
            assert any(contact_id == str(contact.id) for contact in mirrored_contacts)
