#************************************************************************
# Raspberry Pi Parking Sport Detector Camera using TensorFlow Object Detection API
#
# Project: Spot Check
# Author: Bradley Bruce
# Based on code from: Evan Juras
# Date: 11/29/2019
# Description:
#
# This script implements a "vehicle detector" that sends a signal to an API when
# A vehical is detected within a preset 'Parking Spot'. It takes video frames from
# a Picamera, passes them through a TensorFlow object detection model,
# determines if a car, truck, or motorcycle has been detected in the image,
# checks the location of the vehicle in the frame, updates the correct parking spot
# if a car has been detected there
#
# The framework is based off the Object_detection_picamera.py script located here:
# https://github.com/EdjeElectronics/TensorFlow-Object-Detection-on-the-Raspberry-Pi/blob/master/Object_detection_picamera.py
#
# ***********************************************************************

import os
import cv2
import numpy as np
from picamera.array import PiRGBArray
from picamera import PiCamera
import tensorflow as tf
import argparse
import sys

import ParkingSpot
import ApiConnect
import DeviceUpdate

# ************** Run scripts to Update Raspberry Pi ***************** #
if DeviceUpdate.initialize_raspberry_pi(1):
    print("Raspberry Pi Initialized.")
else:
    sys.exit()


# *********** Initialize TensorFlow model that will be deployed ************ #

# Set up camera constants
IM_WIDTH = 1280
IM_HEIGHT = 720
camera_type = 'picamera'

# This is needed since the working directory is the object_detection folder.
sys.path.append('..')

# Import utilites
from utils import label_map_util
from utils import visualization_utils as vis_util

# Name of the directory containing the object detection module we're using
MODEL_NAME = 'ssdlite_mobilenet_v2_coco_2018_05_09'

# Grab path to current working directory
CWD_PATH = os.getcwd()

# Path to frozen detection graph .pb file, which contains the model that is used for detection
PATH_TO_CKPT = os.path.join(CWD_PATH,MODEL_NAME,'frozen_inference_graph.pb')

# Path to label map file
PATH_TO_LABELS = os.path.join(CWD_PATH,'data','mscoco_label_map.pbtxt')

# Specify the number of objects our model can detect
NUM_CLASSES = 10

# Load the label map.
# Label maps map indices to category names, so that when the convolution
# network predicts `5`, we know that this corresponds to `airplane`.
# Here we use internal utility functions, but anything that returns a
# dictionary mapping integers to appropriate string labels would be fine
label_map = label_map_util.load_labelmap(PATH_TO_LABELS)
categories = label_map_util.convert_label_map_to_categories(label_map, max_num_classes=NUM_CLASSES, use_display_name=True)
category_index = label_map_util.create_category_index(categories)

# Load the Tensorflow model into memory.
detection_graph = tf.Graph()
with detection_graph.as_default():
    od_graph_def = tf.GraphDef()
    with tf.gfile.GFile(PATH_TO_CKPT, 'rb') as fid:
        serialized_graph = fid.read()
        od_graph_def.ParseFromString(serialized_graph)
        tf.import_graph_def(od_graph_def, name='')

    sess = tf.Session(graph=detection_graph)

# *** Define input and output tensors (i.e. data) for the object detection classifier *** #

# Input tensor is the image
image_tensor = detection_graph.get_tensor_by_name('image_tensor:0')

# Output tensors are the detection boxes, scores, and classes
# Each box represents a part of the image where a particular object was detected
detection_boxes = detection_graph.get_tensor_by_name('detection_boxes:0')

# Each score represents level of confidence for each of the objects.
# The score is shown on the result image, together with the class label.
detection_scores = detection_graph.get_tensor_by_name('detection_scores:0')
detection_classes = detection_graph.get_tensor_by_name('detection_classes:0')

# Number of objects detected
num_detections = detection_graph.get_tensor_by_name('num_detections:0')

#### Initialize other parameters ####

