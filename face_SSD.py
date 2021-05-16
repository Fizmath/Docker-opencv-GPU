"""
Face detection  OpenCV DNN  with Gsteamer on GPU/CPU

https://github.com/opencv/opencv/tree/master/samples/dnn

"""
import cv2
import numpy as np
import time

#  before messing with w,h,fps pin the embedded w,h,fps of your cam . Replace 0 with your options if other :
camera = cv2.VideoCapture(0)
fps = camera.get(cv2.CAP_PROP_FPS)
width = int(camera.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(camera.get(cv2.CAP_PROP_FRAME_HEIGHT))
del camera

net = cv2.dnn.readNetFromCaffe("./model_SSD/deploy.prototxt",
                                    "./model_SSD/res10_300x300_ssd_iter_140000_fp16.caffemodel")

# comment the two lines below for the CPU inference
net.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
net.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA)
#

confid = 0.75

# the default cam  device path is 'v4l2src device=/dev/video0 ! ..    replace with yours if other
gst_str = 'v4l2src  ! videoconvert ! videoscale  ! videorate ! ' \
          'video/x-raw,width=900,height=500,framerate=20/1  ! appsink  sync=false drop=TRUE '

camera = cv2.VideoCapture(gst_str, cv2.CAP_GSTREAMER)
fpsGS = camera.get(cv2.CAP_PROP_FPS)

while True:
    ret, frame = camera.read()
    if not ret:
        print("stream gone yaw !")
        break
    start = time.time()
    h, w = frame.shape[:2]
    imageBlob = cv2.dnn.blobFromImage(cv2.resize(frame, (300, 300)), 1.0, (300, 300), (104, 177, 123))
    net.setInput(imageBlob)
    detections = net.forward()
    for i in range(0, detections.shape[2]):
        confidence = detections[0, 0, i, 2]
        if confidence > confid:
            box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
            (startX, startY, endX, endY) = box.astype("int")
            face = frame[startY:endY, startX:endX]
            (fH, fW) = face.shape[:2]
            if fW < 30 or fH < 30:
                continue
            # encircling  ellipse
            a1 = int((np.absolute(startX - endX)) / 2)
            a2 = int((np.absolute(startY - endY)) / 2)
            midx = startX + a1
            midy = startY + a2
            cv2.ellipse(frame, (midx, midy), (a1, int(a1 * 1.5)), 0, 120, 360, (66, 245, 242), 2, lineType=8)
    # the text may got out of the frame in other frame sizes  - tune text_x and text_y for the case
    text_x = int(len(frame[0]) - 400)
    text_y = 30
    st1 = f'Camera {width}*{height},fps:{fps}'
    cv2.putText(frame, st1, (text_x, text_y + 20), cv2.FONT_HERSHEY_SIMPLEX , 0.7, (66, 245, 242), 1)
    #  GS
    (h, w) = frame.shape[:2]
    st2 = f'GStreamer {w}*{h},fps:{fpsGS}'
    cv2.putText(frame, st2, (text_x, text_y + 60),cv2.FONT_HERSHEY_SIMPLEX , 0.7, (66, 245, 242), 1)
    #  detection fps
    end = time.time()
    fps_det = 1 / (end - start)
    st3 = f'Detection fps: {fps_det:.1f}'
    cv2.putText(frame, st3, (text_x, text_y + 100), cv2.FONT_HERSHEY_SIMPLEX , 0.7, (66, 245, 242), 1)
    cv2.imshow('OpenCV DNN face detection ', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

camera.release()
cv2.destroyAllWindows()
