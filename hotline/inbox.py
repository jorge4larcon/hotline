import asyncio
import json
import logging
import socket
import datetime
import valid
import dbfunctions
import configuration
from PyQt5 import QtCore

MAX_BYTES = 4096


def address_and_family(writer: asyncio.StreamWriter):
    peersocket = writer.get_extra_info('socket')
    if peersocket:
        peername = writer.get_extra_info('peername')
        if peername:
            return peername[0], peersocket.family
        else:
            return None, peersocket.family
    else:
        return None, None


def address_and_family_from_transport(transport: asyncio.transports.BaseTransport):
    socket = transport.get_extra_info('socket')
    if socket:
        peername = transport.get_extra_info('peername')
        if peername:
            return peername[0], socket.family
        else:
            return None, socket.family
    else:
        return None, None


def parse_request(raw_request: bytes):
    str_request = raw_request.decode('UTF-8')
    try:
        json_request = json.loads(str_request)
        subject = json_request['subject']
        if subject == 'message':
            str_sent_timestamp = json_request['sent_timestamp']
            sent_timestamp = datetime.datetime.fromisoformat(str_sent_timestamp)

            valid.is_valid_message_content(json_request['content'], exception=True)
            content = json_request['content']

            valid.is_mac_address(json_request['sender'], exception=True)
            sender = json_request['sender']

            valid.is_mac_address(json_request['receiver'])
            receiver = json_request['receiver']

            request = {
                'subject': subject,
                'sent_timestamp': sent_timestamp,
                'content': content,
                'sender': sender,
                'receiver': receiver
            }
        elif subject == 'get_contact_information':
            request = {'subject': subject}
        else:
            raise ValueError(f"Invalid subject: '{subject}'")
    except Exception:
        raise
    else:
        return request


# async def get_contact_information(ip_address, port=42000, timeout=3):
#     try:
#         reader, writer = await asyncio.wait_for(asyncio.open_connection(ip_address, port), timeout)
#         request = '{"subject":"get_contact_information"}'.encode('UTF-8')
#         writer.write(request)
#         await writer.drain()
#         data = await asyncio.wait_for(reader.read(MAX_BYTES), timeout)
#         reply = data.decode('UTF-8')
#         json_contact = json.loads(reply)
#         address, family = address_and_family(writer)
#         contact = {
#             'name': json_contact['name'],
#             'mac_address': json_contact['mac_address'],
#             'ipv4_address': json_contact['ipv4_address'],
#             'ipv6_address': json_contact['ipv6_address'],
#             'inbox_port': json_contact['inbox_port'],
#             'ftp_port': json_contact['ftp_port']
#         }
#         if address:
#             if family == socket.AF_INET:
#                 json_contact['ipv4_address'] = address
#             elif family == socket.AF_INET6:
#                 json_contact['ipv6_address'] = address
#
#     except Exception:
#         raise
#     else:
#         return contact
#     finally:
#         writer.close()
#         await writer.wait_closed()


async def get_contact_information(ip_address, port=42000, timeout=3):
    try:
        reader, writer = await asyncio.wait_for(asyncio.open_connection(ip_address, port), timeout)
        try:
            request = '{"subject":"get_contact_information"}'.encode('UTF-8')
            writer.write(request)
            await writer.drain()
            data = await asyncio.wait_for(reader.read(MAX_BYTES), timeout)
            reply = data.decode('UTF-8')
            json_contact = json.loads(reply)
            address, family = address_and_family(writer)
            contact = {
                'name': json_contact['name'],
                'mac_address': json_contact['mac_address'],
                'ipv4_address': json_contact['ipv4_address'],
                'ipv6_address': json_contact['ipv6_address'],
                'inbox_port': json_contact['inbox_port'],
                'ftp_port': json_contact['ftp_port']
            }
            if address:
                if family == socket.AF_INET:
                    json_contact['ipv4_address'] = address
                elif family == socket.AF_INET6:
                    json_contact['ipv6_address'] = address
        except Exception as e:
            raise e
        else:
            return contact
        finally:
            writer.close()
            await writer.wait_closed()

    except asyncio.TimeoutError as e:
        raise e
    except Exception as e:
        raise e


