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

# Check to see if device is already in the database
device_list = APIConnect.get_all_devices()
device_id = DeviceGetInformation.get_device_id(device_list)

# if device does not exist in database, then run method to create new entry
if device_id is None:
    print("Creating Database Entry...")
    new_device = Device.Device(None, DeviceGetInformation.get_host_name(), DeviceGetInformation.get_local_ip(), DeviceGetInformation.get_external_ip(), DeviceGetInformation.get_mac_address(), "1", "1", datetime.datetime.now())
    new_device_id = APIConnect.create_device(new_device)

    # Check to see if newly inserted DeviceId is valid
    if new_device_id is not None:
        print("Database Entry Inserted.")
    
    else:
        print("Could Not Insert Entry.")
    
# if device exists in database, update the database
else:
    print("Updating Existing Database Entry...")
    device = Device.Device(device_id, DeviceGetInformation.get_host_name(), DeviceGetInformation.get_local_ip(), DeviceGetInformation.get_external_ip(), DeviceGetInformation.get_mac_address(), "1", "1", datetime.datetime.now())

    is_updated = APIConnect.update_device(device)
    if is_updated:
        print("Database Entry Updated.")
    else:
        print("Could Not Update Entry.")
