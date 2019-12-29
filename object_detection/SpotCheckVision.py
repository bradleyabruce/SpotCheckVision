# ************************************************************************
# Raspberry Pi Parking Sport Detector Camera using TensorFlow Object Detection API
#
# Project: Spot Check
# Author: Bradley Bruce
# Based on code from: Evan Juras
# Date: 11/29/2019
# Description:
#
# This script implements a "vehicle detector" that sends a signal to an API when
# A vehicle is detected within a preset 'Parking Spot'. It takes video frames from
# a Pi camera, passes them through a TensorFlow object detection model,
# determines if a car, truck, or motorcycle has been detected in the image,
# checks the location of the vehicle in the frame, updates the correct parking spot
# if a car has been detected there
#
# The framework is based off the Object_detection_picamera.py script located here:
# https://github.com/EdjeElectronics/TensorFlow-Object-Detection-on-the-Raspberry-Pi/blob/master/Object_detection_picamera.py
# ***********************************************************************

import os
import cv2
import numpy as np
from picamera.array import PiRGBArray
from picamera import PiCamera
import tensorflow as tf
import sys
import datetime

import ParkingSpot
import ApiConnect
import DeviceUpdate


# **************** Run scripts to Update Raspberry Pi ******************* #


device_id = DeviceUpdate.initialize_raspberry_pi(1)
if device_id is not None:
    print("Raspberry Pi initialized.")
else:
    print("Raspberry Pi could not be initialized.")
    sys.exit()


# *********** Initialize TensorFlow model that will be deployed ************ #


# Set up constants
IM_WIDTH = 1280
IM_HEIGHT = 720
SPOT_CHANGE_LENGTH = 30
API_TRIGGER_LENGTH = 120
camera_type = 'picamera'

# This is needed since the working directory is the object_detection folder.
sys.path.append('..')

# Name of the directory containing the object detection module we're using
MODEL_NAME = 'ssdlite_mobilenet_v2_coco_2018_05_09'

# Grab path to current working directory
CWD_PATH = os.getcwd()

# Path to frozen detection graph .pb file, which contains the model that is used for detection
PATH_TO_CKPT = os.path.join(CWD_PATH, MODEL_NAME, 'frozen_inference_graph.pb')

# Path to label map file
PATH_TO_LABELS = os.path.join(CWD_PATH, 'data', 'mscoco_label_map.pbtxt')

from utils import label_map_util
from utils import visualization_utils as vis_util

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
unused_index_list = []

for index in category_index:
    if index not in required_index_list:
        unused_index_list.append(index)

for index in unused_index_list:
    category_index.pop(index, None)

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

# Get list of all parking spots
parking_spots = ApiConnect.get_parking_spots_by_device_id(device_id)

if parking_spots is None:
    print("Error retrieving parking spots for device.")
    sys.exit()
elif len(parking_spots) < 1:
    print("No spots available for this device.")
    sys.exit()
else:
    print(str(len(parking_spots)) + " Parking spot(s) linked to current device.")

api_counter = 0


# ********************* Spot Check Vision Function ************************ #


