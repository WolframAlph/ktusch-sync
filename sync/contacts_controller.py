import logging

from apis.google import GoogleApiInterface
from apis.hubspot import HubspotApiInterface
from apis import Google, Hubspot
from database.database_interface import exists, get_missing_contacts, delete_contact

import itertools

from sync.contacts import Contact


class ContactsController:

    def __init__(self):
        self.google_client = GoogleApiInterface()
        self.hubspot_client = HubspotApiInterface()

    def pull(self):
        google_contacts = self.google_client.get_all_contacts()
        hubspot_contacts = self.hubspot_client.get_all_contacts()

        for contact in google_contacts:
            contact.mirror_client = self.hubspot_client

        for contact in hubspot_contacts:
            contact.mirror_client = self.google_client

        return google_contacts, hubspot_contacts

    def merge(self):
        google_contacts, hubspot_contacts = self.pull()

        hubspot_common_contacts = set()
        google_common_contacts = set()

        for hubspot_contact in hubspot_contacts:
            for google_contact in google_contacts:
                if hubspot_contact.contact_hash == google_contact.contact_hash:
                    hubspot_contact.save(google_contact.id)
                    hubspot_common_contacts.add(hubspot_contact)
                    google_common_contacts.add(google_contact)

        google_contacts_not_in_hubspot = google_contacts.difference(google_common_contacts)
        hubspot_contacts_not_in_google = hubspot_contacts.difference(hubspot_common_contacts)

        for contact in itertools.chain(google_contacts_not_in_hubspot, hubspot_contacts_not_in_google):
            contact.mirror()

    def get_deleted_contacts(self, google_contacts, hubspot_contacts):
        contacts_to_delete = set()

        google_contacts_missing_in_hubspot = get_missing_contacts('hubspot', [h.id for h in hubspot_contacts])
        hubspot_contacts_missing_in_google = get_missing_contacts('google', [g.id for g in google_contacts])

        deleted_from_all = google_contacts_missing_in_hubspot.intersection(hubspot_contacts_missing_in_google)

        for contact_data in deleted_from_all:
            hubspot_id, google_id = contact_data
            logging.info(f'Found contact which was deleted everywhere '
                         f'with google id: {google_id} and hubspot id: {hubspot_id}')
            delete_contact('hubspot_id', hubspot_id)
            google_contacts_missing_in_hubspot.remove(contact_data)
            hubspot_contacts_missing_in_google.remove(contact_data)

        for contact_data in google_contacts_missing_in_hubspot:
            hubspot_id, google_id = contact_data
            logging.info(f'Found missing contact in hubspot with google id: {google_id} and husbpot id: {hubspot_id}')
            contacts_to_delete.add(Contact(id_=google_id, source=Google, client=self.google_client,
                                           mirror_client=self.hubspot_client))

        for contact_data in hubspot_contacts_missing_in_google:
            hubspot_id, google_id = contact_data
            logging.info(f'Found missing contact in google with google id: {google_id} and husbpot id: {hubspot_id}')
            contacts_to_delete.add(Contact(id_=hubspot_id, source=Hubspot, client=self.hubspot_client,
                                           mirror_client=self.google_client))

        return contacts_to_delete

    def get_created_contacts(self, google_contacts, hubspot_contacts):
        new_contacts = set()

        for contact in hubspot_contacts:
            if not exists('hubspot', str(contact.id)):
                logging.info(f'Found new contact in hubspot account with id {contact.id}')
                new_contacts.add(Contact(id_=contact.id,
                                         source=Hubspot,
                                         client=self.hubspot_client,
                                         mirror_client=self.google_client,
                                         firstname=contact.firstname,
                                         lastname=contact.lastname,
                                         email=contact.email))

        for contact in google_contacts:
            if not exists('google', str(contact.id)):
                logging.info(f'Found new contact in google account with id {contact.id}')
                new_contacts.add(Contact(id_=contact.id,
                                         source=Google,
                                         client=self.google_client,
                                         mirror_client=self.hubspot_client,
                                         firstname=contact.firstname,
                                         lastname=contact.lastname,
                                         email=contact.email))

        return new_contacts

    def get_updated_contacts(self, google_contacts, hubspot_contacts):
        pass
