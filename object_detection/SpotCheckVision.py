# ************************************************************************
# Raspberry Pi Parking Spot Detector Camera using TensorFlow Object Detection API
#
# The framework is based off the Object_detection_picamera script located here:
# https://github.com/EdjeElectronics/TensorFlow-Object-Detection-on-the-Raspberry-Pi/blob/master/Object_detection_picamera.py
# *************************************************************************


import cv2
import numpy as np

import sys
import time
import Initialize
from BL import Device
import DeviceStatusEnum

# **************** Run scripts to Update Raspberry Pi ******************* #
from IoC.IoC import IoC

device = Initialize.initialize_raspberry_pi()
if device is not None:
    print("Raspberry Pi initialized.")
else:
    print("Raspberry Pi could not be initialized.")
    sys.exit()

# Set up constants
IM_WIDTH = 1280
IM_HEIGHT = 720
SPOT_CHANGE_LENGTH = 30
API_TRIGGER_LENGTH = 180  # 60 is roughly 10 seconds on windows
drawVisualization = False

# Initialize frame rate calculation
frame_rate_calc = 1
freq = cv2.getTickFrequency()
font = cv2.FONT_HERSHEY_SIMPLEX

# ******************** Spot Check Undeployed Wait Function **************************** #
undeployedCheckCount = 0
while device.DeviceStatusID is DeviceStatusEnum.DeviceStatus.Undeployed.value:
    time.sleep(3)
    device = device.fill()
    undeployedCheckCount += 1
    if device.TakeNewImage:
        image_encoded_string = device.takeImage()
        if image_encoded_string is not None:
            print(image_encoded_string)
        else:
            print("Error encoding image.")
            sys.exit()
    else:
        if undeployedCheckCount % 10 == 0 or undeployedCheckCount == 1:
            print("Awaiting Deployment... (" + str(undeployedCheckCount) + " checks performed)")

# Get list of all parking spots
# We can assume there will always be at least one spot after deployment
parking_spots = device.getAllParkingSpots()

if parking_spots is None:
    print("Error retrieving parking spots for device.")
    sys.exit()
elif len(parking_spots) < 1:
    print("No spots available for this device.")
    sys.exit()
else:
    print(str(len(parking_spots)) + " Parking spot(s) linked to current device.")

# *********** Initialize TensorFlow model that will be deployed ************ #
tensorFlowList = IoC.returnTensorFlowVariables()

# ******************* Initialize camera and perform object detection ********************* #
global api_counter
api_counter = 0
camera = cv2.VideoCapture(0)
try:
    # Initialize camera and grab reference to the raw capture
    while True:
        api_counter += 1
        ret, frame = camera.read()
        # if image was successfully taken
        if ret:
            t1 = cv2.getTickCount()
            frame = cv2.resize(frame, (IM_WIDTH, IM_HEIGHT))
            frame = np.asarray(frame)
            frame.setflags(write=1)

            # Pass frame into image proccessing function
            frame = device.imageProcessing(frame, parking_spots, tensorFlowList[0], tensorFlowList[1], tensorFlowList[2],
                                           tensorFlowList[3], tensorFlowList[4], tensorFlowList[5], tensorFlowList[6],tensorFlowList[7],
                                           IM_WIDTH, IM_HEIGHT, SPOT_CHANGE_LENGTH, api_counter, API_TRIGGER_LENGTH, drawVisualization)

            # Draw FPS
            cv2.putText(frame, "FPS: {0:.2f}".format(frame_rate_calc), (8, 25), font, .7, (0, 0, 0), 2, cv2.LINE_AA)
            cv2.putText(frame, "FPS: {0:.2f}".format(frame_rate_calc), (8, 25), font, .7, (255, 255, 255), 1,
                        cv2.LINE_AA)

            # All the results have been drawn on the frame, so it's time to display it.
            cv2.imshow('SpotCheck Vision', frame)

            # FPS calculation
            t2 = cv2.getTickCount()
            time1 = (t2 - t1) / freq
            frame_rate_calc = 1 / time1

            if cv2.waitKey(1) == ord('q'):
                break
finally:
    camera.release()

cv2.destroyAllWindows()
