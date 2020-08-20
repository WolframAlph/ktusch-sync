import logging
import os
import psycopg2


connection = psycopg2.connect(user="postgres", password=os.getenv('DATABASE_PASSWORD'), host=os.getenv('HOST') or 'localhost',
                              port="5432" if os.getenv('HOST') else "5000")
cursor = connection.cursor()


def rollback_on_error(func):

    def rollback(*args, **kwargs):
        try:
            func(*args, **kwargs)
            connection.commit()
        except Exception as e:
            logging.exception(str(e))
            logging.info(f"Reverting all changes made in database for last transaction")
            connection.rollback()
            raise

    return rollback


def truncate_contacts():
    cursor.execute('truncate table contacts')
    connection.commit()


def insert_contact(row):
    logging.info(f'Inserting new contact with hubspot id: {row[0]} and google id {row[1]}')
    cursor.execute('insert into contacts(hubspot_id, google_id, contact_hash, first_name, last_name, email) '
                   'values (%s, %s, %s, %s, %s, %s)', row)


def exists(what, contact_id):
    if what == 'google':
        cursor.execute('select 1 from contacts where google_id = %(google_id)s', {'google_id': contact_id})
    else:
        cursor.execute('select 1 from contacts where hubspot_id = %(hubspot_id)s', {'hubspot_id': contact_id})
    return cursor.fetchall()


def get_missing_contacts(source, contacts_ids):
    id_type = 'google_id' if source == 'google' else 'hubspot_id'
    if not contacts_ids:
        statement = 'select hubspot_id, google_id from contacts'
    else:
        contacts_ids = ", ".join(f"'{contact_id}'" for contact_id in contacts_ids)
        statement = f'select hubspot_id, google_id from contacts where {id_type} not in ({contacts_ids})'
    cursor.execute(statement)
    return set([(n[0], n[1]) for n in cursor.fetchall()])


def delete_contact(source, contact_id):
    statement = f"delete from contacts where {source} = %s"
    cursor.execute(statement, (str(contact_id), ))


def update_contact(contact):
    target_id_label = contact.client.name + '_id'
    statement = f"insert into contacts(hubspot_id, google_id, contact_hash, first_name, last_name, email)" \
                f"values(%(hubspot_id)s, %(google_id)s, %(contact_hash)s, %(first_name)s, %(last_name)s, %(email)s) " \
                f"on conflict ({target_id_label}) do update set contact_hash = %(contact_hash)s, " \
                f"first_name = %(first_name)s, last_name = %(last_name)s, email = %(email)s"
    cursor.execute(statement, {
        'hubspot_id': contact.id,
        'google_id': contact.id,
        'contact_hash': contact.contact_hash,
        'first_name': contact.firstname,
        'last_name': contact.lastname,
        'email': contact.email
    })


def select_on_id(source, contact_id):
    statement = f"select hubspot_id, google_id, contact_hash from contacts where {source} = %s"
    cursor.execute(statement, (contact_id, ))
    return cursor.fetchone()