async def message_to(ip_address, sender, sent_timestamp, content, receiver, port=42000, timeout=3):
    received_confirmation = None
    try:
        reader, writer = await asyncio.wait_for(asyncio.open_connection(ip_address, port), timeout)
        request = f'{{"subject":"message","sent_timestamp":"{sent_timestamp}","content":"{content}","sender":"{sender}","receiver":"{receiver}"}}'.encode(
            'UTF-8')
        writer.write(request)
        await writer.drain()
        data = await asyncio.wait_for(reader.read(MAX_BYTES), timeout)
        reply = data.decode('UTF-8')
        received_confirmation = json.loads(reply)
    except Exception:
        raise
    else:
        return received_confirmation
    finally:
        writer.close()
        await writer.wait_closed()


async def confirm_received(writer, receiver, received_timestamp):
    confirmation = f'{{"received_timestamp":"{received_timestamp}","receiver":"{receiver}"}}'.encode('UTF-8')
    writer.write(confirmation)
    await writer.drain()


async def receive_message(message, user_mac_address, received_timestamp, peer_address, peer_family, signals):
    if user_mac_address == message['receiver']:
        try:
            conn = dbfunctions.get_connection()
            exists = dbfunctions.get_contact(conn, message['sender'], 'name')
            is_stranger = False
            if not exists:
                is_stranger = True
                if peer_address:
                    if peer_family == socket.AF_INET:
                        dbfunctions.insert_contact(conn, message['sender'], name='Stranger', ipv4_address=peer_address)
                    elif peer_family == socket.AF_INET6:
                        dbfunctions.insert_contact(conn, message['sender'], name='Stranger', ipv6_address=peer_address)
                    else:
                        dbfunctions.insert_contact(conn, message['sender'], name='Stranger')
                else:
                    dbfunctions.insert_contact(conn, message['sender'], name='Stranger')

            # TODO: After adding or not the contact its a good idead to update its ip address in the database

            ipv = None
            if peer_address:
                if peer_family == socket.AF_INET:
                    ipv = 4
                    dbfunctions.update_contact(conn, message['sender'], ipv4_address=peer_address)
                elif peer_family == socket.AF_INET6:
                    ipv = 6
                    dbfunctions.update_contact(conn, message['sender'], ipv6_address=peer_address)

            dbfunctions.insert_received_message(conn, received_timestamp, message['sender'], message['content'],
                                                message['sent_timestamp'])
            signal_info = {"mac_address": message['sender'], "is_stranger": is_stranger, "ipv": ipv, "ip": peer_address}
            signals.on_message_received.emit(signal_info)
        except Exception as e:
            logging.error(e)
        finally:
            conn.close()
    else:
        logging.info(f"I received a message that was for '{message['receiver']}'")


async def deliver_contact_information(writer, mac_address, name, ipv4_address, ipv6_address, inbox_port, ftp_port):
    contact_info = json.dumps({
        "name": name,
        "mac_address": mac_address,
        "ipv4_address": ipv4_address,
        "ipv6_address": ipv6_address,
        "inbox_port": inbox_port,
        "ftp_port": ftp_port
    }).encode('UTF-8')
    writer.write(contact_info)
    await writer.drain()


async def handle_client(reader, writer):
    data = await reader.read(MAX_BYTES)
    request = parse_request(data)
    if request:
        conn = dbfunctions.get_connection()
        mac_address, name, ipv4_address, ipv6_address, inbox_port, ftp_port = dbfunctions.get_configuration(
            conn, 'mac_address', 'username', 'ipv4_address', 'ipv6_address', 'inbox_port', 'ftp_port')
        conn.close()
        if mac_address:
            if request['subject'] == 'message':
                peer_address, peer_family = address_and_family(writer)
                received_timestamp = datetime.datetime.now().isoformat()
                confirm_received_exception, receive_message_exception = await asyncio.gather(
                    confirm_received(writer, mac_address, received_timestamp),
                    receive_message(request, mac_address, received_timestamp, peer_address, peer_family),
                    return_exceptions=True
                )
                if confirm_received_exception:
                    logging.error(confirm_received_exception)

                if receive_message_exception:
                    logging.error(receive_message_exception)

            elif request['subject'] == 'get_contact_information':
                await deliver_contact_information(writer, mac_address, name, ipv4_address, ipv6_address, inbox_port,
                                                  ftp_port)
        else:
            logging.critical(f"Could not obtain the user information from the database")
    else:
        logging.error(f"Could not parse the request")

    writer.close()


