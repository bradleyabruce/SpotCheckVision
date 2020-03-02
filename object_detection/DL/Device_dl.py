from datetime import datetime

import BL
import json
from BL.Device import Device
from IoC.IoC import IoC


class Device_dl(Device):
    # 'pass' is used when no new methods need to be created
    def __init__(self, device_id, device_name, local_ip, external_ip, mac_address, last_update_date, company_id,
                 take_new_image, device_status_id, parking_lot_id):
        # we need to add the init for device
        super().__init__(device_id, device_name, local_ip, external_ip, mac_address, last_update_date, company_id,
                        take_new_image, device_status_id, parking_lot_id)

    # now we can start adding methods specific to the Device_dl class
    def fill(self):
        response = IoC.sendRequest('device/fill', self.DeviceID, 'json', 'POST')
        data = response.text

        if response.status_code == 200:
            device_json = json.loads(response.text)
            device = Device.decoder(device_json)
            return device
        else:
            return None

    def getAllParkingSpots(self):
        from BL.Spot import Spot
        parking_spots = []
        response = IoC.sendRequest('device/getParkingSpotsByDeviceId', self.DeviceID, 'json', 'POST')

        if response.status_code == 200:
            parking_spot_json = json.loads(response.text)
            for p in parking_spot_json:
                parking_spot = Spot.decoder(p)
                parking_spots.append(parking_spot)
            return parking_spots
        else:
            return None

    def updateDevice(self):
        bodyData = {'deviceID': self.DeviceID, 'deviceName': self.DeviceName, 'localIpAddress': self.LocalIP,
                'externalIpAddress': self.ExternalIP, 'macAddress': self.MacAddress,
                'lastUpdateDate': str(self.LastUpdateDate), 'companyID': self.CompanyID,
                    'deviceStatusID': self.DeviceStatusID, 'parkingLotID': self.ParkingLotID}
        response = IoC.sendRequest('device/updateDevice', bodyData, 'json', 'POST')

        if response.status_code == 200:
            return True
        else:
            return False

    def createDevice(self):
        bodyData = {'deviceID': self.DeviceID, 'deviceName': self.DeviceName, 'localIpAddress': self.LocalIP,
                    'externalIpAddress': self.ExternalIP, 'macAddress': self.MacAddress,
                    'lastUpdateDate': str(self.LastUpdateDate), 'companyID': self.CompanyID,
                    'deviceStatusID': self.DeviceStatusID, 'parkingLotID': self.ParkingLotID}
        response = IoC.sendRequest('device/createDevice', bodyData, 'json', 'POST')

        if response.status_code == 200:
            return response.text    # return new device id
        else:
            return None

    def updateAllSpots(self, parkingSpots):
        from BL.Spot import Spot
        now = datetime.datetime.now()
        date_time = now.strftime("%Y-%m-%d %H:%M:%S")

        bodyData = []
        for spot in parkingSpots:
            bodyData.append({'spotId': spot.SpotID, 'floorNum': '0', 'lotId': '0', 'isOpen': spot.IsOpen, 'deviceId': '0',
                         'topLeftXCoordinate': '0', 'topLeftYCoordinate': '0', 'bottomRightXCoordinate': '0',
                         'bottomRightYCoordinate': '0', 'updateDate': date_time})

        response = IoC.sendRequest('parkingSpot/updateMultipleParkingSpotsAvailabilityBySpotId', bodyData, 'json',
                                   'POST')

        if response.status_code == 200:
            return True
        else:
            return False

