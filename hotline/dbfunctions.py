import sqlite3
import os
import datetime
import operator
import logging

DB_PATH = None

CONFIGURATION_FIELDS = {
    'mac_address': {'editable': True, 'validator': None},
    'username': {'editable': True, 'validator': None},
    'ipv4_address': {'editable': True, 'validator': None},
    'ipv6_address': {'editable': True, 'validator': None},
    'inbox_port': {'editable': True, 'validator': None},
    'ftp_port': {'editable': True, 'validator': None},
    'ftp_banner': {'editable': True, 'validator': None},
    'ftp_max_connections': {'editable': True, 'validator': None},
    'ftp_max_connections_per_ip': {'editable': True, 'validator': None},
    'ftp_folder': {'editable': True, 'validator': None},
    'ftp_users_can_upload_files': {'editable': True, 'validator': None},
    'interlocutor_address': {'editable': True, 'validator': None},
    'interlocutor_port': {'editable': True, 'validator': None},
    'interlocutor_password': {'editable': True, 'validator': None},
    'get_only_by_mac': {'editable': True, 'validator': None}
}

CONTACT_FIELDS = {
    'mac_address': {'editable': False, 'validator': None},
    'name': {'editable': True, 'validator': None},
    'ipv4_address': {'editable': True, 'validator': None},
    'ipv6_address': {'editable': True, 'validator': None},
    'inbox_port': {'editable': True, 'validator': None},
    'ftp_port': {'editable': True, 'validator': None}
}

SENT_MESSAGE_FIELDS = {
    'sent_timestamp': {'editable': False, 'validator': None},
    'receiver_contact': {'editable': True, 'validator': None},
    'content': {'editable': True, 'validator': None},
    'received_timestamp': {'editable': True, 'validator': None}
}

RECEIVED_MESSAGE_FIELDS = {
    'received_timestamp': {'editable': False, 'validator': None},
    'sender_contact': {'editable': True, 'validator': None},
    'content': {'editable': True, 'validator': None},
    'sent_timestamp': {'editable': True, 'validator': None}
}


def unwrap_get_configuration(function):
    def configuration_unwrapper(*args):
        len_args = len(args)
        if len_args < 2:
            raise TypeError(f'get_configuration() takes at least 2 arguments ({len_args} given)')
        dict_of_fields = function(*args)
        if len(dict_of_fields) == 1:
            return dict_of_fields.popitem()[1]

        values = [dict_of_fields.get(field) for field in args[1:]]
        return values

    return configuration_unwrapper


def unwrap_get_contact(function):
    def contact_unwrapper(*args, **kwargs):
        len_args = len(args)
        if len_args < 3:
            raise TypeError(f'get_contact() takes at least 3 arguments ({len_args} given)')
        dict_of_fields = function(*args, **kwargs)
        if len(dict_of_fields) == 1:
            return dict_of_fields.popitem()[1]

        values = [dict_of_fields.get(field) for field in args[2:]]
        return values

    return contact_unwrapper


def unwrap_get_sent_message(function):
    def sent_message_unwrapper(*args, **kwargs):
        len_args = len(args)
        if len_args < 3:
            raise TypeError(f'get_sent_message() takes at least 3 arguments ({len_args} given)')
        dict_of_fields = function(*args, **kwargs)
        if len(dict_of_fields) == 1:
            return dict_of_fields.popitem()[1]

        values = [dict_of_fields.get(field) for field in args[2:]]
        return values

    return sent_message_unwrapper


def unwrap_get_received_message(function):
    def received_message_unwrapper(*args, **kwargs):
        len_args = len(args)
        if len_args < 3:
            raise TypeError(f'get_received_message() takes at least 3 arguments ({len_args} given)')
        dict_of_fields = function(*args, **kwargs)
        if len(dict_of_fields) == 1:
            return dict_of_fields.popitem()[1]

        values = [dict_of_fields.get(field) for field in args[2:]]
        return values

    return received_message_unwrapper


