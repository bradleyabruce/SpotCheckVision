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
import DeviceStatusEnum
from IoC.IoC import IoC

# **************** Run scripts to Update Raspberry Pi ******************* #
device = Initialize.initialize_raspberry_pi()
if device is not None:
    print("SpotCheck Vision initialized.")
else:
    # most likely isnt connected to the internet
    print("SpotCheck Vision could not be initialized.")
    sys.exit()

# Set up constants
IM_WIDTH = 1280
IM_HEIGHT = 720
SPOT_UPDATE_AVAILABILITY_LENGTH = 20    # 20 consecutive frames until a spot can change from opened to closed
SPOT_UPDATE_API_LENGTH = 180    # 60 is roughly 10 seconds on windows
drawVisualization = False

# Initialize frame rate calculation
frame_rate_calc = 1
freq = cv2.getTickFrequency()
font = cv2.FONT_HERSHEY_SIMPLEX

# temp variables
undeployedCheckCount = 0
api_counter = 0
refreshVariables = True

# Initialize tensorflow model
tensorFlowList = IoC.returnTensorFlowVariables()

# We are going to loop forever, constantly checking for the status to be deployed or undeployed and reacting accordingly
while True:
    if refreshVariables:
        device = device.fill()

    # ************* Spot Check Undeployed Function ****************** #
    if device.DeviceStatusID is DeviceStatusEnum.DeviceStatus.Undeployed.value:
        refreshVariables = True
        api_counter = 0
        time.sleep(3)
        undeployedCheckCount += 1
        if device.TakeNewImage:
            if device.saveImage():  # the API will ensure that TakeNewImage is set back to False
                print("Image saved.. awaiting further deployment.")
            else:
                print("Error encoding image.")
                sys.exit()
        else:
            if undeployedCheckCount % 10 == 0 or undeployedCheckCount == 1:
                print("Awaiting Deployment... (" + str(undeployedCheckCount) + " check(s) performed)")

    # ************** Spot Check Deployed Function ******************** #
    elif device.DeviceStatusID is DeviceStatusEnum.DeviceStatus.Deployed.value:
        refreshVariables = False
        undeployedCheckCount = 0

        # Get list of all parking spots, we can assume there will always be at least 1
        parking_spots = device.getAllParkingSpots()

        # ******************* Initialize camera and perform object detection ********************* #
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
                                           IM_WIDTH, IM_HEIGHT, SPOT_UPDATE_AVAILABILITY_LENGTH, api_counter, SPOT_UPDATE_API_LENGTH, drawVisualization)

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
