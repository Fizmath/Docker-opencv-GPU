
import cv2

with open('cv2_Build_Info', 'a') as f:
    f.write(cv2.getBuildInformation())