async def start_server(ip_address, signals, port=42000):
    server = await asyncio.start_server(handle_client, ip_address, port)
    logging.info(f'Inbox server listening on {ip_address}:{port}')
    async with server:
        await server.serve_forever()


class InboxServerSignals(QtCore.QObject):
    # the ip and port where the server is binded
    on_start = QtCore.pyqtSignal(str, int)
    on_error = QtCore.pyqtSignal('PyQt_PyObject')
    # The mac address of who sent us the message
    on_message_received = QtCore.pyqtSignal(dict)
    # remote ip who requested information
    on_get_contact_information = QtCore.pyqtSignal(str)


class InboxServerProtocol(asyncio.Protocol):
    def __init__(self, signals: InboxServerSignals):
        self.signals = signals

    def connection_made(self, transport: asyncio.transports.BaseTransport) -> None:
        peername = transport.get_extra_info('peername')
        logging.info('Connection from {}'.format(peername))
        self.transport = transport

    def data_received(self, data: bytes) -> None:
        request = parse_request(data)
        if request:
            conn = dbfunctions.get_connection()
            mac_address, name, ipv4_address, ipv6_address, inbox_port, ftp_port = dbfunctions.get_configuration(
                conn, 'mac_address', 'username', 'ipv4_address', 'ipv6_address', 'inbox_port', 'ftp_port')
            conn.close()
            if mac_address:
                peer_address, peer_family = address_and_family_from_transport(self.transport)
                if request['subject'] == 'message':
                    received_timestamp = datetime.datetime.now().isoformat()

                    ### CONFIRM RECEIVED
                    confirmation = f'{{"received_timestamp":"{received_timestamp}","receiver":"{mac_address}"}}'.encode(
                        'UTF-8')
                    self.transport.write(confirmation)
                    ### CONFIRM RECEIVED

                    ### RECEIVE MESSAGE
                    if mac_address == request['receiver']:
                        try:
                            conn = dbfunctions.get_connection()
                            try:
                                exists = dbfunctions.get_contact(conn, request['sender'], 'name')
                            except Exception as e:
                                exists = False
                            else:
                                exists = True

                            is_stranger = False
                            if not exists:
                                logging.info(f"The contact {request['sender']} does not exist, adding him to db")
                                is_stranger = True
                                if peer_address:
                                    if peer_family == socket.AF_INET:
                                        dbfunctions.insert_contact(conn, request['sender'], name='Stranger',
                                                                   ipv4_address=peer_address)
                                        logging.info(f"The contact {request['sender']} was added")
                                    elif peer_family == socket.AF_INET6:
                                        dbfunctions.insert_contact(conn, request['sender'], name='Stranger',
                                                                   ipv6_address=peer_address)
                                        logging.info(f"The contact {request['sender']} was added")
                                    else:
                                        dbfunctions.insert_contact(conn, request['sender'], name='Stranger')
                                        logging.info(f"The contact {request['sender']} was added")
                                else:
                                    dbfunctions.insert_contact(conn, request['sender'], name='Stranger')
                                    logging.info(f"The contact {request['sender']} was added")

                            ipv = None
                            if peer_address:
                                if peer_family == socket.AF_INET:
                                    ipv = 4
                                    dbfunctions.update_contact(conn, request['sender'], ipv4_address=peer_address)
                                elif peer_family == socket.AF_INET6:
                                    ipv = 6
                                    dbfunctions.update_contact(conn, request['sender'], ipv6_address=peer_address)

                            dbfunctions.insert_received_message(conn, received_timestamp, request['sender'],
                                                                request['content'],
                                                                request['sent_timestamp'])
                            signal_info = {"mac_address": request['sender'], "is_stranger": is_stranger, "ipv": ipv,
                                           "ip": peer_address}
                            self.signals.on_message_received.emit(signal_info)
                        except Exception as e:
                            logging.error(e)
                        finally:
                            conn.close()
                    else:
                        logging.info(f"I received a message that was for '{request['receiver']}'")
                    ### RECEIVE MESSAGE

                elif request['subject'] == 'get_contact_information':
                    self.signals.on_get_contact_information.emit(peer_address)

                    ### DELIVER CONTACT INFORMATION
                    contact_info = json.dumps({
                        "name": name,
                        "mac_address": mac_address,
                        "ipv4_address": ipv4_address,
                        "ipv6_address": ipv6_address,
                        "inbox_port": inbox_port,
                        "ftp_port": ftp_port
                    }).encode('UTF-8')
                    self.transport.write(contact_info)
                    ### DELIVER CONTACT INFORMATION
            else:
                logging.critical(f"Could not obtain the user information from the database")
        else:
            logging.error(f"Could not parse the request")

        self.transport.close()


