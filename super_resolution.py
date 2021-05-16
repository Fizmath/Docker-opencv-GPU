"""
OpenCV DNN Super Resolution with GPU/CPU
https://github.com/opencv/opencv_contrib/tree/master/modules/dnn_superres

"""
import cv2
from cv2 import dnn_superres

image = cv2.imread('./golden_axe.png')
path = "./model_SURE/EDSR_x3.pb"

net = dnn_superres.DnnSuperResImpl_create()
net.readModel(path)
# if you run out of GPU memory comment the following two lines to make inference by CPU cores
net.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
net.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA)
#
# input EDSR version
net.setModel("edsr", 3)
result = net.upsample(image)
cv2.imwrite("./SURE_golden_axe.png", result)