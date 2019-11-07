import sqlite3
import os

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
    'interlocutor_address': {'editable': True, 'validator': None},
    'interlocutor_port': {'editable': True, 'validator': None},
    'interlocutor_password': {'editable': True, 'validator': None}
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


def insert_contact(conn: sqlite3.Connection, mac_address, name='Muhammad', ipv4_address=None, ipv6_address=None,
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
            statement = (f"SELECT {', '.join(fields)} FROM Contact WHERE mac_address = ?")
            values = conn.execute(statement, (mac_address,)).fetchone()
            if not values:
                raise sqlite3.Error(f"The Contact with the mac_address '{mac_address}' does not exist")
        return dict(zip(fields, values))


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


def insert_received_message(conn: sqlite3.Connection, received_timestamp, sender_contact, content, sent_timestamp):
    statement = 'INSERT INTO ReceivedMessage(received_timestamp, sender_contact, content, sent_timestamp) ' \
                'VALUES (?, ?, ?, ?)'
    with conn:
        conn.execute(statement, (received_timestamp, sender_contact, content, sent_timestamp))


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