async def run_inbox_server(ip, port, signals):
    loop = asyncio.get_running_loop()
    server = await loop.create_server(lambda: InboxServerProtocol(signals), ip, port)
    signals.on_start.emit(ip, port)
    async with server:
        await server.serve_forever()


class InboxServerThread(QtCore.QRunnable):
    def __init__(self, ip, port):
        super(InboxServerThread, self).__init__()
        self.ip = ip
        self.port = port
        self.signals = InboxServerSignals()

    def run(self) -> None:
        try:
            asyncio.run(run_inbox_server(self.ip, self.port, self.signals))
        except Exception as e:
            self.signals.on_error.emit(e)


class SendMessageSignals(QtCore.QObject):
    # remote_ip4, remote_ip6, ip_version, remote_mac, remote_name, local_mac, message, port, exception
    on_error = QtCore.pyqtSignal(str, str, int, str, str, str, str, int, 'PyQt_PyObject')
    # remote_ip4, remote_ip6, ip_version, remote_mac, remote_name, local_mac, message, port, received_confirmation_dict, sent_timestamp
    on_received_confirmation = QtCore.pyqtSignal(str, str, int, str, str, str, str, int, dict, str)
    # remote_mac, remote_ip
    on_sent = QtCore.pyqtSignal(str, str)


class SendMessageThread(QtCore.QRunnable):
    def __init__(self, remote_ip4, remote_ip6, ip_version, remote_mac, remote_name, local_mac, message, port):
        super(SendMessageThread, self).__init__()
        self.remote_ip4 = remote_ip4
        self.remote_ip6 = remote_ip6
        self.ip_version = ip_version
        self.port = port

        self.remote_mac = remote_mac
        self.remote_name = remote_name

        self.local_mac = local_mac

        self.message = message

        self.signals = SendMessageSignals()

    def run(self) -> None:
        try:
            ip = None
            if self.ip_version == 4:
                ip = self.remote_ip4
            elif self.ip_version == 6:
                ip = self.remote_ip6

            sent_timestamp = datetime.datetime.now().isoformat()
            recv_confirmation = asyncio.run(
                message_to(ip, self.local_mac, sent_timestamp, self.message, self.remote_mac, self.port))
        except Exception as e:
            self.signals.on_error.emit(self.remote_ip4, self.remote_ip6, self.ip_version, self.remote_mac,
                                       self.remote_name, self.local_mac, self.message, self.port, e)
        else:
            self.signals.on_received_confirmation.emit(self.remote_ip4, self.remote_ip6, self.ip_version,
                                                       self.remote_mac, self.remote_name, self.local_mac, self.message,
                                                       self.port, recv_confirmation, sent_timestamp)


class LastAttempSendMessageSignals(QtCore.QObject):
    on_received_confirmation = QtCore.pyqtSignal(str, dict, str, str)
    on_error = QtCore.pyqtSignal(str, 'PyQt_PyObject')


