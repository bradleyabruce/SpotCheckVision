# ************************************************************************
# Raspberry Pi Parking Spot Detector Camera using TensorFlow Object Detection API
#
# The framework is based off the Object_detection_picamera script located here:
# https://github.com/EdjeElectronics/TensorFlow-Object-Detection-on-the-Raspberry-Pi/blob/master/Object_detection_picamera.py
# *************************************************************************

import os
import cv2
import numpy as np
import tensorflow as tf
import sys
import time
import Initialize
from BL import Device
import DeviceStatusEnum

# **************** Run scripts to Update Raspberry Pi ******************* #
device = Initialize.initialize_raspberry_pi()
if device is not None:
    print("Raspberry Pi initialized.")
else:
    print("Raspberry Pi could not be initialized.")
    sys.exit()

# *********** Initialize TensorFlow model that will be deployed ************ #
# Set up constants
IM_WIDTH = 1280
IM_HEIGHT = 720
SPOT_CHANGE_LENGTH = 30
API_TRIGGER_LENGTH = 180    # 60 is roughly 10 seconds on windows
camera_type = 'picamera'

# This is needed since the working directory is the object_detection folder.
sys.path.append('..')

# Name of the directory containing the object detection module we're using
MODEL_NAME = 'ssd_inception_v2_coco_2018_01_28'

# Grab path to current working directory
CWD_PATH = os.getcwd()

# Path to frozen detection graph .pb file, which contains the model that is used for detection
PATH_TO_CKPT = os.path.join(CWD_PATH, MODEL_NAME, 'frozen_inference_graph.pb')

# Path to label map file
PATH_TO_LABELS = os.path.join(CWD_PATH, 'data', 'mscoco_label_map.pbtxt')

from utils import label_map_util

# Specify the number of objects our model can detect
NUM_CLASSES = 90

# Load the label map.
# Label maps map indices to category names, so that when the convolution
# network predicts `5`, we know that this corresponds to `airplane`.
# Here we use internal utility functions, but anything that returns a
# dictionary mapping integers to appropriate string labels would be fine
label_map = label_map_util.load_labelmap(PATH_TO_LABELS)
categories = label_map_util.convert_label_map_to_categories(label_map, max_num_classes=NUM_CLASSES,
                                                            use_display_name=True)
category_index = label_map_util.create_category_index(categories)

# We need to limit the scope of the category_index to detect less objects
required_index_list = [3, 4, 8]

# Load the TensorFlow model into memory.
detection_graph = tf.Graph()
with detection_graph.as_default():
    od_graph_def = tf.GraphDef()
    with tf.io.gfile.GFile(PATH_TO_CKPT, 'rb') as fid:
        serialized_graph = fid.read()
        od_graph_def.ParseFromString(serialized_graph)
        tf.import_graph_def(od_graph_def, name='')

    sess = tf.Session(graph=detection_graph)

# ************** Define input and output for the object detection classifier *************** #
# Input tensor is the image
image_tensor = detection_graph.get_tensor_by_name('image_tensor:0')

# Output tensors are the detection boxes, scores, and classes
detection_boxes = detection_graph.get_tensor_by_name('detection_boxes:0')

# Each score represents level of confidence for each of the objects.
# The score is shown on the result image, together with the class label.
detection_scores = detection_graph.get_tensor_by_name('detection_scores:0')
detection_classes = detection_graph.get_tensor_by_name('detection_classes:0')

# Number of objects detected
num_detections = detection_graph.get_tensor_by_name('num_detections:0')

# *********************** Initialize other parameters **************************** #
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
            frame = device.imageProcessing(frame, parking_spots, sess, detection_boxes, detection_scores,
                                                  detection_classes,
                                                  num_detections, image_tensor, category_index, required_index_list,
                                                  IM_WIDTH, IM_HEIGHT, SPOT_CHANGE_LENGTH, api_counter, API_TRIGGER_LENGTH)

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