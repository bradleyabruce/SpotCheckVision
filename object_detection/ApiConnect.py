import requests
import ParkingSpot
import json

address = "http://173.91.255.135:8080/SpotCheckServer-2.1.8.RELEASE/"


def get_parking_spots_by_device_id(device_id):

    parking_spots = []

    try:
        url = address + 'parkingSpot/getParkingSpotsByDeviceId'
        headers = {'Content-type': 'application/json'}
        body = str(device_id)

        r = requests.post(url=url, headers=headers, data=json.dumps(body))
        status_code = r.status_code

        if status_code == 200:
            parking_spot_json = json.loads(r.text)
            for p in parking_spot_json:
                parking_spot = ParkingSpot.decoder(p)
                parking_spots.append(parking_spot)
            return parking_spots
        else:
            print(r.text)
            return None

    except Exception as err:
        print(str(err) + " from ApiConnect.get_parking_spots_by_device_id")
        return None


def update_device(device):
    try:
        url = address + 'device/updateDevice'
        body = {'deviceId': device.DeviceId, 'deviceName': device.DeviceName, 'localIpAddress': device.LocalIpAddress,
                'externalIpAddress': device.ExternalIpAddress, 'macAddress': device.MacAddress, 'lotId': device.LotId,
                'floorNumber': device.FloorNumber, 'lastUpdateDate': str(device.LastUpdateDate)}
        headers = {'Content-type': 'application/json'}

        r = requests.post(url=url, headers=headers, data=json.dumps(body))
        data = r.text
        status_code = r.status_code

        if status_code == 200:
            return True
        else:
            print(data)
            return False
    except Exception as err:
        print(str(err) + " from ApiConnect.update_device")
        return False


def create_device(device):
    try:
        url = address + 'device/createDevice'
        body = {'deviceName': device.DeviceName, 'localIpAddress': device.LocalIpAddress,
                'externalIpAddress': device.ExternalIpAddress, 'macAddress': device.MacAddress, 'lotId': device.LotId,
                'floorNumber': device.FloorNumber, 'lastUpdateDate': str(device.LastUpdateDate),
                'companyId': device.CompanyID}
        headers = {'Content-type': 'application/json'}

        r = requests.post(url=url, headers=headers, data=json.dumps(body))
        data = r.text
        status_code = r.status_code

        if status_code == 200:
            return data
        else:
            return None

    except Exception as err:
        print(str(err) + " from ApiConnect.create_device")
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
        print(str(err) + " from ApiConnect.get_all_devices")
        return None
