import numpy as np
import cv2
import cv2.aruco as aruco
import json
import os
import sys

from time import sleep

aruco_dict = aruco.Dictionary_get(aruco.DICT_6X6_1000)  # must match the generator
parameters = aruco.DetectorParameters_create()

aruco_size = 0.03 # in meters
camera_up = 2.0   # some cameras need time to warm up
camera_name = 'mac_1502_face_time'
max_wait = 3

def load(config_path):
    if os.path.exists(config_path):
        with open(config_path) as json_data:
            j_config = json.load(json_data)
        return j_config
    else:
        print(config_path + ' not found')
        sys.exit(1)


def camera_calibration():
    # camera matrix and dist_coeff needs to be known or use these defaults
    camera_matrix = np.array([[5.3434144579284975e+02, 0., 3.3915527836173959e+02],
                             [0., 5.3468425881789324e+02, 2.3384359492532246e+02],
                             [0., 0., 1.]], np.float)
    dist_coeff = np.array([-2.8832098285875657e-01, 5.4107968489116441e-02,
                           1.7350162244695508e-03, -2.6133389531953340e-04,
                           2.0411046472667685e-01], np.float)
    config_dir = os.path.dirname(__file__)
    camera_config = load(config_dir + '/calibration_matrix.json')
    if camera_name in camera_config:
        camera_matrix = np.array(camera_config[camera_name]['camera_matrix'], np.float)
        dist_coeff = np.array(camera_config[camera_name]['dist_coeff'], np.float)

    return [camera_matrix, dist_coeff]


camera_matrix, dist_coeff = camera_calibration()

cap = cv2.VideoCapture(0)
while not cap.isOpened():
    sleep(camera_up)
    print('waiting for camera')
    max_wait -= 1
    if max_wait <= 0:
        print('failed to start camera !')
        sys.exit(1)

while True:
    ret, frame = cap.read()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    corners, ids, rejectedImgPoints = aruco.detectMarkers(gray, aruco_dict, parameters=parameters)
    gray = aruco.drawDetectedMarkers(gray, corners, ids)

    # if aruco marker detected
    if ids is not None:
        rvec, tvec, objp = aruco.estimatePoseSingleMarkers(corners, aruco_size, camera_matrix, dist_coeff)  # For a single marker
        aruco.drawDetectedMarkers(frame, corners, ids, (0, 255, 0))
        aruco.drawAxis(frame, camera_matrix, dist_coeff, rvec, tvec, 1)
        print(tvec[0][0])
        distance = round(np.linalg.norm(tvec[0][0]), 2) * 100
        info = str(ids) + ':' + str(distance) + " cm"
        cv2.putText(frame, info, (10, 400), cv2.FONT_HERSHEY_PLAIN, 1, (255, 0, 255))

    cv2.imshow('frame', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()
