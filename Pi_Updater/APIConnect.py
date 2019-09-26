import requests
import Device
import json

address = "http://localhost:8080/"
# address = "http://173.91.255.135:8080/SpotCheckServer-2.1.8.RELEASE/"


def update_device(device):
    try:
        url = address + 'device/updateDevice'
        body = {'deviceId': device.DeviceId, 'deviceName': device.DeviceName, 'localIpAddress': device.LocalIpAddress, 'externalIpAddress': device.ExternalIpAddress, 'macAddress': device.MacAddress, 'lotId': device.LotId, 'floorNumber': device.FloorNumber, 'lastUpdateDate': str(device.LastUpdateDate)}
        headers = {'Content-type': 'application/json'}

        r = requests.post(url=url, headers=headers, data=json.dumps(body))
        data = r.text
        status_code = r.status_code

        if status_code == 200:
            return True
        else:
            print(data)
            return False

    # Catch any errors and return false
    except Exception as err:
        print(err)
        return False


def create_device(device):
    try:
        url = address + 'device/createDevice'
        body = {'deviceName': device.DeviceName, 'localIpAddress': device.LocalIpAddress, 'externalIpAddress': device.ExternalIpAddress, 'macAddress': device.MacAddress, 'lotId': device.LotId, 'floorNumber': device.FloorNumber, 'lastUpdateDate': str(device.LastUpdateDate)}
        headers = {'Content-type': 'application/json'}

        r = requests.post(url=url, headers=headers, data=json.dumps(body))
        data = r.text
        status_code = r.status_code

        if status_code == 200:
            return data
        else:
            return None

    except Exception as err:
        print(err)
        return None


def get_all_devices():
    try:
        url = address + 'device/getDevices'
        headers = {'Content-type': 'application/json'}

        r = requests.get(url=url, headers=headers)
        status_code = r.status_code

        if status_code == 200:
            device_list = json.loads(r.text)
            return device_list
        else:
            print(r.text)
            return None

    except Exception as err:
        print(err)
        return None
