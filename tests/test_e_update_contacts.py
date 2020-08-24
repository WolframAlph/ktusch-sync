import random
from time import sleep

from tests.helpers import generate_contacts
from business.sync.contacts import Contact
from business.apis import Hubspot, Google
from tests import sync


class TestUpdateContacts:
    def test_update_contacts(self, hubspot_client, google_client):
        hubspot_contacts = hubspot_client.get_all_contacts()
        google_contacts = google_client.get_all_contacts()

        assert len(hubspot_contacts) == len(google_contacts)

        hubspot_contacts_to_update = random.sample(list(hubspot_contacts), k=random.randint(1, len(hubspot_contacts)))
        google_contacts_to_update = random.sample(list(google_contacts), k=random.randint(1, len(google_contacts)))

        for contact, updated_contact in zip(hubspot_contacts_to_update,
                                            generate_contacts(len(hubspot_contacts_to_update))):
            hubspot_client.update_contact(
                Contact(firstname=updated_contact['firstname'],
                        lastname=updated_contact['lastname'],
                        email=updated_contact['email'],
                        id_=contact.id,
                        source=Hubspot)
            )

        for contact, updated_contact in zip(google_contacts_to_update,
                                            generate_contacts(len(google_contacts_to_update))):
            google_client.update_contact(
                Contact(firstname=updated_contact['firstname'],
                        lastname=updated_contact['lastname'],
                        email=updated_contact['email'],
                        id_=contact.id,
                        source=Google)
            )
        sleep(20)
        sync.watch()
        sync.watch()
        sleep(20)

        updated_hubspot_contacts = sorted(hubspot_client.get_all_contacts(), key=lambda c: c.contact_hash)
        updated_google_contacts = sorted(google_client.get_all_contacts(), key=lambda c: c.contact_hash)

        assert len(updated_hubspot_contacts) == len(updated_google_contacts)
        print(updated_hubspot_contacts)
        print(updated_google_contacts)
        for google_contact, hubspot_contact in zip(updated_google_contacts, updated_hubspot_contacts):
            assert google_contact.contact_hash == hubspot_contact.contact_hash
