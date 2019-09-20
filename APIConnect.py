import requests
import Device


def update_device(device):

    try:
        url = 'http://localhost:8080/device/updateDevice'
        json = {'deviceId': device.DeviceId, 'deviceName': device.DeviceName, 'localIpAddress': device.LocalIpAddress, 'externalIpAddress': device.ExternalIpAddress, 'macAddress': device.MacAddress, 'lotId': device.LotId, 'floorNumber': device.FloorNumber, 'lastUpdateDate': str(device.LastUpdateDate)}
        headers = {'Content-type': 'application/json'}

        r = requests.post(url=url, headers=headers, json=json)
        data = r.text
        # print(data)
        if data == 'updateDevice - Success':
            return True
        else:
            return False

    # Catch any errors and return false
    except Exception as err:
        # print(err)
        return False
