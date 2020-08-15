import logging
import os
import psycopg2


connection = psycopg2.connect(user="postgres", password=os.getenv('DATABASE_PASSWORD'), host=os.getenv('HOST'),
                              port="5432")
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
