import logging
import sys
import os
import netifaces
import socket
import ipaddress
import dbfunctions


def setup_network_information():
    ipv4 = ipv4_address()
    iface = network_interface(ipv4)
    ipv6 = ipv6_link_local_address(iface)
    mac = mac_address(iface)
    conn = dbfunctions.get_connection()
    dbfunctions.update_configuration(conn, mac_address=mac, ipv4_address=ipv4, ipv6_address=ipv6)
    conn.close()
    logging.info(f'Network information:\nIPv4={ipv4}\nIPv6={ipv6}\nIFACE={iface}\nMAC={mac}')


def configure_logging(level):
    logging.basicConfig(
        # format='[%(asctime)s] [thread-id=%(thread)d] [thread-name=%(threadName)s] %(levelname)s: %(message)s',
        format='[%(asctime)s] p%(process)s {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s',
        level=level)


# You need to pass __file__
def bundled_database_path(file):
    bundle_dir = getattr(sys, '_MEIPASS', os.path.abspath(os.path.dirname(file)))
    return os.path.join(bundle_dir, 'hotline.db')


def debug_database_path():
    return os.path.join('../resources', 'hotline.db')


def running_as_a_python_process():
    try:
        if getattr(sys, 'frozen') and hasattr(sys, '_MEIPASS'):
            # The program is running in a PyInstaller bundle
            return False
        else:
            # The program is running in a normal Python process
            return True
    except AttributeError:
        return True


def generate_ipv6_linklocal_eui64_address(mac_address: str):
    parts = [mac_address[:2], mac_address[2:4], mac_address[5:7], mac_address[7:9], mac_address[10:12],
             mac_address[12:]]
    parts.insert(3, "ff")
    parts.insert(4, "fe")
    parts[0] = "%x" % (int(parts[0], 16) ^ 2)
    ipv6Parts = []
    for i in range(0, len(parts), 2):
        ipv6Parts.append("".join(parts[i:i + 2]))
    ipv6 = "fe80::%s" % (":".join(ipv6Parts))
    return ipv6


def ipv4_address():
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.connect(('192.168.1.1', 42000))
        ip = sock.getsockname()[0]
    except OSError:
        ip = None
    finally:
        return ip


def ipv6_link_local_address(iface):
    for interface in netifaces.interfaces():
        if iface == interface:
            addresses = netifaces.ifaddresses(iface).get(netifaces.AF_INET6)
            if addresses:
                for address in addresses:
                    ip = address['addr'].split('%')[0]
                    if ipaddress.IPv6Address(ip).is_link_local:
                        return address['addr']


def network_interface(ipv4):
    for iface in netifaces.interfaces():
        addresses = netifaces.ifaddresses(iface).get(netifaces.AF_INET)
        if addresses:
            for address in addresses:
                if address.get('addr') == ipv4:
                    return iface


def mac_address(iface):
    mac = netifaces.ifaddresses(iface).get(netifaces.AF_LINK)[0].get('addr')
    return f"{mac[0:2]}{mac[3:5]}.{mac[6:8]}{mac[9:11]}.{mac[12:14]}{mac[15:]}"


if __name__ == '__main__':
    ipv4_addr = ipv4_address()
    net_interface = network_interface(ipv4_addr)
    ipv6_link_local_addr = ipv6_link_local_address(net_interface)
    mac_addr = mac_address(net_interface)
    ip_info = f"""Network interface:       {net_interface}
IPv4 address:            {ipv4_addr}
IPv6 link-local address: {ipv6_link_local_addr}
MAC address:             {mac_addr}"""
    print(ip_info)