# Initialize frame rate calculation
frame_rate_calc = 1
freq = cv2.getTickFrequency()
font = cv2.FONT_HERSHEY_SIMPLEX

#TODO read from database to get box information
# Define inside box coordinates (top left and bottom right)
TL_inside = (40,450)
BR_inside = (303,633)

# Define outside box coordinates (top left and bottom right)
TL_outside = (int(IM_WIDTH*0.46),int(IM_HEIGHT*0.25))
BR_outside = (int(IM_WIDTH*0.8),int(IM_HEIGHT*.85))

# Initialize control variables used for pet detector
detected_inside = False
detected_outside = False

inside_counter = 0
outside_counter = 0

pause = 0
pause_counter = 0

#### Pet detection function ####

# This function contains the code to detect a pet, determine if it's
# inside or outside, and send a text to the user's phone.
def car_detector(frame):

    # Use globals for the control variables so they retain their value after function exits
    global detected_inside, detected_outside
    global inside_counter, outside_counter
    global pause, pause_counter

    frame_expanded = np.expand_dims(frame, axis=0)

    # Perform the actual detection by running the model with the image as input
    (boxes, scores, classes, num) = sess.run(
        [detection_boxes, detection_scores, detection_classes, num_detections],
        feed_dict={image_tensor: frame_expanded})

    # Draw the results of the detection (aka 'visulaize the results')
    vis_util.visualize_boxes_and_labels_on_image_array(
        frame,
        np.squeeze(boxes),
        np.squeeze(classes).astype(np.int32),
        np.squeeze(scores),
        category_index,
        use_normalized_coordinates=True,
        line_thickness=2,
        min_score_thresh=0.25)

    # Draw boxes defining parking spots
    cv2.rectangle(frame,TL_outside,BR_outside,(0,0,255),2)
    cv2.putText(frame,"SpotID: 2",(TL_outside[0]+10,TL_outside[1]-10),font,1,(0,0,255),1,cv2.LINE_AA)
    cv2.rectangle(frame,TL_inside,BR_inside,(0,0,255),2)
    cv2.putText(frame,"SpotID: 1",(TL_inside[0]+10,TL_inside[1]-10),font,1,(0,0,255),1,cv2.LINE_AA)

    # classes array is an array of all detected objects and what they have been classified as
    # loop through every detected object and check if it is a vehicle (car (3), motorcycle (4), or truck (8))
    # the boxes array holds coordinates of detected objects that we can use
    # boxes[0][objectIndex] variable holds coordinates of detected objects as (ymin, xmin, ymax, xmax)
    detectedObjectIndex = 0
    for detectedObject in classes[0]:
        if((detectedObject == 3) or (detectedObject == 4) or (detectedObject == 8)):
            # Place a dot in objects center
            x = int(((boxes[0][detectedObjectIndex][1] + boxes[0][detectedObjectIndex][3]) / 2) * IM_WIDTH)
            y = int(((boxes[0][detectedObjectIndex][0] + boxes[0][detectedObjectIndex][2]) / 2) * IM_HEIGHT)
            cv2.circle(frame, (x, y), 5, (75, 13, 180), -1)

            # Check if vehicle is inside one of our spots
            # print(classes[0][detectedObjectIndex])

        detectedObjectIndex += 1

    if (((int(classes[0][0]) == 3) or (int(classes[0][0] == 4) or (int(classes[0][0]) == 8))) and (pause == 0)):
        x = int(((boxes[0][0][1]+boxes[0][0][3])/2)*IM_WIDTH)
        y = int(((boxes[0][0][0]+boxes[0][0][2])/2)*IM_HEIGHT)

        # If object is in inside box, increment inside counter variable
        if ((x > TL_inside[0]) and (x < BR_inside[0]) and (y > TL_inside[1]) and (y < BR_inside[1])):
            inside_counter = inside_counter + 1

        # If object is in outside box, increment outside counter variable
        if ((x > TL_outside[0]) and (x < BR_outside[0]) and (y > TL_outside[1]) and (y < BR_outside[1])):
            outside_counter = outside_counter + 1

    # If pet has been detected inside for more than 10 frames, set detected_inside flag
    # and send a text to the phone.
    if inside_counter > 10:
        detected_inside = True
        print("Spot 2 Taken")
        inside_counter = 0
        outside_counter = 0
        # Pause pet detection by setting "pause" flag
        pause = 1

    # If pet has been detected outside for more than 10 frames, set detected_outside flag
    # and send a text to the phone.
    if outside_counter > 10:
        detected_outside = True
        print("Spot 1 Taken!")
        inside_counter = 0
        outside_counter = 0
        # Pause pet detection by setting "pause" flag
        pause = 1

    # If pause flag is set, draw message on screen.
    if pause == 1:
        if detected_inside == True:
            cv2.putText(frame,'Spot 1 is taken!',(int(IM_WIDTH*.1),int(IM_HEIGHT*.5)),font,3,(0,0,0),7,cv2.LINE_AA)
            cv2.putText(frame,'Spot 1 is taken!',(int(IM_WIDTH*.1),int(IM_HEIGHT*.5)),font,3,(95,176,23),5,cv2.LINE_AA)

        if detected_outside == True:
            cv2.putText(frame,'Spot 2 is taken!',(int(IM_WIDTH*.1),int(IM_HEIGHT*.5)),font,3,(0,0,0),7,cv2.LINE_AA)
            cv2.putText(frame,'Spot 2 is taken!',(int(IM_WIDTH*.1),int(IM_HEIGHT*.5)),font,3,(95,176,23),5,cv2.LINE_AA)

        # Increment pause counter until it reaches 30 (for a framerate of 1.5 FPS, this is about 20 seconds),
        # then unpause the application (set pause flag to 0).
        pause_counter = pause_counter + 1
        if pause_counter > 15:
            pause = 0
            pause_counter = 0
            detected_inside = False
            detected_outside = False

    # Draw counter info
    cv2.putText(frame,'Detection counter: ' + str(max(inside_counter,outside_counter)),(10,100),font,0.5,(255,255,0),1,cv2.LINE_AA)
    cv2.putText(frame,'Pause counter: ' + str(pause_counter),(10,150),font,0.5,(255,255,0),1,cv2.LINE_AA)

    return frame

