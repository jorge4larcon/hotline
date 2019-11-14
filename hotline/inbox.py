import asyncio
import json
import logging
import socket
import datetime
import valid
import dbfunctions

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


async def receive_message(message, user_mac_address, received_timestamp, peer_address, peer_family):
    if user_mac_address == message['receiver']:
        try:
            conn = dbfunctions.get_connection()
            exists = dbfunctions.get_contact(conn, message['sender'], 'name')
            if not exists:
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
            dbfunctions.insert_received_message(conn, received_timestamp, message['sender'], message['content'],
                                                message['sent_timestamp'])
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


async def start_server(ip_address, port=42000):
    server = await asyncio.start_server(handle_client, ip_address, port)
    logging.info(f'Inbox server listening on {ip_address}:{port}')
    async with server:
        await server.serve_forever()
