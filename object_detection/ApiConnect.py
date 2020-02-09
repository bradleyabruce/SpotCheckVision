import requests
import Spot
import json
import datetime
import Device

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
                parking_spot = Spot.decoder(p)
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
        body = {'deviceID': device.DeviceID, 'deviceName': device.DeviceName, 'localIpAddress': device.LocalIpAddress,
                'externalIpAddress': device.ExternalIpAddress, 'macAddress': device.MacAddress, 'lastUpdateDate': str(device.LastUpdateDate), 'companyID': device.CompanyID}
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
                'externalIpAddress': device.ExternalIpAddress, 'macAddress': device.MacAddress, 'lastUpdateDate': str(device.LastUpdateDate),
                'companyID': device.CompanyID, 'takeNewImage': device.TakeNewImage}
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
        devices = []

        url = address + 'device/getDevices'
        headers = {'Content-type': 'application/json'}

        r = requests.get(url=url, headers=headers)
        status_code = r.status_code

        if status_code == 200:
            device_json = json.loads(r.text)
            for d in device_json:
                device = Device.decoder(d)
                devices.append(device)
            return devices
        else:
            print(r.text)
            return None

    except Exception as err:
        print(str(err) + " from ApiConnect.get_all_devices")
        return None


def update_parking_spots(parking_spots):
    try:
        now = datetime.datetime.now()
        date_time = now.strftime("%Y-%m-%d %H:%M:%S")

        url = address + 'parkingSpot/updateMultipleParkingSpotsAvailabilityBySpotId'
        body = []
        for spot in parking_spots:
            body.append({'spotId': spot.SpotID, 'floorNum': '0', 'lotId': '0', 'isOpen': spot.IsOpen, 'deviceId': '0', 'topLeftXCoordinate': '0', 'topLeftYCoordinate': '0', 'bottomRightXCoordinate': '0', 'bottomRightYCoordinate': '0', 'updateDate': date_time})
        headers = {'Content-type': 'application/json'}
        r = requests.post(url=url, headers=headers, data=json.dumps(body))
        data = r.text
        status_code = r.status_code

        if status_code == 200:
            return True
        else:
            return False

    except Exception as err:
        print(str(err) + " from ApiConnect.update_parking_spots")
        return False
