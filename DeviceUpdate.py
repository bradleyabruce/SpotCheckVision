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

# Check to see if DeviceID has been set
# If it has not been set, then run the create script
device_id = DeviceGetInformation.get_device_id()
if device_id == "":
    print("Creating Database Entry")
    new_device = Device.Device(None, DeviceGetInformation.get_host_name(), DeviceGetInformation.get_local_ip(), DeviceGetInformation.get_external_ip(), DeviceGetInformation.get_mac_address(), "1", "1", datetime.datetime.now())
    new_device_id = APIConnect.create_device(new_device)
    
    #write new device id to text file for next time
    if new_device_id != "":
        DeviceGetInformation.write_device_id(new_device_id)
        print("Creation Complete.")
    
    else:
        print("Could Not Create Entry.")
    
# If device_id exists, then simply update the existing entry
else:   
    device = Device.Device(device_id, DeviceGetInformation.get_host_name(), DeviceGetInformation.get_local_ip(), DeviceGetInformation.get_external_ip(), DeviceGetInformation.get_mac_address(), "1", "1", datetime.datetime.now())

    is_updated = APIConnect.update_device(device)
    if is_updated:
        print("Update Complete.")
    else:
        print("Error Caused Update To Fail.")

