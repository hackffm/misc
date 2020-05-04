import cv2
import json
import numpy as np
import sys
from time import sleep

camera_up = 2.0
max_wait = 3

cap = cv2.VideoCapture(0)
while not cap.isOpened():
    sleep(camera_up)
    print('waiting for camera')
    max_wait -= 1
    if max_wait <= 0:
        print('failed to start camera !')
        sys.exit(1)

images = []

for count in range(10):
    ret, img = cap.read()
    while True:
        ret, img = cap.read()
        cv2.imshow('push s to store chessboard ' + str(count), img)
        k = cv2.waitKey(1)
        if k == 27 or k == ord('q'):  # wait for ESC key to exit
            cap.release()
            cv2.destroyAllWindows()
            sys.exit(1)
        if k == ord('s'):  # wait for 's' key to save and exit
            #cv2.imwrite('shot_' + str(count) + '.png', img)
            images.append(img)
            cv2.destroyAllWindows()
            break

cap.release()
cv2.destroyAllWindows()
print('analyse images')

# Defining the dimensions of checkerboard
CHECKERBOARD = (8, 8)
CHECKERBOARD_x = CHECKERBOARD[0] -1
CHECKERBOARD_y = CHECKERBOARD[1] -1
# termination criteria
criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
objp = np.zeros((CHECKERBOARD_x*CHECKERBOARD_y,3), np.float32)
objp[:,:2] = np.mgrid[0:CHECKERBOARD_x,0:CHECKERBOARD_y].T.reshape(-1,2)
# Arrays to store object points and image points from all the images.
objpoints = []  # 3d point in real world space
imgpoints = []  # 2d points in image plane.

found = 0

for img in images:
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    ret, corners = cv2.findChessboardCorners(gray, (CHECKERBOARD_x,CHECKERBOARD_y), None)
    if ret:
        objpoints.append(objp)  # Certainly, every loop objp is the same, in 3D.

        corners2 = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
        imgpoints.append(corners2)
        found += 1
        cv2.drawChessboardCorners(img, CHECKERBOARD, corners2, ret)
        cv2.imshow('Found Chessboard points and vectors', img)
        cv2.waitKey(500)

cv2.destroyAllWindows()
print("Number of images used for calibration: ", found)

"""
Performing camera calibration by passing the value of known 3D points (objpoints)
and corresponding pixel coordinates of the detected corners (imgpoints)
"""
ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)

# store result
camera_name = 'mac_1502_face_time'
# transform the matrix and distortion coefficients to writable lists
data = {camera_name : {'camera_matrix': np.asarray(mtx).tolist(),
        'dist_coeff': np.asarray(dist).tolist()}}

# and save it to a file
file_result = 'calibration_matrix.json'
print('save ' + file_result)
with open(file_result, "w") as f:
    json.dump(data, f, indent=4, sort_keys=True)
