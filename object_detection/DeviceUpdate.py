import time
import sys
import datetime
import ApiConnect
import DeviceGetInformation
import Device


def initialize_raspberry_pi():
    # Check to see if device is connected to network
    is_connected = DeviceGetInformation.is_connected()
    connection_try_count = 0

    while not is_connected:
        print("Connection Attempt: " + str(connection_try_count + 1) + ".")
        time.sleep(5)
        connection_try_count += 1
        is_connected = DeviceGetInformation.is_connected()

        if connection_try_count == 10:
            print("Failed to Connect to Internet.")
            return False

    # Check to see if device is already in the database by getting all devices and verifying the DeviceID
    device_list = ApiConnect.get_all_devices()
    device_from_db = DeviceGetInformation.get_device_from_list(device_list)

    # if device does not exist in database, then run method to create new entry
    if device_from_db is None:
        print("Creating Database Entry...")
        new_device = Device.Device(None, DeviceGetInformation.get_host_name(), DeviceGetInformation.get_local_ip(),
                                   DeviceGetInformation.get_external_ip(), DeviceGetInformation.get_mac_address(), datetime.datetime.now(), None, True)
        new_device_id = ApiConnect.create_device(new_device)
        new_device.DeviceID = new_device_id

        # Check to see if newly inserted DeviceId is valid
        if new_device.DeviceId is not None:
            print("Database Entry Inserted.")
            return new_device

        else:
            print("Could Not Insert Entry.")
            return None

    # if device exists in database, update the database
    else:
        print("Updating Existing Database Entry...")
        updated_device = Device.Device(device_from_db.DeviceID, DeviceGetInformation.get_host_name(), DeviceGetInformation.get_local_ip(),
                               DeviceGetInformation.get_external_ip(), DeviceGetInformation.get_mac_address(), datetime.datetime.now(), device_from_db.CompanyID, device_from_db.TakeNewImage)

        is_updated = ApiConnect.update_device(updated_device)
        if is_updated:
            print("Database Entry Updated.")
            return updated_device
        else:
            print("Could Not Update Entry.")
            return None