def update_configuration(conn: sqlite3.Connection, **kwargs):
    fields = [*filter(lambda f: f in CONFIGURATION_FIELDS and CONFIGURATION_FIELDS[f]['editable'], kwargs)]
    if fields:
        values = [kwargs[field] for field in fields]
        statement = f"UPDATE Configuration SET {'= ?, '.join(fields)} = ?"
        with conn:
            conn.execute(statement, values)


@unwrap_get_configuration
def get_configuration(conn: sqlite3.Connection, *args):
    fields = [*filter(lambda f: f in CONFIGURATION_FIELDS, args)]
    if fields:
        with conn:
            statement = (f"SELECT {', '.join(fields)} FROM Configuration")
            values = conn.execute(statement).fetchone()
        return dict(zip(fields, values))


def insert_contact(conn: sqlite3.Connection, mac_address, name='Muhammad', ipv4_address='', ipv6_address='',
                   inbox_port=42000, ftp_port=21):
    statement = 'INSERT INTO Contact(mac_address, name, ipv4_address, ipv6_address, inbox_port, ftp_port) ' \
                'VALUES (?, ?, ?, ?, ?, ?)'
    with conn:
        conn.execute(statement, (mac_address, name, ipv4_address, ipv6_address, inbox_port, ftp_port))


def update_contact(conn: sqlite3.Connection, mac_address, **kwargs):
    fields = [*filter(lambda f: f in CONTACT_FIELDS and CONTACT_FIELDS[f]['editable'], kwargs)]
    if fields:
        values = [kwargs[field] for field in fields]
        values.append(mac_address)
        statement = f"UPDATE Contact SET {'= ?, '.join(fields)} = ? WHERE mac_address = ?"
        with conn:
            conn.execute(statement, values)


def delete_contact(conn: sqlite3.Connection, mac_address):
    with conn:
        conn.execute('DELETE FROM Contact WHERE mac_address = ?', (mac_address,))


@unwrap_get_contact
def get_contact(conn: sqlite3.Connection, mac_address, *args):
    fields = [*filter(lambda f: f in CONTACT_FIELDS, args)]
    if fields:
        with conn:
            statement = f"SELECT {', '.join(fields)} FROM Contact WHERE mac_address = ?"
            values = conn.execute(statement, (mac_address,)).fetchone()
            if not values:
                raise sqlite3.Error(f"The Contact with the mac_address '{mac_address}' does not exist")
        return dict(zip(fields, values))


def contacts(conn: sqlite3.Connection, mac_address=None):
    with conn:
        return conn.execute(
            'SELECT mac_address, name, ipv4_address, ipv6_address, inbox_port, ftp_port FROM Contact ORDER BY name ASC').fetchall()


def last_sent_messages(conn: sqlite3.Connection, limit=10):
    statement = 'SELECT DISTINCT MAX(sent_timestamp), receiver_contact, name FROM SentMessage, Contact WHERE receiver_contact = mac_address GROUP BY receiver_contact ORDER BY sent_timestamp DESC LIMIT ?;'
    with conn:
        return conn.execute(statement, (limit,)).fetchall()


def last_sent_messages_to_contact(conn: sqlite3.Connection, mac_address, limit=10):
    statement = 'SELECT sent_timestamp, received_timestamp, receiver_contact, name, content FROM SentMessage, Contact WHERE receiver_contact = ? AND receiver_contact = mac_address ORDER BY sent_timestamp DESC LIMIT ?;'
    with conn:
        return conn.execute(statement, (mac_address, limit))


def insert_sent_message(conn: sqlite3.Connection, sent_timestamp, receiver_contact, content, received_timestamp):
    statement = 'INSERT INTO SentMessage(sent_timestamp, receiver_contact, content, received_timestamp) ' \
                'VALUES (?, ?, ?, ?)'
    with conn:
        conn.execute(statement, (sent_timestamp, receiver_contact, content, received_timestamp))


