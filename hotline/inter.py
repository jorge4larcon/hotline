import asyncio
import logging
import json

_THE_MOST_COMMON_NAME_IN_THE_WORLD = 'Muhammad'
_GET = 'get'
_SIGN_UP = 'sign_up'
_DROP = 'drop'


class _Base:
    def __init__(self, password, method):
        self.user = 'client'
        self.password = password
        self.method = method

    def to_json_request(self):
        return f"{{\"user\":\"{self.user}\",\"password\":\"{self.password}\",\"method\":\"{self.method}\""

    def __str__(self):
        return 'base request'

    async def send_to(self, ip, port, timeout=3, password='secret'):
        # Write / Send
        try:
            reader, writer = await asyncio.wait_for(asyncio.open_connection(ip, port), timeout)
            self.password = password
            request = self.to_json_request().encode('UTF-8')
            logging.info(
                f'Sending a {self.method} to {ip}:{port} PASSWORD={password} [{len(request)} byte(s)]')
            writer.write(request)
            await writer.drain()
        except Exception as e:
            raise e

        # Read / Receive
        try:
            reply = await asyncio.wait_for(reader.read(65_535), timeout)
            logging.info(f'{len(reply)} byte(s) were received')
            reply = reply.decode('UTF-8')
            reply = json.loads(reply)
            return reply
        except Exception as e:
            raise e



class _Get(_Base):
    def __init__(self, password, how):
        super().__init__(password, _GET)
        self.how = how

    def to_json_request(self):
        return f"{super().to_json_request()},\"how\":\"{self.how}\""


class _GetByMac(_Get):
    def __init__(self, password, mac):
        super().__init__(password, 'mac')
        self.mac = mac

    def __str__(self):
        return f"Get '{self.mac}', password={self.password}"

    def to_json_request(self):
        return f"{super().to_json_request()},\"mac\":\"{self.mac}\"}}"


class _GetByUsername(_Get):
    def __init__(self, password, username, start_index):
        super().__init__(password, 'username')
        self.username = username
        self.start_index = start_index

    def __str__(self):
        return f"Get '{self.username}' start index: {self.start_index}, password={self.password}"

    def to_json_request(self):
        return f"{super().to_json_request()},\"username\":\"{self.username}\",\"start_index\":{self.start_index}}}"


class _Drop(_Base):
    def __init__(self, ip, password):
        super().__init__(password, _DROP)
        self.ip = ip

    def __str__(self):
        return f"Drop '{self.ip}', password={self.password}"

    def to_json_request(self):
        return f"{super().to_json_request()},\"ip\":\"{self.ip}\"}}"


class _SignUp(_Base):
    def __init__(self, mac, password, username, port, get_only_by_mac):
        super().__init__(password, _SIGN_UP)
        self.username = username
        self.mac = mac
        self.port = port
        self.get_only_by_mac = get_only_by_mac

    def __str__(self):
        if self.get_only_by_mac:
            return f"Sign up '{self.mac}' '{self.username}' PORT={self.port} GET-ONLY-BY-MAC, password={self.password}"
        else:
            return f"Sign up '{self.mac}' '{self.username}' PORT={self.port}, password={self.password}"

    def to_json_request(self):
        if self.get_only_by_mac:
            return f"{super().to_json_request()},\"username\":\"{self.username}\",\"mac\":\"{self.mac}\",\"port\":{self.port},\"get_only_by_mac\":true}}"
        else:
            return f"{super().to_json_request()},\"username\":\"{self.username}\",\"mac\":\"{self.mac}\",\"port\":{self.port},\"get_only_by_mac\":false}}"


def sign_up(mac, username=_THE_MOST_COMMON_NAME_IN_THE_WORLD, port=42_000, get_only_by_mac=False):
    return _SignUp(mac, '', username, port, get_only_by_mac)


def drop(ip):
    return _Drop(ip, '')


def get_by_username(username=_THE_MOST_COMMON_NAME_IN_THE_WORLD, start_index=0):
    return _GetByUsername('', str(username), start_index)


def get_by_mac(mac):
    return _GetByMac('', mac)
