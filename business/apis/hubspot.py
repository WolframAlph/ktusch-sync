import json

from business.sync.http_session import AuthHttpSession
from business.apis import Hubspot
from business.sync.contacts import Contact
from business.sync.interfaces import ContactsInterface


class HubspotApiInterface(Hubspot, ContactsInterface):
    props_to_extract = (
        'firstname',
        'lastname',
        'company',
        'email'
    )

    def __init__(self):
        self.http_session = AuthHttpSession(self)

    @staticmethod
    def extract_properties(contact_data):
        res = {}
        for prop in HubspotApiInterface.props_to_extract:
            res[prop] = contact_data['properties'][prop]['value'] if prop in contact_data['properties'] else None
        res["id_"] = contact_data["vid"]
        return res

    def get_all_contacts(self):
        has_more = True
        parameter_dict = {'count': 100}
        contact_list = set()

        while has_more:
            r = self.http_session.get(self.get_all_contacts_url + "?property=firstname&property=lastname&"
                                                                  "property=company&property=email",
                                      params=parameter_dict)
            response_dict = json.loads(r.text)
            has_more = response_dict['has-more']
            parameter_dict['vidOffset'] = response_dict['vid-offset']

            for contact_data in response_dict['contacts']:
                data = HubspotApiInterface.extract_properties(contact_data)
                contact_list.add(Contact(source=Hubspot, client=self, **data))

        return contact_list

    def create_contact(self, **kwargs):
        request_data = {"properties": [{"property": "firstname", "value": kwargs.get('firstname')},
                        {"property": "lastname", "value": kwargs.get('lastname')},
                        {"property": "email", "value": kwargs.get('email')}]}
        payload = json.dumps(request_data)
        response = self.http_session.post(self.create_contact_url, data=payload)

        return json.loads(response.text)['vid']

    def delete_contact(self, contact_id):
        r = self.http_session.delete(self.delete_contact_url.format(contact_id))
        return r.text

    def update_contact(self, contact: Contact):
        request_data = {"properties": [{"property": "firstname", "value": contact.firstname},
                                       {"property": "lastname", "value": contact.lastname},
                                       {"property": "email", "value": contact.email}]}
        payload = json.dumps(request_data)
        return self.http_session.post(self.update_contact_url.format(contact.id), data=payload)
