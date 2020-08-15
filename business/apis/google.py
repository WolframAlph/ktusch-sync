import json

from business.apis import Google
from business.sync.contacts import Contact
from business.sync.interfaces import ContactsInterface
from business.sync.http_session import AuthHttpSession


class GoogleApiInterface(Google, ContactsInterface):
    props_to_extract = (
        "names",
        "organizations",
        "emailAddresses",
        "addresses",
        "phoneNumbers"
    )

    def __init__(self):
        self.http_session = AuthHttpSession(self)

    @staticmethod
    def extract_properties(contact_data):
        res = dict()
        res['firstname'] = contact_data['names'][0].get('givenName', '') if 'names' in contact_data and contact_data[
            'names'] else None
        res['lastname'] = contact_data['names'][0].get('familyName', '') if 'names' in contact_data and contact_data[
            'names'] else None
        res['email'] = contact_data['emailAddresses'][0].get('value', '') if 'emailAddresses' in contact_data and \
                                                                             contact_data['emailAddresses'] else None
        res['company'] = contact_data['organizations'][0].get('name', '') if 'organizations' in contact_data and \
                                                                             contact_data['organizations'] else None
        res['id_'] = contact_data['resourceName']
        return res

    def get_contact(self, contact_id):
        params = {'personFields': 'names'}
        return json.loads(self.http_session.get(f"https://people.googleapis.com/v1/{contact_id}", params=params).text)

    def create_contact(self, **kwargs):
        payload = json.dumps(
            {"names": [{"givenName": kwargs.get('firstname'),
                        "familyName": kwargs.get('lastname')}],
             "organizations": [{"name": kwargs.get('company')}],
             "emailAddresses": [{"value": kwargs.get('email')}]}
        )
        r = self.http_session.post(self.create_contact_url, data=payload)
        return json.loads(r.text)['resourceName']

    def get_all_contacts(self):
        contact_list = set()
        querystring = {"personFields": ",".join(GoogleApiInterface.props_to_extract)}
        next_page_token = '1'

        while next_page_token:
            resp = json.loads(self.http_session.get(self.get_all_contacts_url, params=querystring).text)
            next_page_token = resp.get('nextPageToken', '')
            querystring['pageToken'] = next_page_token

            for contact_data in resp.get('connections', []):
                data = GoogleApiInterface.extract_properties(contact_data)
                contact_list.add(Contact(source=Google, client=self, **data))
        return contact_list

    def delete_contact(self, contact_id):
        return json.loads(self.http_session.delete(self.delete_contact_url.format(contact_id)).text)

    def update_contact(self, contact):
        person_etag = self.get_contact(contact.id)['etag']
        payload = json.dumps({"resourceName": contact.id, "etag": person_etag,
                              "names": [{"givenName": contact.firstname,
                                         "familyName": contact.lastname}],
                              "emailAddresses": [{"value": contact.email}]})
        params = {'updatePersonFields': 'emailAddresses,names'}
        return self.http_session.patch(self.update_contact_url.format(contact.id), params=params, data=payload)
