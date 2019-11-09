import re
import ipaddress

NAME_RE = '^[a-zA-Z0-9_-]{3,24}$'
MAC_ADDR_RE = '^(^([a-f0-9][a-f0-9][a-f0-9][a-f0-9]+[.]){2}([a-f0-9][a-f0-9][a-f0-9][a-f0-9]))$'


def is_mac_address(mac_address: str, exception=False) -> bool:
    is_valid = True if re.match(MAC_ADDR_RE, mac_address) else False
    if exception and not is_valid:
        raise ValueError(f"Invalid MAC address: '{mac_address}'")

    return is_valid


def is_name(name: str, exception=False) -> bool:
    is_valid = True if re.match(NAME_RE, name) else False
    if exception and not is_valid:
        raise ValueError(f"Invalid name: '{name}'")

    return is_valid


def is_ipv4_address(ipv4_address: str, exception=False) -> bool:
    try:
        ipaddress.IPv4Address(ipv4_address)
    except ipaddress.AddressValueError:
        if exception:
            raise

        return False
    else:
        return True


def is_ipv6_address(ipv6_address: str, exception=False) -> bool:
    try:
        if '%' in ipv6_address:
            ipv6_address = ipv6_address.split('%')[0]

        ipaddress.IPv6Address(ipv6_address)
    except ipaddress.AddressValueError:
        if exception:
            raise

        return False
    else:
        return True


def is_valid_message_content(content: str, exception=False) -> bool:
    is_valid = 1 <= len(content) <= 2048
    if exception and not is_valid:
        raise ValueError('The message content is a str, with a length that must be within the range [1,2048]')

    return is_valid
