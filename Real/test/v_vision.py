import cv
import sys
sys.path.append("../Logic")
import Logic as ll
sys.path.append("../Vision")
import Vision as vv
import time 


bb=ll.Logic()
aa=vv.Vision(None)
cc=1
"""
while cc<10:
    aa.frame=cv.LoadImage("img/"+str(cc)+".jpg")
    cv.Resize(aa.frame, aa.small)                        
    cv.CvtColor(aa.small, aa.hsv_frame, cv.CV_BGR2HSV)    
    #aa.FindCircle()
    aa.FindWall()
    cv.SaveImage("img_t/"+str(cc)+".jpg")
    cc+=1
"""
