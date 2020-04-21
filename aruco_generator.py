import numpy as np
import cv2
import cv2.aruco as aruco

'''
    drawMarker(...)
        drawMarker(dictionary, id, sidePixels[, img[, borderBits]]) -> img
'''
# must match the detection
aruco_dict = aruco.Dictionary_get(aruco.DICT_6X6_1000)
print(aruco_dict)
id = 2 # aruco ID
image_size = 300
img = aruco.drawMarker(aruco_dict, 2, image_size)
cv2.imwrite("test_marker.jpg", img)

cv2.imshow('aruco ' + str(id), img)
cv2.waitKey(0)
cv2.destroyAllWindows()