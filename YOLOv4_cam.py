""""
OPENCV YOLO v4 web cam object detection with  GPU/CPU

https://gist.github.com/YashasSamaga/e2b19a6807a13046e399f4bc3cca3a49
https://github.com/easyadin/Object-Detection-YOLOv4

"""
import cv2
import time
import numpy as np

CONFIDENCE_THRESHOLD = 0.2
NMS_THRESHOLD = 0.4

net = cv2.dnn.readNet("./model_YOLOv4/yolov4.weights", "./model_YOLOv4/yolov4.cfg")

# comment to make inference by CPU cores :
net.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
net.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA)
#
#  if your device supports FP16 replace this with the above line:
# net.setPreferableTarget(cv.dnn.DNN_TARGET_OPENCL_FP16)

model = cv2.dnn_DetectionModel(net)
model.setInputParams(size=(416, 416), scale=1 / 255, swapRB=True)

with open("./model_YOLOv4/coco.names", "r") as f:
    class_names = [cname.strip() for cname in f.readlines()]

COLORS = np.random.randint(256, size=(10, 3)).tolist()  # 10 random colors

# pin the inherent cam params  ,  change 0 if not your input device :
camera = cv2.VideoCapture(0)
fps = camera.get(cv2.CAP_PROP_FPS)
width0 = int(camera.get(cv2.CAP_PROP_FRAME_WIDTH))
height0 = int(camera.get(cv2.CAP_PROP_FRAME_HEIGHT))
del camera

# the default cam device path is 'v4l2src device=/dev/video0 ! .. !    replace with yours if other
gst_str = 'v4l2src  ! videoconvert ! videoscale  ! videorate ! ' \
          'video/x-raw,width=1000,height=500,framerate=12/1  ! appsink  sync=false drop=TRUE '

cap = cv2.VideoCapture(gst_str, cv2.CAP_GSTREAMER)
wid = cap.get(3)
hei = cap.get(4)
fpsGS = cap.get(5)

while True:
    ret, frame = cap.read()
    if not ret:
        print(' stream gone yaw !')
        break
    start = time.time()
    classes, scores, boxes = model.detect(frame, CONFIDENCE_THRESHOLD, NMS_THRESHOLD)

    for (classid, score, box) in zip(classes, scores, boxes):
        color = COLORS[int(classid) % len(COLORS)]
        label = "%s : %.2f" % (class_names[classid[0]], score)
        cv2.rectangle(frame, box, color, 2)
        cv2.putText(frame, label, (box[0], box[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
    # the text may got out of the frame in other frame sizes  - tune text_x and text_y for the case
    text_x = int(len(frame[0]) - 400)
    text_y = 30
    st1 = f'Camera {width0}*{height0},fps:{fps}'
    cv2.putText(frame, st1, (text_x, text_y + 20), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (66, 245, 242), 1)
    #
    st2 = f'Gstreamer {wid}*{hei},fps:{fpsGS}'
    cv2.putText(frame, st2, (text_x, text_y + 60), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (66, 245, 242), 1)
    #
    end = time.time()
    fps_det = 1 / (end - start)
    st3 = f'Detection fps: {fps_det:.2f} '
    cv2.putText(frame, st3, (text_x, text_y + 100), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (66, 245, 242), 1)
    #
    cv2.imshow("detections", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
