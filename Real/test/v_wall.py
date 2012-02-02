import cv
import string
import numpy as np
import sys
sys.path.append('../')
import Vision as vv

a=vv.Vision(None)
a.frame = cv.LoadImage("../99.jpg")
cv.Resize(a.frame,a.sample)
cv.CvtColor(a.sample, a.hsv_frame, cv.CV_BGR2HSV)
a.hsv_np= np.asarray(a.hsv_frame[:, :], dtype=np.uint8)
a.Copy()                                              

"""
a.Init_Binary()
cv.SetData(a.dis_small,a.small.tostring())
cv.SaveImage("1qqqaa.jpg",a.dis_small)
cv.SaveImage("1yyy.jpg",a.thresholded)
a.ThresWall('y')
cv.SaveImage("1cc.jpg",a.thres_small)
"""

a.FindLine()
a.state='b'
a.display()
a.FindWall()
a.state='y'
a.display()

cv.SaveImage("qq.jpg",a.sample)
print a.target

