# Author: Jorge Alarcon Alvarez
# Email: jorge4larcon@gmail.com
"""This module defines functions and classes to send and receive messages across a LAN"""

import asyncio
import json
import logging
import socket
import datetime
import valid
import dbfunctions
import configuration
import inter
from PyQt5 import QtCore

MAX_BYTES = 4096


def address_and_family(writer: asyncio.StreamWriter):
    """This functions get the IP address and the socket family of a client socket"""
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
    """This functions get the IP address and the socket family of a client transport"""
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
    """This function parses the incomming client request"""
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
    """This functions sends a `get_contact_information` request to an specific socket address."""
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
    """This functions send a `message` request to an specific socket address."""
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
    """This functions writes a `received_confirmation` to a client socket."""
    confirmation = f'{{"received_timestamp":"{received_timestamp}","receiver":"{receiver}"}}'.encode('UTF-8')
    writer.write(confirmation)
    await writer.drain()


async def receive_message(message, user_mac_address, received_timestamp, peer_address, peer_family, signals):
    """This functions receives an incomming message from a remote contact and add the message to the database."""
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
    """This functions writes the user contact information to a remote socket."""
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
    """This functions handles the request of a client."""
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
    """This functions starts the server in an specific socket address"""
    server = await asyncio.start_server(handle_client, ip_address, port)
    logging.info(f'Inbox server listening on {ip_address}:{port}')
    async with server:
        await server.serve_forever()


class InboxServerSignals(QtCore.QObject):
    """This class defines the events of the message receiver server"""
    # the ip and port where the server is binded
    on_start = QtCore.pyqtSignal(str, int)
    on_error = QtCore.pyqtSignal('PyQt_PyObject')
    # The mac address of who sent us the message
    on_message_received = QtCore.pyqtSignal(dict)
    # remote ip who requested information
    on_get_contact_information = QtCore.pyqtSignal(str)


class InboxServerProtocol(asyncio.Protocol):
    """This is the class that defines the thread where the message receiver server runs"""
    def __init__(self, signals: InboxServerSignals):
        self.signals = signals

    def connection_made(self, transport: asyncio.transports.BaseTransport) -> None:
        """When a client connects to the server"""
        peername = transport.get_extra_info('peername')
        logging.info('Connection from {}'.format(peername))
        self.transport = transport

    def data_received(self, data: bytes) -> None:
        """When a client sends data to the server"""
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
    """This is an async function to start the server"""
    loop = asyncio.get_running_loop()
    server = await loop.create_server(lambda: InboxServerProtocol(signals), ip, port)
    signals.on_start.emit(ip, port)
    async with server:
        await server.serve_forever()


class InboxServerThread(QtCore.QRunnable):
    """This is the thread of the message receiver server"""
    def __init__(self, ip, port):
        super(InboxServerThread, self).__init__()
        self.ip = ip
        self.port = port
        self.signals = InboxServerSignals()

    def run(self) -> None:
        """This functions defines the actions of the message receiver server does when started"""
        try:
            asyncio.run(run_inbox_server(self.ip, self.port, self.signals))
        except Exception as e:
            self.signals.on_error.emit(e)

class SmartSendMessageSignals(QtCore.QObject):
    """This class defines the signals or events of a SmartSendMessageThread"""
    # remote_name, remote_mac
    on_fail = QtCore.pyqtSignal(str, str)
    # received_confirmation, sent_timestamp, message, IPv used (4, 6, 6lleui64), contact_information
    on_success = QtCore.pyqtSignal(dict, str, str, str, dict)


