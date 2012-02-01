import cv
import string
import numpy as np
import sys
sys.path.append('../')
import Vision as vv

a=vv.Vision(None)
a.frame = cv.LoadImage("../44.jpg")
cv.Resize(a.frame,a.sample)
cv.CvtColor(a.sample, a.hsv_frame, cv.CV_BGR2HSV)
a.hsv_np= np.asarray(a.hsv_frame[:, :], dtype=np.uint8)
a.Copy()                                              
a.FindWall()

print a.target

