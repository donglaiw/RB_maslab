import cv,time

#1. test camera frame rate
cv.NamedWindow("camera", 1)
capture = cv.CaptureFromCAM(2)
    

while True:
    img = cv.QueryFrame(capture)

    cv.ShowImage("camera",img)
    kk=cv.WaitKey(10)
    if kk=='g': 
        break
"""
img = cv.QueryFrame(capture)
cv.SaveImage("kkdd.jpg",img)
"""   
