import random

from tests import sync
from time import sleep
from business.database.database_interface import cursor


class TestDeleteContact:

    def test_delete_contacts(self, hubspot_client, google_client):

        hubspot_contacts = hubspot_client.get_all_contacts()
        google_contacts = google_client.get_all_contacts()

        assert len(hubspot_contacts) == len(google_contacts)

        hubspot_contacts_to_delete = random.sample(list(hubspot_contacts), k=random.randint(1, len(hubspot_contacts)))
        google_contacts_to_delete = random.sample(list(google_contacts), k=random.randint(1, len(google_contacts)))

        h = ", ".join(f"'{contact.id}'" for contact in hubspot_contacts_to_delete)
        g = ", ".join(f"'{contact.id}'" for contact in google_contacts_to_delete)

        cursor.execute(f"select google_id from contacts where hubspot_id in ({h})")
        google_contacts_ids_for_deleted_in_hubspot = [n[0] for n in cursor.fetchall()]

        cursor.execute(f"select hubspot_id from contacts where google_id in ({g})")
        hubspot_ids_for_deleted_in_google = [n[0] for n in cursor.fetchall()]

        for contact in hubspot_contacts_to_delete:
            hubspot_client.delete_contact(contact.id)

        for contact in google_contacts_to_delete:
            google_client.delete_contact(contact.id)

        sleep(20)
        sync.watch()
        sleep(20)

        updated_hubspot_contacts = hubspot_client.get_all_contacts()
        updated_google_contacts = google_client.get_all_contacts()

        assert len(updated_google_contacts) != len(google_contacts)
        assert len(updated_hubspot_contacts) != len(hubspot_contacts)
        assert len(updated_hubspot_contacts) == len(updated_google_contacts)

        updated_hubspot_contacts_sorted = sorted(list(updated_hubspot_contacts),
                                                 key=lambda contact: contact.contact_hash)
        updated_google_contacts_sorted = sorted(list(updated_google_contacts), key=lambda contact: contact.contact_hash)

        for hubspot_contact, google_contact in zip(updated_hubspot_contacts_sorted, updated_google_contacts_sorted):
            assert hubspot_contact.contact_hash == google_contact.contact_hash

        for contact_id in google_contacts_ids_for_deleted_in_hubspot:
            assert not any(contact_id == contact.id for contact in updated_google_contacts)

        for contact_id in hubspot_ids_for_deleted_in_google:
            assert not any(contact_id == contact.id for contact in updated_hubspot_contacts)

        cursor.execute(f'select 1 from contacts where hubspot_id in ({h})')
        assert not cursor.fetchall()

        cursor.execute(f'select 1 from contacts where google_id in ({g})')
        assert not cursor.fetchall()

        cursor.execute('select count(*) from contacts')
        assert cursor.fetchall()[0][0] == len(updated_google_contacts) == len(updated_hubspot_contacts)