def spot_check_vision(current_frame):
    global api_counter
    api_counter += 1

    frame_expanded = np.expand_dims(current_frame, axis=0)

    # Perform the actual detection by running the model with the image as input
    (boxes, scores, classes, num) = sess.run(
        [detection_boxes, detection_scores, detection_classes, num_detections],
        feed_dict={image_tensor: frame_expanded})

    # Draw the results of the detection
    # vis_util.visualize_boxes_and_labels_on_image_array(current_frame, np.squeeze(boxes),
                                                       # np.squeeze(classes).astype(np.int32), np.squeeze(scores),
                                                       # category_index, use_normalized_coordinates=True,
                                                       # line_thickness=0, min_score_thresh=0.45)

    # Draw parking spots labels
    for p in parking_spots:
        top_left = (p.TopLeftXCoordinate, p.TopLeftYCoordinate)
        cv2.putText(frame, "SpotID: " + str(p.ParkingSpotID), (top_left[0], top_left[1] - 5), font, .7, (0, 0, 0),
                    2, cv2.LINE_AA)
        cv2.putText(frame, "SpotID: " + str(p.ParkingSpotID), (top_left[0], top_left[1] - 5), font, .7,
                    (255, 255, 255), 1, cv2.LINE_AA)

    # classes array is an array of all detected objects and what they have been classified as
    # the boxes array holds coordinates of detected objects that we can use
    # boxes[0][objectIndex] variable holds coordinates of detected objects as (ymin, xmin, ymax, xmax)

    # Get all detected vehicles
    object_coordinates = []
    detected_object_index = 0
    for detected_object in classes[0]:
        if detected_object in required_index_list:
            # Get center of object
            x = int(((boxes[0][detected_object_index][1] + boxes[0][detected_object_index][3]) / 2) * IM_WIDTH)
            y = int(((boxes[0][detected_object_index][0] + boxes[0][detected_object_index][2]) / 2) * IM_HEIGHT)
            object_coordinates.append((x, y))
            # cv2.circle(current_frame, (x, y), 7, (0, 0, 255), -1)
        detected_object_index += 1

    # Run calculations to determine if a spot is available, occupied, or currently changing
    for spot in parking_spots:
        spot_changed = False
        object_detected = False
        for coord in object_coordinates:

            # If an object is detected within the spot and the spot is currently open
            if (spot.TopLeftXCoordinate < coord[0]) and (spot.BottomRightXCoordinate > coord[0]) and (
                    spot.TopLeftYCoordinate < coord[1]) and (spot.BottomRightYCoordinate > coord[1])\
                    and spot.IsOpen is True:
                object_detected = True
                spot_changed = True
                spot.OccupiedCounter += 1
                spot.EmptyCounter = 0
                 #print("Spot ID: " + str(spot.ParkingSpotID) + " " + "Occupied Counter: " + str(spot.OccupiedCounter) + " " + "Empty Counter: " + str(spot.EmptyCounter) + " " + "Is Spot Open?: " + str(spot.IsOpen))
                if spot.OccupiedCounter is SPOT_CHANGE_LENGTH:
                    spot.IsOpen = False
                    spot_changed = False
                break

            # If an object is detected within the spot and the spot is currently taken
            if (spot.TopLeftXCoordinate < coord[0]) and (spot.BottomRightXCoordinate > coord[0]) and (
                    spot.TopLeftYCoordinate < coord[1]) and (spot.BottomRightYCoordinate > coord[1]) \
                    and spot.IsOpen is False:
                object_detected = True
                spot_changed = False
                spot.OccupiedCounter = 0
                spot.EmptyCounter = 0
                # print("Spot ID: " + str(spot.ParkingSpotID) + " " + "Occupied Counter: " + str(spot.OccupiedCounter) + " " + "Empty Counter: " + str(spot.EmptyCounter) + " " + "Is Spot Open?: " + str(spot.IsOpen))
                break
        # If none of the objects were found in the spot and the spot is currently open
        if object_detected is False and spot.IsOpen is True:
            spot_changed = False
            spot.OccupiedCounter = 0
            spot.EmptyCounter = 0
            # print("Spot ID: " + str(spot.ParkingSpotID) + " " + "Occupied Counter: " + str(spot.OccupiedCounter) + " " + "Empty Counter: " + str(spot.EmptyCounter) + " " + "Is Spot Open?: " + str(spot.IsOpen))

        # If none of the objects were found in the spot and the spot is currently taken ie. Change
        if object_detected is False and spot.IsOpen is False:
            spot_changed = True
            spot.EmptyCounter += 1
            spot.OccupiedCounter = 0
            # print("Spot ID: " + str(spot.ParkingSpotID) + " " + "Occupied Counter: " + str(spot.OccupiedCounter) + " " + "Empty Counter: " + str(spot.EmptyCounter) + " " + "Is Spot Open?: " + str(spot.IsOpen))
            if spot.EmptyCounter is SPOT_CHANGE_LENGTH:
                spot.IsOpen = True
                spot_changed = False

        # Draw parking space lines based on if it is occupied, available, or changing
        top_left = (spot.TopLeftXCoordinate, spot.TopLeftYCoordinate)
        bottom_right = (spot.BottomRightXCoordinate, spot.BottomRightYCoordinate)
        if spot.IsOpen is True and spot_changed is False:
            cv2.rectangle(current_frame, top_left, bottom_right, (0, 255, 0), 2)
        if spot.IsOpen is True and spot_changed is True:
            cv2.rectangle(current_frame, top_left, bottom_right, (0, 255, 0), 2)
            if spot.OccupiedCounter % 2 == 0:
                cv2.rectangle(current_frame, (top_left[0] + 2, top_left[1] + 2), (bottom_right[0] - 2, bottom_right[1] - 2), (0, 255, 255), 2)
        if spot.IsOpen is False and spot_changed is False:
            cv2.rectangle(current_frame, top_left, bottom_right, (0, 0, 255), 2)
        if spot.IsOpen is False and spot_changed is True:
            cv2.rectangle(current_frame, top_left, bottom_right, (0, 0, 255), 2)
            if spot.EmptyCounter % 2 == 0:
                cv2.rectangle(current_frame, (top_left[0] + 2, top_left[1] + 2), (bottom_right[0] - 2, bottom_right[1] - 2), (0, 255, 255), 2)

    total_spots = 0
    open_spots = 0

    for spot in parking_spots:
        total_spots += 1
        if spot.IsOpen:
            open_spots += 1

    cv2.putText(frame, "Open Spots: " + str(open_spots) + "/" + str(total_spots), (8, 50), font, .7, (0, 0, 0), 2, cv2.LINE_AA)
    cv2.putText(frame, "Open Spots: " + str(open_spots) + "/" + str(total_spots), (8, 50), font, .7, (255, 255, 255), 1, cv2.LINE_AA)

    # Send parking spot data to API
    if api_counter % API_TRIGGER_LENGTH == 0:
        api_result = ApiConnect.update_parking_spots(parking_spots)
        now = datetime.datetime.now()
        date_time = now.strftime("%m/%d/%Y %H:%M:%S")
        if api_result:
            print("Database updated at: " + str(date_time) + ".")
        else:
            print("Database failed to update. Application exit at " + str(date_time) + ".")
            sys.exit()

    return current_frame


