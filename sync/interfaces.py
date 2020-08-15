from abc import ABC, abstractmethod


class ContactsInterface(ABC):
    props_to_extract = ()

    @abstractmethod
    def get_all_contacts(self):
        pass

    @abstractmethod
    def create_contact(self, **kwargs):
        pass

    @abstractmethod
    def delete_contact(self, contact_id):
        pass

    @abstractmethod
    def update_contact(self, contact_id):
        pass


class Service(ABC):
    name = None
    get_all_contacts_url = None
    create_contact_url = None
    delete_contact_url = None
    update_contact_url = None
