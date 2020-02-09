class Device:
    def __init__(self, device_id, device_name, local_ip, external_ip, mac_address, last_update_date, company_id, take_new_image):
        self.DeviceID = device_id
        self.DeviceName = device_name
        self.LocalIpAddress = local_ip
        self.ExternalIpAddress = external_ip
        self.MacAddress = mac_address
        self.LastUpdateDate = last_update_date
        self.CompanyID = company_id
        self.TakeNewImage = take_new_image


def decoder(obj):
    device = Device(obj['deviceID'], obj['deviceName'], obj['localIpAddress'], obj['externalIpAddress'], obj['macAddress'], obj['lastUpdateDate'], obj['companyID'], obj['takeNewImage'])
    return device
