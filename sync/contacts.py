import hashlib
import logging

from apis import Hubspot
from database.database_interface import insert_contact, delete_contact
from sync.interfaces import ContactsInterface


class Contact:

    def __init__(self, id_, source, firstname='', lastname='', email='', company='',
                 client: ContactsInterface = None, mirror_client: ContactsInterface = None):
        self.id = id_
        self.firstname = firstname
        self.lastname = lastname
        self.email = email
        self.company = company
        self.client = client
        self.mirror_client = mirror_client
        self.source = source

    @property
    def contact_hash(self):
        concatenated_data = self.firstname or '' + self.lastname or '' + self.email or ''
        return hashlib.sha3_224(bytes(concatenated_data.encode('UTF-8'))).hexdigest()

    def mirror(self):
        logging.info(f'Found {self.client.name} contact missing '
                     f'in {self.mirror_client.name} with {self.client.name} id: {self.id}')
        logging.info(f'Creating contact in {self.mirror_client.name}')
        mirror_id = self.mirror_client.create_contact(firstname=self.firstname,
                                                      lastname=self.lastname,
                                                      email=self.email,
                                                      company=self.company)
        logging.info(f'Created contact in {self.mirror_client.name} with id: {mirror_id}')
        self.save(mirror_id)

    def save(self, mirror_id):
        contact_data = (mirror_id if self.source is not Hubspot else self.id,
                        mirror_id if self.source is Hubspot else self.id,
                        self.contact_hash,
                        self.firstname,
                        self.lastname,
                        self.email)
        insert_contact(contact_data)

    def update(self):
        pass

    def delete_on_client(self):
        logging.info(f'Deleting {self.client.name} contact with {self.client.name} id: {self.id}')
        response = self.client.delete_contact(self.id)
        logging.info(response)
        logging.info(f'Successfuly deleted contact with {self.client.name} id: {self.id} from {self.client.name}')
        logging.info(f'Deleting contact with {self.client.name} id: {self.id} from database')
        delete_contact(self.client.name + '_id', self.id)
        logging.info(f'Successfuly deleted contact with {self.client.name} id: {self.id} from database')

    def __repr__(self):
        return f"Contact({self.id}, {self.firstname}, {self.lastname}, {self.email}, {self.contact_hash}, {self.source}"
