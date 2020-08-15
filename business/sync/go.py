import logging

from business.database.database_interface import truncate_contacts, connection, rollback_on_error
from business.sync.contacts_controller import ContactsController


class Sync:
    synchronized = False

    def __init__(self):
        self.contacts_controller = ContactsController()

    @property
    def hubspot_client(self):
        return self.contacts_controller.hubspot_client

    @property
    def google_client(self):
        return self.contacts_controller.google_client

    @rollback_on_error
    def synchronize(self):
        truncate_contacts()
        self.contacts_controller.merge()
        Sync.synchronized = True

    @rollback_on_error
    def watch(self):
        google_contacts, hubspot_contacts = self.contacts_controller.pull()
        contacts_to_delete = self.contacts_controller.get_deleted_contacts(google_contacts, hubspot_contacts)
        contacts_to_create = self.contacts_controller.get_created_contacts(google_contacts, hubspot_contacts)
        contacts_to_update = self.contacts_controller.get_updated_contacts(google_contacts, hubspot_contacts)

        for contact in contacts_to_create:
            contact.mirror()

        # for contact in contacts_to_update:
        #     contact.update()

        for contact in contacts_to_delete:
            contact.delete_on_client()

    def run(self):
        logging.info('Running scheduled synchronization')
        if not Sync.synchronized:
            self.synchronize()
        else:
            self.watch()