# ******************* Initialize camera and perform object detection ********************* #


if camera_type == 'picamera':
    # Initialize Picamera and grab reference to the raw capture
    camera = PiCamera()
    camera.resolution = (IM_WIDTH, IM_HEIGHT)
    camera.framerate = 10
    rawCapture = PiRGBArray(camera, size=(IM_WIDTH, IM_HEIGHT))
    rawCapture.truncate(0)

    # Continuously capture frames and perform object detection on them
    for frame1 in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):

        t1 = cv2.getTickCount()

        # Acquire frame and expand frame dimensions to have shape: [1, None, None, 3]
        # i.e. a single-column array, where each item in the column has the pixel RGB value
        # frame = frame1.array
        frame = np.copy(frame1.array)
        frame.setflags(write=1)

        # Pass frame into pet detection function
        frame = spot_check_vision(frame)

        # Draw FPS
        cv2.putText(frame, "FPS: {0:.2f}".format(frame_rate_calc), (8, 25), font, .7, (0, 0, 0), 2, cv2.LINE_AA)
        cv2.putText(frame, "FPS: {0:.2f}".format(frame_rate_calc), (8, 25), font, .7, (255, 255, 255), 1, cv2.LINE_AA)

        # All the results have been drawn on the frame, so it's time to display it.
        cv2.imshow('Object detector', frame)

        # FPS calculation
        t2 = cv2.getTickCount()
        time1 = (t2 - t1) / freq
        frame_rate_calc = 1 / time1

        # Press 'q' to quit
        if cv2.waitKey(1) == ord('q'):
            break

        rawCapture.truncate(0)
    camera.close()
cv2.destroyAllWindows()
