import time
import sys
import datetime
import APIConnect
import DeviceGetInformation
import Device


# Check to see if device is connected to network
isConnected = DeviceGetInformation.is_connected()
connectionTryCount = 0

while not isConnected:
    print("Connection Attempt: " + str(connectionTryCount + 1))
    time.sleep(5)
    connectionTryCount += 1
    isConnected = DeviceGetInformation.is_connected()

    if connectionTryCount == 10:
        print("Failed to Connect")
        sys.exit()

# Get information to send to database
device = Device.Device("1", DeviceGetInformation.get_host_name(), DeviceGetInformation.get_local_ip(), DeviceGetInformation.get_external_ip(), DeviceGetInformation.get_mac_address(), "1", "1", datetime.datetime.now())

is_updated = APIConnect.update_device(device)
if is_updated:
    print("Update Complete.")
else:
    print("Error Caused Update To Fail.")

