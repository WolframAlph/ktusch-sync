class TestCreateContacts:

    def test_insert_contacts(self, created_contacts: dict):
        all_contacts, created_ids = created_contacts['all_contacts'], created_contacts['created_contacts_ids']
        assert len(all_contacts) == len(created_ids)

        contacts_sorted = sorted(list(all_contacts), key=lambda contact: contact.id)
        for contact_id, client_contact_id in zip(sorted(created_ids), contacts_sorted):
            assert contact_id == client_contact_id.id
