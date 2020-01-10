import socket
import urllib
import uuid
import Device


def get_device_from_list(devices=[]):
    try:
        current_mac_address = get_mac_address()
        for device in devices:
            if device.MacAddress == current_mac_address:
                return device
        return None

    except Exception:
        # most likely to catch if list of devices is empty
        return None


def get_host_name():
    try:
        host_name = socket.gethostname()
        return host_name
    except Exception:
        print("Unable to get Host Name")
        return "Error"


def get_local_ip():
    try:
        host_name = socket.gethostname()
        local_ip = socket.gethostbyname(host_name + ".local")
        return local_ip
    except Exception:
        print("Unable to get local IP")
        return "Error"


def get_external_ip():
    try:
        external_ip = urllib.urlopen('https://ident.me').read().decode('utf8')
        return external_ip
    except Exception:
        print("Unable to get external IP")
        return "Error"


def get_mac_address():
    try:
        mac_address = ':'.join(['{:02x}'.format((uuid.getnode() >> ele) & 0xff)
                                for ele in range(0, 8 * 6, 8)][::-1])
        return mac_address
    except Exception:
        print("Unable to get mac address")
        return "Error"


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
    except Exception:
        return False