class SmartSendMessageThread(QtCore.QRunnable):
    """This is the class that defines the thread to send a message."""
    def __init__(self, ip4, ip6, port, remote_mac, local_mac, inter_ip, inter_port, inter_password, message, name, timeout=3):
        super(SmartSendMessageThread, self).__init__()
        self.name = name
        self.port = port
        self.remote_mac = remote_mac
        self.local_mac = local_mac
        self.ip4 = ip4
        self.ip6 = ip6
        self.ip6lleui64 = configuration.generate_ipv6_linklocal_eui64_address(remote_mac)
        self.inter_ip = inter_ip
        self.inter_port = inter_port
        self.inter_password = inter_password
        self.i_requested_info_before = False
        self.message = message
        self.timeout = timeout
        self.signals = SmartSendMessageSignals()
        self.new_contact_info = {}

    def run(self) -> None:
        """This method is called when the SmartSentMessageThread starts"""
        if self.ip4 and self.ip6:
            self.sm_ip4_ip6()
        elif self.ip4 and not self.ip6:
            self.sm_ip4_noip6()
        elif not self.ip4 and self.ip6:
            self.sm_noip4_ip6()
        elif not self.ip4 and not self.ip6:
            self.sm_noip4_noip6()

    def sm_ip4_ip6(self):
        """This method send the message using the IPv4 address"""
        logging.info(f'{self.name} has IPv4 and IPv6 address, trying with IPv4')
        try:
            sent_timestamp = datetime.datetime.now().isoformat()
            recv_conf = asyncio.run(message_to(self.ip4, self.local_mac, sent_timestamp, self.message, self.remote_mac, self.port, self.timeout))
        except Exception as e:
            logging.info(f'Could not send the message by IPv4')
            self.sm_noip4_ip6()
        else:
            logging.info(f'The message was sent')
            if recv_conf.get('receiver') == self.remote_mac:
                logging.info('The message was delivered to the correct contact')
                self.signals.on_success.emit(recv_conf, sent_timestamp, self.message, '4', self.new_contact_info)
            else:
                logging.info('The message was delivered to the incorrect contact, requesting information')
                self.req_information()

    def sm_noip4_ip6(self):
        """This method send the message using the IPv6 address"""
        logging.info(f'{self.name} has IPv6 address, trying with IPv6')
        try:
            sent_timestamp = datetime.datetime.now().isoformat()
            recv_conf = asyncio.run(message_to(self.ip6, self.local_mac, sent_timestamp, self.message, self.remote_mac, self.port, self.timeout))
        except Exception as e:
            logging.info(f'Could not send the message by IPv6')
            self.sm_noip4_noip6()
        else:
            logging.info(f'The message was sent')
            if recv_conf.get('receiver') == self.remote_mac:
                logging.info('The message was delivered to the correct contact')
                self.signals.on_success.emit(recv_conf, sent_timestamp, self.message, '6', self.new_contact_info)
                # Avisa que la IPv4 deberia ser eliminada
                # Recurrí a IPv4, IPv6 , solo la ultima funciono, por lo tanto deberias eliminar la IPv4
            else:
                logging.info('The message was delivered to the incorrect contact, requesting information')
                self.req_information()

    def sm_ip4_noip6(self):
        """This method send the message using the IPv4 address"""
        logging.info(f'{self.name} has IPv4 address, trying with IPv4')
        try:
            sent_timestamp = datetime.datetime.now().isoformat()
            recv_conf = asyncio.run(message_to(self.ip4, self.local_mac, sent_timestamp, self.message, self.remote_mac, self.port, self.timeout))
        except Exception as e:
            logging.info(f'Could not send the message by IPv4')
            self.sm_noip4_noip6()
        else:
            logging.info(f'The message was sent')
            if recv_conf.get('receiver') == self.remote_mac:
                logging.info('The message was delivered to the correct contact')
                self.signals.on_success.emit(recv_conf, sent_timestamp, self.message, '4', self.new_contact_info)
            else:
                logging.info('The message was delivered to the incorrect contact, requesting information')
                self.req_information()

    def sm_noip4_noip6(self):
        """This method send the message using the IPv6 link local EUI-64 address"""
        logging.info(f'{self.name} has not IPv4 or IPv6 address, trying with IPv6 LL EUI-64 address')
        if self.ip6 == self.ip6lleui64:
            logging.info(f'The IPv6 address is the same as the IPv6 LL EUI-64 address, requesting information')
            self.req_information()
        else:
            logging.info(f'The IPv6 address is different to the IPv6 LL EUI-64 address')
            try:
                sent_timestamp = datetime.datetime.now().isoformat()
                recv_conf = asyncio.run(
                    message_to(self.ip6lleui64, self.local_mac, sent_timestamp, self.message, self.remote_mac, self.port,
                               self.timeout))
            except Exception as e:
                logging.info(f'Could not send the message by IPv6 LL EUI-64, requesting information')
                self.req_information()
            else:
                logging.info(f'The message was sent')
                if recv_conf.get('receiver') == self.remote_mac:
                    logging.info('The message was delivered to the correct contact')
                    self.signals.on_success.emit(recv_conf, sent_timestamp, self.message, '6lleui64', self.new_contact_info)
                    # Recurrí a IPv4, IPv6 e IPv6 LL, solo la ultima funciono, por lo tanto deberias actualizar
                    # la ipv6 y eliminar la IPv4
                else:
                    logging.info('The message was delivered to the incorrect contact, requesting information')
                    self.req_information()

    def req_information(self):
        """This method request information to an Interlocutor server"""
        # Ive tried with IPv4, IPv6 and IPv6 LL EUI-64 and no one has worked.
        # Im going to ask for information to the Interlocutor
        if self.i_requested_info_before:
            logging.info(f'I have requested information to {self.name} before, cancelling the message')
            self.signals.on_fail.emit(self.name, self.remote_mac)
        else:
            self.i_requested_info_before = True
            logging.info(f'Requesting information to Interlocutor server {self.inter_ip}...')
            try:
                req = inter.get_by_mac(self.remote_mac)
                ci = asyncio.run(
                    req.send_to(self.inter_ip, self.inter_port, timeout=self.timeout, password=self.inter_password))
            except Exception as e:
                logging.info('Could not request information to the Interlocutor server')
                self.signals.on_fail.emit(self.name, self.remote_mac)
            else:
                logging.info('Information requested to the Interlocutor server')
                ci = ci.get('client')
                if ci:
                    try:
                        ip4 = ci['ipv4_addr']
                        port = ci['port']
                    except Exception as e:
                        logging.info(f'The reply from the Interlocutor is wrong, cancelling')
                        self.signals.on_fail.emit(self.name, self.remote_mac)
                    else:
                        logging.info(f'Interlocutor suggested the next address: {ip4}:{port}')
                        if ip4 == self.ip4 and port == self.port:
                            logging.info('The address suggested and the one we tried with are the same, cancelling')
                            self.signals.on_fail.emit(self.name, self.remote_mac)
                        else:
                            try:
                                logging.info(f'Requesting information to {self.name} using {ip4}:{port}...')
                                ci = asyncio.run(get_contact_information(ip4, port, self.timeout))
                            except Exception as e:
                                logging.info('Could not request information')
                                self.signals.on_fail.emit(self.name, self.remote_mac)
                            else:
                                logging.info('The information request was successful')
                                if ci['mac_address'] == self.remote_mac:
                                    try:
                                        logging.info(f'The user who replied to the information request has the same MAC address')
                                        self.ip4 = ci['ipv4_address']
                                        self.ip6 = ci['ipv6_address']
                                        self.port = ci['inbox_port']
                                        self.new_contact_info = ci
                                        if self.ip4 and self.ip6:
                                            self.sm_ip4_ip6()
                                        elif self.ip4 and not self.ip6:
                                            self.sm_ip4_noip6()
                                        elif not self.ip4 and self.ip6:
                                            self.sm_noip4_ip6()
                                        elif not self.ip4 and not self.ip6:
                                            self.sm_noip4_noip6()
                                    except Exception as e:
                                        self.signals.on_fail.emit(self.name, self.remote_mac)
                                else:
                                    logging.info(f'The user who replied to the information request has a different MAC address, cancelling')
                                    self.signals.on_fail.emit(self.name, self.remote_mac)
                else:
                    self.signals.on_fail.emit(self.name, self.remote_mac)