class LastAttempSendMessageThread(QtCore.QRunnable):
    def __init__(self, remote_ip4, remote_ip6, ip_version, port, remote_mac, remote_name, local_mac, message):
        super(LastAttempSendMessageThread, self).__init__()
        self.remote_ip4 = remote_ip4
        self.remote_ip6 = remote_ip6
        self.port = port
        self.ip_version = ip_version
        self.remote_mac = remote_mac
        self.remote_name = remote_name
        self.message = message
        self.local_mac = local_mac
        self.signals = LastAttempSendMessageSignals()

    def run(self) -> None:
        try:
            ip = None
            if self.ip_version == 4:
                ip = self.remote_ip4
            elif self.ip_version == 6:
                ip = self.remote_ip6

            sent_timestamp = datetime.datetime.now().isoformat()
            recv_conf = asyncio.run(
                message_to(ip, self.local_mac, sent_timestamp, self.message, self.remote_mac, self.port))
        except Exception as e:
            self.signals.on_error.emit(self.remote_name, e)
        else:
            self.signals.on_received_confirmation.emit(self.remote_mac, recv_conf, sent_timestamp, self.message)


class SmartSendMessageSignals(QtCore.QObject):
    on_fail = QtCore.pyqtSignal()
    # received_confirmation, sent_timestamp and message
    on_success = QtCore.pyqtSignal(dict, str, str)


class SmartSendMessageThread(QtCore.QRunnable):
    def __init__(self, ip4, ip6, port, remote_mac, local_mac, inter_ip, inter_port, inter_password, message, timeout=3):
        super(SmartSendMessageThread, self).__init__()
        self.port = port
        self.remote_mac = remote_mac
        self.local_mac = local_mac
        self.ip4 = ip4
        self.ip6 = ip6
        self.ip6lleui64 = configuration.generate_ipv6_linklocal_eui64_address(remote_mac)
        self.inter_ip = inter_ip
        self.inter_port = inter_port
        self.inter_password = inter_password
        self.did_i_request_info = False
        self.message = message
        self.timeout = timeout
        self.signals = SmartSendMessageSignals()

    def run(self) -> None:
        if self.ip4 and self.ip6:
            self.sm_ip4_ip6()
        elif self.ip4 and not self.ip6:
            self.sm_ip4_noip6()
        elif not self.ip4 and self.ip6:
            self.sm_noip4_ip6()
        elif not self.ip4 and not self.ip6:
            self.sm_noip4_noip6()

    def sm_ip4_ip6(self):
        try:
            sent_timestamp = datetime.datetime.now().isoformat()
            recv_conf = asyncio.run(message_to(self.ip4, self.local_mac, sent_timestamp, self.message, self.remote_mac, self.port, self.timeout))
        except Exception as e:
            self.sm_noip4_ip6()
        else:
            if recv_conf.get('receiver') == self.remote_mac:
                self.signals.on_success.emit(recv_conf, sent_timestamp, self.message)
            else:
                self.sm_noip4_noip6()

    def sm_noip4_ip6(self):
        try:
            sent_timestamp = datetime.datetime.now().isoformat()
            recv_conf = asyncio.run(message_to(self.ip6, self.local_mac, sent_timestamp, self.message, self.remote_mac, self.port, self.timeout))
        except Exception as e:
            self.sm_noip4_noip6()
        else:
            if recv_conf.get('receiver') == self.remote_mac:
                self.signals.on_success.emit(recv_conf, sent_timestamp, self.message)
            else:
                self.sm_noip4_noip6()

    def sm_ip4_noip6(self):
        try:
            sent_timestamp = datetime.datetime.now().isoformat()
            recv_conf = asyncio.run(message_to(self.ip4, self.local_mac, sent_timestamp, self.message, self.remote_mac, self.port, self.timeout))
        except Exception as e:
            self.sm_noip4_noip6()
        else:
            if recv_conf.get('receiver') == self.remote_mac:
                self.signals.on_success.emit(recv_conf, sent_timestamp, self.message)
            else:
                self.sm_noip4_noip6()

    def sm_noip4_noip6(self):
        pass
