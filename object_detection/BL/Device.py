import cv2
import base64
import numpy as np


# Constructors
class Device:

    def __init__(self, device_id, device_name, local_ip, external_ip, mac_address, last_update_date, company_id,
                 take_new_image, device_status_id, parking_lot_id):
        self.DeviceID = device_id
        self.DeviceName = device_name
        self.LocalIP = local_ip
        self.ExternalIP = external_ip
        self.MacAddress = mac_address
        self.LastUpdateDate = last_update_date
        self.CompanyID = company_id
        self.TakeNewImage = take_new_image
        self.DeviceStatusID = device_status_id
        self.ParkingLotID = parking_lot_id

    @staticmethod
    def constructEmpty():
        device = Device(None, None, None, None, None, None, None, None, None, None, )
        return device

    # Methods
    def decoder(obj):
        device = Device(obj['deviceID'], obj['deviceName'], obj['localIpAddress'], obj['externalIpAddress'],
                        obj['macAddress'], obj['lastUpdateDate'], obj['companyID'], obj['takeNewImage'],
                        obj['deviceStatusID'], obj['parkingLotID'])
        return device

    def fill(self):
        from DL.Device_dl import Device_dl
        device_dl = Device_dl(self.DeviceID, self.DeviceName, self.LocalIP, self.ExternalIP, self.MacAddress,
                              self.LastUpdateDate, self.CompanyID, self.TakeNewImage, self.DeviceStatusID,
                              self.ParkingLotID)
        return device_dl.fill()

    @staticmethod
    def getLocalIP():
        try:
            import socket as sc
            host_name = sc.gethostname()
            local_ip = sc.gethostbyname(host_name + ".local")
            return local_ip
        except Exception:
            return "Error"

    @staticmethod
    def getExternalIP():
        try:
            import urllib.request as ur
            external_ip = ur.urlopen('https://ident.me').read().decode('utf8')
            return external_ip
        except Exception:
            return "Error"

    @staticmethod
    def getMacAddress():
        try:
            import uuid
            mac_address = ':'.join(['{:02x}'.format((uuid.getnode() >> ele) & 0xff)
                                    for ele in range(0, 8 * 6, 8)][::-1])
            return mac_address
        except Exception:
            return "Error"

    @staticmethod
    def isConnected():
        try:
            import urllib.request as ur
            ur.urlopen('http://216.58.192.142', timeout=1)
            return True
        except Exception as err:
            return False

    def findDeviceFromList(self, devices=[]):
        try:
            current_mac_address = self.getMacAddress()
            for device in devices:
                if device.MacAddress == current_mac_address:
                    return device
            return None

        except Exception:
            # most likely to catch if list of devices is empty
            return None

    def getAllParkingSpots(self):
        from DL.Device_dl import Device_dl
        device_dl = Device_dl(self.DeviceID, self.DeviceName, self.LocalIP, self.ExternalIP, self.MacAddress,
                              self.LastUpdateDate, self.CompanyID, self.TakeNewImage, self.DeviceStatusID,
                              self.ParkingLotID)
        return device_dl.getAllParkingSpots()

    def updateDevice(self):
        from DL.Device_dl import Device_dl
        device_dl = Device_dl(self.DeviceID, self.DeviceName, self.LocalIP, self.ExternalIP, self.MacAddress,
                              self.LastUpdateDate, self.CompanyID, self.TakeNewImage, self.DeviceStatusID,
                              self.ParkingLotID)
        return device_dl.updateDevice()

    def createDevice(self):
        from DL.Device_dl import Device_dl
        device_dl = Device_dl(self.DeviceID, self.DeviceName, self.LocalIP, self.ExternalIP, self.MacAddress,
                              self.LastUpdateDate, self.CompanyID, self.TakeNewImage, self.DeviceStatusID,
                              self.ParkingLotID)
        return device_dl.createDevice()

    def updateAllSpots(self, parkingLots):
        from DL.Device_dl import Device_dl
        device_dl = Device_dl(self.DeviceID, self.DeviceName, self.LocalIP, self.ExternalIP, self.MacAddress,
                              self.LastUpdateDate, self.CompanyID, self.TakeNewImage, self.DeviceStatusID,
                              self.ParkingLotID)
        return device_dl.updateAllSpots(parkingLots)

    @staticmethod
    def takeImage():
        camera = cv2.VideoCapture(0)
        camera.set(3, 1280)
        camera.set(4, 720)
        camera.set(15, -8.0)
        ret, frame = camera.read()
        camera.release()
        if ret:
            t = np.arange(25, dtype=np.float64)
            s = base64.b64encode(frame)
            r = base64.decodebytes(s)
            q = np.frombuffer(r, dtype=np.float64)

            print(np.allclose(q, t))
        else:
            return None
