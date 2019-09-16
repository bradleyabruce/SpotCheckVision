import time
import sys
import datetime
import APIConnect
import DeviceGetInformation


# Check to see if device is connected to network
isConnected = DeviceGetInformation.is_connected()
connectionTryCount = 0

while not isConnected:
    time.sleep(5)
    connectionTryCount += 1
    isConnected = DeviceGetInformation.is_connected()

    if connectionTryCount == 10:
        print("Failed to Connect")
        sys.exit()

# Get information to send to database
pi_id = 1
# deviceName = DeviceGetInformation.gethostname()
local_ip = DeviceGetInformation.get_local_ip()
external_ip = DeviceGetInformation.get_external_ip()
mac_address = DeviceGetInformation.get_mac_address()
# LotID = 1
# FloorNumber = 1
update_date = datetime.datetime.now()

is_updated = APIConnect.update_device(pi_id, local_ip, external_ip, mac_address, update_date)
if is_updated:
    print("success!")
else:
    print("error")