def update_sent_message(conn: sqlite3.Connection, sent_timestamp, **kwargs):
    fields = [*filter(lambda f: f in SENT_MESSAGE_FIELDS and SENT_MESSAGE_FIELDS[f]['editable'], kwargs)]
    if fields:
        values = [kwargs[field] for field in fields]
        values.append(sent_timestamp)
        statement = f"UPDATE SentMessage SET {'= ?, '.join(fields)} = ? WHERE sent_timestamp = ?"
        with conn:
            conn.execute(statement, values)


def delete_sent_message(conn: sqlite3.Connection, sent_timestamp):
    with conn:
        conn.execute('DELETE FROM SentMessage WHERE sent_timestamp = ?', (sent_timestamp,))


@unwrap_get_sent_message
def get_sent_message(conn: sqlite3.Connection, sent_timestamp, *args):
    fields = [*filter(lambda f: f in SENT_MESSAGE_FIELDS, args)]
    if fields:
        with conn:
            statement = (f"SELECT {', '.join(fields)} FROM SentMessage WHERE sent_timestamp = ?")
            values = conn.execute(statement, (sent_timestamp,)).fetchone()
            if not values:
                raise sqlite3.Error(f"The SentMessage with the sent_timestamp '{sent_timestamp}' does not exist")
        return dict(zip(fields, values))


def sent_messages(conn: sqlite3.Connection):
    with conn:
        return conn.execute(
            'SELECT sent_timestamp, receiver_contact, content, received_timestamp FROM SentMessage ORDER BY sent_timestamp DESC').fetchall()


def insert_received_message(conn: sqlite3.Connection, received_timestamp, sender_contact, content, sent_timestamp):
    statement = 'INSERT INTO ReceivedMessage(received_timestamp, sender_contact, content, sent_timestamp) ' \
                'VALUES (?, ?, ?, ?)'
    with conn:
        conn.execute(statement, (received_timestamp, sender_contact, content, sent_timestamp))


def last_received_messages(conn: sqlite3.Connection, limit=10):
    # Use of distinc, max and group by to get the last n messages
    statement = 'SELECT DISTINCT MAX(received_timestamp), sender_contact, name FROM ReceivedMessage, Contact WHERE sender_contact = mac_address GROUP BY sender_contact ORDER BY received_timestamp DESC LIMIT ?'
    with conn:
        return conn.execute(statement, (limit,)).fetchall()


def last_received_messages_from_contact(conn: sqlite3.Connection, mac_address, limit=10):
    statement = 'SELECT received_timestamp, sent_timestamp, sender_contact, name, content FROM ReceivedMessage, Contact WHERE sender_contact = ? AND sender_contact = mac_address ORDER BY received_timestamp DESC LIMIT ?'
    with conn:
        return conn.execute(statement, (mac_address, limit))


def update_received_message(conn: sqlite3.Connection, sent_timestamp, **kwargs):
    fields = [*filter(lambda f: f in RECEIVED_MESSAGE_FIELDS and RECEIVED_MESSAGE_FIELDS[f]['editable'], kwargs)]
    if fields:
        values = [kwargs[field] for field in fields]
        values.append(sent_timestamp)
        statement = f"UPDATE ReceivedMessage SET {'= ?, '.join(fields)} = ? WHERE received_timestamp = ?"
        with conn:
            conn.execute(statement, values)


def delete_received_message(conn: sqlite3.Connection, received_timestamp):
    with conn:
        conn.execute('DELETE FROM ReceivedMessage WHERE received_timestamp = ?', (received_timestamp,))


@unwrap_get_received_message
def get_received_message(conn: sqlite3.Connection, received_timestamp, *args):
    fields = [*filter(lambda f: f in RECEIVED_MESSAGE_FIELDS, args)]
    if fields:
        with conn:
            statement = (f"SELECT {', '.join(fields)} FROM ReceivedMessage WHERE received_timestamp = ?")
            values = conn.execute(statement, (received_timestamp,)).fetchone()
            if not values:
                raise sqlite3.Error(
                    f"The ReceivedMessage with the received_timestamp '{received_timestamp}' does not exist")
        return dict(zip(fields, values))


