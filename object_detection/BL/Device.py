from datetime import datetime

import cv2
import base64
import numpy as np


# Constructors
class Device:

    def __init__(self, device_id, device_name, local_ip, external_ip, mac_address, last_update_date, company_id,
                 take_new_image, device_status_id, parking_lot_id):
        self.DeviceID = device_id
        self.DeviceName = device_name
        self.LocalIP = local_ip
        self.ExternalIP = external_ip
        self.MacAddress = mac_address
        self.LastUpdateDate = last_update_date
        self.CompanyID = company_id
        self.TakeNewImage = take_new_image
        self.DeviceStatusID = device_status_id
        self.ParkingLotID = parking_lot_id

    @staticmethod
    def constructEmpty():
        device = Device(None, None, None, None, None, None, None, None, None, None, )
        return device

    # Methods
    def decoder(obj):
        device = Device(obj['deviceID'], obj['deviceName'], obj['localIpAddress'], obj['externalIpAddress'],
                        obj['macAddress'], obj['lastUpdateDate'], obj['companyID'], obj['takeNewImage'],
                        obj['deviceStatusID'], obj['parkingLotID'])
        return device

    def fill(self):
        from DL.Device_dl import Device_dl
        device_dl = Device_dl(self.DeviceID, self.DeviceName, self.LocalIP, self.ExternalIP, self.MacAddress,
                              self.LastUpdateDate, self.CompanyID, self.TakeNewImage, self.DeviceStatusID,
                              self.ParkingLotID)
        return device_dl.fill()

    @staticmethod
    def getLocalIP():
        try:
            import socket as sc
            host_name = sc.gethostname()
            local_ip = sc.gethostbyname(host_name + ".local")
            return local_ip
        except Exception:
            return "Error"

    @staticmethod
    def getExternalIP():
        try:
            import urllib.request as ur
            external_ip = ur.urlopen('https://ident.me').read().decode('utf8')
            return external_ip
        except Exception:
            return "Error"

    @staticmethod
    def getMacAddress():
        try:
            import uuid
            mac_address = ':'.join(['{:02x}'.format((uuid.getnode() >> ele) & 0xff)
                                    for ele in range(0, 8 * 6, 8)][::-1])
            return mac_address
        except Exception:
            return "Error"

    @staticmethod
    def isConnected():
        try:
            import urllib.request as ur
            ur.urlopen('http://216.58.192.142', timeout=1)
            return True
        except Exception as err:
            return False

    def findDeviceFromList(self, devices=[]):
        try:
            current_mac_address = self.getMacAddress()
            for device in devices:
                if device.MacAddress == current_mac_address:
                    return device
            return None

        except Exception:
            # most likely to catch if list of devices is empty
            return None

    def getAllParkingSpots(self):
        from DL.Device_dl import Device_dl
        device_dl = Device_dl(self.DeviceID, self.DeviceName, self.LocalIP, self.ExternalIP, self.MacAddress,
                              self.LastUpdateDate, self.CompanyID, self.TakeNewImage, self.DeviceStatusID,
                              self.ParkingLotID)
        return device_dl.getAllParkingSpots()

    def updateDevice(self):
        from DL.Device_dl import Device_dl
        device_dl = Device_dl(self.DeviceID, self.DeviceName, self.LocalIP, self.ExternalIP, self.MacAddress,
                              self.LastUpdateDate, self.CompanyID, self.TakeNewImage, self.DeviceStatusID,
                              self.ParkingLotID)
        return device_dl.updateDevice()

    def createDevice(self):
        from DL.Device_dl import Device_dl
        device_dl = Device_dl(self.DeviceID, self.DeviceName, self.LocalIP, self.ExternalIP, self.MacAddress,
                              self.LastUpdateDate, self.CompanyID, self.TakeNewImage, self.DeviceStatusID,
                              self.ParkingLotID)
        return device_dl.createDevice()

    def updateAllSpots(self, parkingLots):
        from DL.Device_dl import Device_dl
        device_dl = Device_dl(self.DeviceID, self.DeviceName, self.LocalIP, self.ExternalIP, self.MacAddress,
                              self.LastUpdateDate, self.CompanyID, self.TakeNewImage, self.DeviceStatusID,
                              self.ParkingLotID)
        return device_dl.updateAllSpots(parkingLots)

    def imageProcessing(self, current_frame, parking_spots, sess, detection_boxes, detection_scores, detection_classes,
                        num_detections, image_tensor, category_index, required_index_list,
                        IM_WIDTH, IM_HEIGHT, SPOT_CHANGE_LENGTH, api_counter, API_TRIGGER_COUNT):

        from utils import visualization_utils as vis_util
        font = cv2.FONT_HERSHEY_SIMPLEX

        frame_expanded = np.expand_dims(current_frame, axis=0)

        # Perform the actual detection by running the model with the image as input
        (boxes, scores, classes, num) = sess.run(
            [detection_boxes, detection_scores, detection_classes, num_detections],
            feed_dict={image_tensor: frame_expanded})

        # Draw the results of the detection
        vis_util.visualize_boxes_and_labels_on_image_array(current_frame, np.squeeze(boxes),
                                                           np.squeeze(classes).astype(np.int32), np.squeeze(scores),
                                                           category_index, use_normalized_coordinates=True,
                                                           line_thickness=0, min_score_thresh=0.45)

        # Draw parking spots labels
        for p in parking_spots:
            top_left = (p.TopLeftXCoordinate, p.TopLeftYCoordinate)
            cv2.putText(current_frame, "SpotID: " + str(p.SpotID), (top_left[0], top_left[1] - 5), font, .7, (0, 0, 0),
                        2, cv2.LINE_AA)
            cv2.putText(current_frame, "SpotID: " + str(p.SpotID), (top_left[0], top_left[1] - 5), font, .7,
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
                        spot.TopLeftYCoordinate < coord[1]) and (spot.BottomRightYCoordinate > coord[1]) \
                        and spot.IsOpen is True:
                    object_detected = True
                    spot_changed = True
                    spot.OccupiedCounter += 1
                    spot.EmptyCounter = 0
                    # print("Spot ID: " + str(spot.ParkingSpotID) + " " + "Occupied Counter: " + str(spot.OccupiedCounter) + " " + "Empty Counter: " + str(spot.EmptyCounter) + " " + "Is Spot Open?: " + str(spot.IsOpen))
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
                    cv2.rectangle(current_frame, (top_left[0] + 2, top_left[1] + 2),
                                  (bottom_right[0] - 2, bottom_right[1] - 2), (0, 255, 255), 2)
            if spot.IsOpen is False and spot_changed is False:
                cv2.rectangle(current_frame, top_left, bottom_right, (0, 0, 255), 2)
            if spot.IsOpen is False and spot_changed is True:
                cv2.rectangle(current_frame, top_left, bottom_right, (0, 0, 255), 2)
                if spot.EmptyCounter % 2 == 0:
                    cv2.rectangle(current_frame, (top_left[0] + 2, top_left[1] + 2),
                                  (bottom_right[0] - 2, bottom_right[1] - 2), (0, 255, 255), 2)

        total_spots = 0
        open_spots = 0

        for spot in parking_spots:
            total_spots += 1
            if spot.IsOpen:
                open_spots += 1

        cv2.putText(current_frame, "Open Spots: " + str(open_spots) + "/" + str(total_spots), (8, 50), font, .7, (0, 0, 0), 2,
                    cv2.LINE_AA)
        cv2.putText(current_frame, "Open Spots: " + str(open_spots) + "/" + str(total_spots), (8, 50), font, .7,
                    (255, 255, 255), 1, cv2.LINE_AA)

        # Send parking spot data to API
        if api_counter % API_TRIGGER_COUNT == 0:
            spotUpdateResult = self.updateAllSpots(parking_spots)
            now = datetime.now().strftime("%m/%d/%Y %H:%M:%S")
            if spotUpdateResult:
                print("Database updated at: " + str(now) + ".")
            else:
                print("Database failed to update at " + str(now) + ".")
            #    sys.exit()

        return current_frame

    def takeImage(self):
        camera = cv2.VideoCapture(0)
        camera.set(3, 1280)
        camera.set(4, 720)
        camera.set(15, -8.0)
        ret, frame = camera.read()
        camera.release()
        if ret:
            t = np.arange(25, dtype=np.float64)
            s = base64.b64encode(frame)
            r = base64.decodebytes(s)
            q = np.frombuffer(r, dtype=np.float64)

            print(np.allclose(q, t))

            # now we need to update the database so that we dont take another image
            self.TakeNewImage = False
            self.updateDevice()
        else:
            return None
