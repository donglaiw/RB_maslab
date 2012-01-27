import cv,time

#1. test camera frame rate
cv.NamedWindow("camera", 1)
capture = cv.CaptureFromCAM(2)
    
cc=0
while cc<100:
    img = cv.QueryFrame(capture)
    """
    cv.ShowImage("camera",img)
    kk=cv.WaitKey(10)
    if kk=='g': 
        break
        
    """
    cv.SaveImage('img/'+str(cc)+".jpg",img)
    time.sleep(0.5)
    cc+=1
    
"""
img = cv.QueryFrame(capture)
cv.SaveImage("kkdd.jpg",img)
"""   
