from time import sleep

from business.database.database_interface import cursor
from tests import sync


class TestMergeContacts:

    def test_merge_contacts(self, hubspot_client, google_client):

        hubspot_contacts = hubspot_client.get_all_contacts()
        google_contacts = google_client.get_all_contacts()

        sync.synchronize()

        cursor.execute('select count(*) from contacts')
        assert cursor.fetchall()[0][0] == len(hubspot_contacts) + len(google_contacts)

        sleep(20)

        synced_hubspot_contacts = hubspot_client.get_all_contacts()
        synced_google_contacts = google_client.get_all_contacts()

        assert len(synced_google_contacts) == len(synced_hubspot_contacts)

        for contact in google_contacts:
            assert any(contact.id == synced_contact.id for synced_contact in synced_google_contacts)

        for contact in hubspot_contacts:
            assert any(contact.id == synced_contact.id for synced_contact in synced_hubspot_contacts)

        synced_hubspot_contacts_sorted = sorted(list(synced_hubspot_contacts), key=lambda contact: contact.contact_hash)
        synced_google_contacts_sorted = sorted(list(synced_google_contacts), key=lambda contact: contact.contact_hash)

        for hubspot_contact, google_contact in zip(synced_hubspot_contacts_sorted, synced_google_contacts_sorted):
            assert hubspot_contact.contact_hash == google_contact.contact_hash

        cursor.execute('select count(*) from contacts')
        assert cursor.fetchall()[0][0] == len(synced_hubspot_contacts) == \
               len(synced_google_contacts) == len(hubspot_contacts) + len(google_contacts)
