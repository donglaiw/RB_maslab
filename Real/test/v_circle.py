import cv
import string
import numpy as np
import sys
sys.path.append('../')
import Vision as vv

a=vv.Vision(None)
a.frame = cv.LoadImage("../88.jpg")
cv.Resize(a.frame,a.sample)
cv.CvtColor(a.sample, a.hsv_frame, cv.CV_BGR2HSV)
a.hsv_np= np.asarray(a.hsv_frame[:, :], dtype=np.uint8)

a.Init_Binary()
#a.ThresCircle()
#a.ThresWall('b')
a.ThresCircle()
cv.SaveImage("pp.jpg",a.thresholded)                                             
a.FindLine()
a.FindCircle()
a.state='r'
a.display()

a.state='b'
a.display()
cv.SaveImage("qq.jpg",a.sample)                                             

print a.target

