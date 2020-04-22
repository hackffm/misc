import numpy as np
import cv2
import cv2.aruco as aruco

from time import sleep

cap = cv2.VideoCapture(0)
aruco_dict = aruco.Dictionary_get(aruco.DICT_6X6_1000)  # must match the generator
parameters = aruco.DetectorParameters_create()

aruco_size = 0.03 # in meters
camera_up = 2.0   # some cameras need time to warm up

while True:
    if not cap.isOpened():
        sleep(camera_up)
        print('waiting for camera')
    else:
        ret, frame = cap.read()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        corners, ids, rejectedImgPoints = aruco.detectMarkers(gray, aruco_dict, parameters=parameters)
        gray = aruco.drawDetectedMarkers(gray, corners, ids)

        # camera matrix and distCoeffs needs to be known
        cameraMatrix = np.array([[5.3434144579284975e+02, 0., 3.3915527836173959e+02],
                        [0., 5.3468425881789324e+02, 2.3384359492532246e+02],
                        [0., 0., 1.]], np.float)
        distCoeffs = np.array([-2.8832098285875657e-01, 5.4107968489116441e-02,
                         1.7350162244695508e-03, -2.6133389531953340e-04,
                         2.0411046472667685e-01], np.float)

        # if aruco marker detected
        if ids is not None:
            rvec, tvec, objp = aruco.estimatePoseSingleMarkers(corners, aruco_size, cameraMatrix, distCoeffs)  # For a single marker
            aruco.drawDetectedMarkers(frame, corners, ids, (0, 255, 0))
            aruco.drawAxis(frame, cameraMatrix, distCoeffs, rvec, tvec, 10)
            print(tvec[0][0])
            distance = round(np.linalg.norm(tvec[0][0]), 2)
            info = str(ids) + ':' + str(distance) + " cm"
            cv2.putText(frame, info, (10, 400), cv2.FONT_HERSHEY_PLAIN, 1, (255, 0, 255))

        cv2.imshow('frame', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()
