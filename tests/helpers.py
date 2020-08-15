import random
import string

from business.sync.interfaces import ContactsInterface


def random_string_generator(n):
    return ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(n))


def generate_contacts(count):
    contacts = []

    for _ in range(count):
        first_name = random_string_generator(10)
        last_name = random_string_generator(10)
        email = random_string_generator(10) + "@mail.com"
        contacts.append(dict(firstname=first_name, lastname=last_name, email=email))

    return contacts


def delete_all_contacts(client: ContactsInterface):
    old_contacts = client.get_all_contacts()
    for contact in old_contacts:
        client.delete_contact(contact.id)
