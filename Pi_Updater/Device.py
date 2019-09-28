class Device:
    def __init__(self, device_id, device_name, local_ip, external_ip, mac_address, lot_id, floor_number, last_update_date, company_id):
        self.DeviceId = device_id
        self.DeviceName = device_name
        self.LocalIpAddress = local_ip
        self.ExternalIpAddress = external_ip
        self.MacAddress = mac_address
        self.LotId = lot_id
        self.FloorNumber = floor_number
        self.LastUpdateDate = last_update_date
        self.CompanyID = company_id
