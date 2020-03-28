import requests
import json
import os
import sys
import tensorflow as tf

class IoC(object):
    def __int__(self):
        self._DeviceID = None

    # DeviceID
    @property
    def DeviceID(self):
        return self._DeviceID

    @DeviceID.setter
    def DeviceID(self, value):
        self._DeviceID = value

    # Api Address
    @staticmethod
    def ApiAddress():
        return "http://173.91.255.135:8080/SpotCheckServer-2.1.8.RELEASE/"

    # Methods
    @staticmethod
    def sendRequest(address, bodyData, headerType, type):
        try:
            if headerType == 'json':
                headerData = {'Content-type': 'application/json'}
            elif headerType == 'txt':
                headerData = {'Content-type': 'text/plain'}
            if type == 'GET':
                url = IoC.ApiAddress() + address
                response = requests.get(url=url,headers=headerData)
                return response
            elif type == 'POST':
                url = IoC.ApiAddress() + address
                body = bodyData
                response = requests.post(url=url, headers=headerData, data=json.dumps(body))
                return response
        except Exception as err:
            return None

    @staticmethod
    def getAllDevices():
        try:
            from BL.Device import Device
            devices = []
            response = IoC.sendRequest('device/getDevices', None, 'json', 'GET')

            status_code = response.status_code
            if status_code == 200:
                device_json = json.loads(response.text)
                for d in device_json:
                    device = Device.decoder(d)
                    devices.append(device)
                return devices
            else:
                return None
        except Exception as err:
            return None

    @staticmethod
    def returnTensorFlowVariables():
        tensorflowList = []

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

        # ************** Define input and output for the object detection classifier **************** #
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

        tensorflowList.append(sess)
        tensorflowList.append(detection_boxes)
        tensorflowList.append(detection_scores)
        tensorflowList.append(detection_classes)
        tensorflowList.append(num_detections)
        tensorflowList.append(image_tensor)
        tensorflowList.append(category_index)
        tensorflowList.append(required_index_list)

        return tensorflowList