def received_messages(conn: sqlite3.Connection):
    with conn:
        return conn.execute(
            'SELECT received_timestamp, sender_contact, content, sent_timestamp FROM ReceivedMessage ORDER BY received_timestamp DESC').fetchall()


def last_sent_or_received_messages_from_contact(conn: sqlite3.Connection, mac_address, limit=10):
    received_messages = last_received_messages_from_contact(conn, mac_address, limit)
    sent_messages = last_sent_messages_to_contact(conn, mac_address, limit)
    messages = []

    for received in received_messages:
        message = {
            'mac_address': received['sender_contact'],
            'name': received['name'],
            'timestamp': datetime.datetime.fromisoformat(received['received_timestamp']),
            'sent_timestamp': datetime.datetime.fromisoformat(received['sent_timestamp']),
            'content': received['content'],
            'type': 'received'
        }
        messages.append(message)

    for sent in sent_messages:
        message = {
            'mac_address': sent['receiver_contact'],
            'name': sent['name'],
            'timestamp': datetime.datetime.fromisoformat(sent['sent_timestamp']),
            'received_timestamp': datetime.datetime.fromisoformat(sent['received_timestamp']),
            'content': sent['content'],
            'type': 'sent'
        }
        messages.append(message)

    messages = sorted(messages, key=operator.itemgetter('timestamp'), reverse=True)
    return messages[:limit]


def last_sent_received_messages(conn: sqlite3.Connection, limit=10):
    last_sent = last_sent_messages(conn, limit)
    last_received = last_received_messages(conn, limit)
    last_messenguers = []

    for received in last_received:
        contact = {
            'mac_address': received['sender_contact'],
            'timestamp': datetime.datetime.fromisoformat(received['MAX(received_timestamp)']),
            'name': received['name']
        }
        last_messenguers.append(contact)

    for sent in last_sent:
        contact = {
            'mac_address': sent['receiver_contact'],
            'timestamp': datetime.datetime.fromisoformat(sent['MAX(sent_timestamp)']),
            'name': sent['name'],
        }
        exist = False
        for messenguer in last_messenguers:
            if messenguer['mac_address'] == contact['mac_address']:
                logging.debug(f"The contact '{messenguer['mac_address']}' exists")
                exist = True
                messenger_timestamp = messenguer['timestamp']
                if contact['timestamp'] > messenger_timestamp:
                    logging.debug(f"Updating timestamp")
                    logging.debug(f"Old timestamp: {messenguer['timestamp'].isoformat()}")
                    messenguer['timestamp'] = contact['timestamp']
                    logging.debug(f"New timestamp: {messenguer['timestamp'].isoformat()}")

        if not exist:
            last_messenguers.append(contact)

    last_messenguers = sorted(last_messenguers, key=operator.itemgetter('timestamp'), reverse=True)
    return last_messenguers


def get_connection():
    if DB_PATH:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn
    else:
        raise Exception('The database path has not been defined')


def set_dbpath(path):
    if os.path.isfile(path):
        global DB_PATH
        DB_PATH = path
    else:
        raise FileNotFoundError(f"No such file: '{path}')")


if __name__ == '__main__':
    from configuration import debug_database_path
    from pprint import pprint

    set_dbpath(debug_database_path())
    conn = get_connection()

    print('Last messages with McGleen')

    messages = last_sent_or_received_messages_from_contact(conn, 'eeee.fefe.acdf', limit=10)
    for m in messages:
        print(m)


    # last_messages_from_mcgleen = last_received_messages_from_contact(conn, 'eeee.fefe.acdf', 1)
    # for m in last_messages_from_mcgleen:
    #     print(dict(m))
    #
    # print('Las messages to McGleen')
    # last_messages_to_mcgleen = last_sent_messages_to_contact(conn, 'eeee.fefe.acdf', 1)
    # for m in last_messages_to_mcgleen:
    #     print(dict(m))
    conn.close()
    # last_messages = last_sent_received_messages(conn)
    # for m in last_messages:
    #     print(m)
