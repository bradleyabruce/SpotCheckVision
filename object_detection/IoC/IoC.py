import requests
import json


class IoC(object):
    def __int__(self):
        self._DeviceID = None

    # DeviceID
    @property
    def DeviceID(self):
        return self._DeviceID

    @DeviceID.setter
    def DeviceID(self, value):
        self._DeviceID = value

    # Api Address
    @staticmethod
    def ApiAddress():
        return "http://173.91.255.135:8080/SpotCheckServer-2.1.8.RELEASE/"

    # Methods
    @staticmethod
    def sendRequest(address, bodyData, headerType, type):
        try:
            if headerType == 'json':
                headerData = {'Content-type': 'application/json'}
            if type == 'GET':
                url = IoC.ApiAddress() + address
                response = requests.get(url=url,headers=headerData)
                return response
            elif type == 'POST':
                url = IoC.ApiAddress() + address
                body = bodyData
                response = requests.post(url=url, headers=headerData, data=json.dumps(body))
                return response
        except Exception as err:
            return None

    @staticmethod
    def getAllDevices():
        try:
            from BL.Device import Device
            devices = []
            response = IoC.sendRequest('device/getDevices', None, 'json', 'GET')

            status_code = response.status_code
            if status_code == 200:
                device_json = json.loads(response.text)
                for d in device_json:
                    device = Device.decoder(d)
                    devices.append(device)
                return devices
            else:
                return None
        except Exception as err:
            return None

