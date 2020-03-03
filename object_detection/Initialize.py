import time
import datetime
from BL import Device
from IoC.IoC import IoC


def initialize_raspberry_pi():

    device = Device.Device.constructEmpty()
    # Attempt to connect to the network
    is_connected = Device.Device.isConnected()
    connection_try_count = 0

    while not is_connected:
        print("Connection Attempt: " + str(connection_try_count + 1) + ".")
        time.sleep(5)
        connection_try_count += 1
        is_connected = Device.Device.isConnected()

    # Check to see if device is already in the database by getting all devices and verifying the DeviceID
    device_list = IoC.getAllDevices()
    device = device.findDeviceFromList(device_list)

    # if device does not exist in database, then run method to create new entry
    if device is None:
        print("Creating Database Entry...")
        new_device = Device.Device(None, "Camera", Device.Device.getLocalIP(), Device.Device.getExternalIP(),
                                   Device.Device.getMacAddress(), datetime.datetime.now(), None, True)
        new_device_id = new_device.createDevice()
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
        updated_device = Device.Device(device.DeviceID, device.DeviceName, Device.Device.getLocalIP(),
                                       Device.Device.getExternalIP(), Device.Device.getMacAddress(),
                                       datetime.datetime.now(), device.CompanyID, device.TakeNewImage,
                                       device.DeviceStatusID, device.ParkingLotID)

        is_updated = updated_device.updateDevice()
        if is_updated:
            print("Database Entry Updated.")
            return updated_device
        else:
            print("Could Not Update Entry.")
            return None