#### Initialize camera and perform object detection ####

### Picamera ###
if camera_type == 'picamera':
    # Initialize Picamera and grab reference to the raw capture
    camera = PiCamera()
    camera.resolution = (IM_WIDTH,IM_HEIGHT)
    camera.framerate = 1
    rawCapture = PiRGBArray(camera, size=(IM_WIDTH,IM_HEIGHT))
    rawCapture.truncate(0)

    # Continuously capture frames and perform object detection on them
    for frame1 in camera.capture_continuous(rawCapture, format="bgr",use_video_port=True):

        t1 = cv2.getTickCount()
        
        # Acquire frame and expand frame dimensions to have shape: [1, None, None, 3]
        # i.e. a single-column array, where each item in the column has the pixel RGB value
        #frame = frame1.array
        frame = np.copy(frame1.array)
        frame.setflags(write=1)

        # Pass frame into pet detection function
        frame = car_detector(frame)

        # Draw FPS
        cv2.putText(frame,"FPS: {0:.2f}".format(frame_rate_calc),(30,50),font,1,(255,255,0),2,cv2.LINE_AA)

        # All the results have been drawn on the frame, so it's time to display it.
        cv2.imshow('Object detector', frame)

        # FPS calculation
        t2 = cv2.getTickCount()
        time1 = (t2-t1)/freq
        frame_rate_calc = 1/time1

        # Press 'q' to quit
        if cv2.waitKey(1) == ord('q'):
            break

        rawCapture.truncate(0)

    camera.close()

cv2.destroyAllWindows()