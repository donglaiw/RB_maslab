import cv
import string
import numpy as np
class Vision ():
    def __init__(self,step=1):
        self.capture = cv.CaptureFromCAM(1)
        self.hsv=[[0]*12]*3
        self.frame=cv.LoadImage("t4.jpg")
        self.strip_size =cv.GetSize(self.frame)
        self.hsv_frame = cv.CreateImage(self.strip_size, cv.IPL_DEPTH_8U, 3)
        self.thresholded = cv.CreateImage(self.strip_size, cv.IPL_DEPTH_8U, 1)
        self.thresholded2 = cv.CreateImage(self.strip_size, cv.IPL_DEPTH_8U, 1)               
        self.loadHSV()

    def loadHSV(self):
        a=open("0.cal")
        line=a.readline().split(",")
        self.hsv[0]=[string.atof(x) for x in line[:-1]]
        a.close()
        
        a=open("1.cal")
        line=a.readline().split(",")
        self.hsv[1]=[string.atof(x) for x in line[:-1]]
        a.close()
        
        a=open("2.cal")
        line=a.readline().split(",")
        self.hsv[2]=[string.atof(x) for x in line[:-1]]
        a.close()

        self.setThres()
    
    def setThres(self):  
        self.r0min = cv.Scalar(self.hsv[0][0], self.hsv[0][1], self.hsv[0][2],0)
        self.r0max = cv.Scalar(self.hsv[0][3], self.hsv[0][4], self.hsv[0][5],0)
        
        self.r1min = cv.Scalar(self.hsv[0][6], self.hsv[0][7], self.hsv[0][8],0)
        self.r1max = cv.Scalar(self.hsv[0][9], self.hsv[0][10], self.hsv[0][11],0)
        
        self.y0min = cv.Scalar(self.hsv[1][0], self.hsv[1][1], self.hsv[1][2],0)
        self.y0max = cv.Scalar(self.hsv[1][3], self.hsv[1][4], self.hsv[1][5],0)

        self.b0min = cv.Scalar(self.hsv[2][0], self.hsv[2][1], self.hsv[2][2],0)
        self.b0max = cv.Scalar(self.hsv[2][3], self.hsv[2][4], self.hsv[2][5],0)
        
        
    def FindCircle(self):        
        #if self.frame is not None :
        cv.CvtColor(self.frame, self.hsv_frame, cv.CV_BGR2HSV)
        self.lock=0            
        cv.InRangeS(self.hsv_frame, self.r0min, self.r0max, self.thresholded)
        cv.InRangeS(self.hsv_frame, self.r1min, self.r1max, self.thresholded2)
        cv.Or(self.thresholded, self.thresholded2, self.thresholded)                                           
        # pre-smoothing improves Hough detector
        cv.Smooth(self.thresholded, self.thresholded, cv.CV_GAUSSIAN, 9, 9)
        self.circles = cv.CreateMat(self.strip_size[0], 1, cv.CV_32FC3)            
        cv.SaveImage("ho.jpg", self.thresholded)
        cv.HoughCircles(self.thresholded, self.circles, cv.CV_HOUGH_GRADIENT, 2, 20,200,100,0,500)            
        self.target=self.circles.height
        print "hooo",self.circles.height        


if __name__== "__main__":
    a=Vision()
    a.FindCircle()
    