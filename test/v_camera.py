import cv,time

#1. test camera frame rate
cv.NamedWindow("camera", 1)
capture = cv.CaptureFromCAM(0)
cv.SetCaptureProperty(capture, cv.CV_CAP_PROP_FRAME_WIDTH, 200);
cv.SetCaptureProperty(capture, cv.CV_CAP_PROP_FRAME_HEIGHT,200);
    
  
while True:
    img = cv.QueryFrame(capture)
    cv.ShowImage("camera", img)
    k = cv.WaitKey(10);
    if k == 'f':
        break
"""
img = cv.QueryFrame(capture)
print cv.GetSize(img)
#cv.SaveImage("kkdd.jpg",img)
""" 
