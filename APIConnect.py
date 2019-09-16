import requests


def update_device(pi_id, local_ip, external_ip, mac_address, update_date):
    url = 'https://174.101.154.93:1337/api/entryRetrieval'
    params = {'PiID': str(pi_id), 'LocalIP': str(local_ip), 'ExternalIP': str(external_ip), 'MacAddress': str(mac_address), 'UpdateAddress': update_date}

    try:
        r = requests.post(url=url, data=params, verify=False)
        data = r.json()
        if data is not None:
            return True

    except:
        return False

