import socket
from requests import get
import uuid


def get_host_name():
    host_name = socket.gethostname()
    return host_name


def get_local_ip():
    try:
        host_name = socket.gethostname()
        local_ip = socket.gethostbyname(host_name)
        return local_ip
    except:
        print("Unable to get local IP")
        return None


def get_external_ip():
    try:
        external_ip = get('https://api.ipify.org').text
        return external_ip
    except:
        print("Unable to get external IP")


def get_mac_address():
    mac_address = ':'.join(['{:02x}'.format((uuid.getnode() >> ele) & 0xff)
                           for ele in range(0, 8 * 6, 8)][::-1])
    return mac_address


def is_connected(host="8.8.8.8", port=53, timeout=3):
    """
    Host: 8.8.8.8 (google-public-dns-a.google.com)
    OpenPort: 53/tcp
    Service: domain (DNS/TCP)
    """
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        # print("Connected")
        return True
    except:
        return False
