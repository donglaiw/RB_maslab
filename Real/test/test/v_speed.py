import cv
import sys
sys.path.append('../Vision')
import Vision as vv
import cv
import time


"""
#1. test camera frame rate
capture = cv.CaptureFromCAM(1)
cc=0
st=time.time()
while cc<10:
    img = cv.QueryFrame(capture)    
    cc+=1
cv.SaveImage("wo.jpg",img)    
print "Camera",(time.time()-st)/10,"seconds per frame"
"""
#2. test image processing speed
#CP=cali.CvProcess((640,480),[0, 50, 100,10,180, 256,150, 50,100,256,180,256])
#CP.frame=cv.QueryFrame(CP.capture)
#CP.frame=cv.LoadImage("camli.jpg")
aa=vv.Vision(None)
cc=1

st=time.time()
while cc<10:
    #aa.frame=cv.LoadImage("img/"+str(cc)+".jpg")
    #aa.target=cc    
    #aa.frame=cv.LoadImage("img/1.jpg")
    aa.frame = cv.QueryFrame(aa.capture)
    cv.Resize(aa.frame, aa.small)                        
    cv.CvtColor(aa.small, aa.hsv_frame, cv.CV_BGR2HSV)    
    #aa.FindCircle()
    aa.FindWall()
    cc+=1
print "Image Processing", (time.time()-st)/10,"seconds per frame"
"""

#3. test sequential time
cc=0
st=time.time()
while cc<10:
    CP.frame=cv.QueryFrame(CP.capture)
    CP.lock=1
    CP.FindCircle()    
    cc+=1
print "Naive Sequential",(time.time()-st)/10,"seconds per frame"

#4. multithread
CP.lock=0
CP.procount=0
cam_thread = threading.Thread(target=CP.getImg,args=())
cam_thread.start()
st=time.time()
while CP.procount<10:
    CP.FindCircle()    
print "Mutli-thread",(time.time()-st)/10,"seconds per frame"
CP.killed=True
cam_thread.join()
"""
"""
#5. multiprocess
CP.killed=False
p = mp.Process(target=CP.getImg, args=())
st=time.time()
while CP.procount<10:
    CP.FindCircle()    
print "Mutli-Process",(time.time()-st)/10,"seconds per frame"
CP.killed=True
p.join()
"""
