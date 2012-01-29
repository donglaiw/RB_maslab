import multiprocessing,thread,time
import cv
import string
import numpy as np
class Vision (multiprocessing.Process):
    def __init__(self,pipe):
        multiprocessing.Process.__init__(self)  
        self.capture = cv.CaptureFromCAM(0)
        self.hsv=[[0]*12]*3
        self.pipe_vision=pipe
        #self.size = (int(cv.GetCaptureProperty(self.capture, cv.CV_CAP_PROP_FRAME_WIDTH)),int(cv.GetCaptureProperty(self.capture, cv.CV_CAP_PROP_FRAME_HEIGHT)))        
        self.size =(640,480)
        self.circles=None
        self.strip_size =(320,240)
        self.strip_size =self.size
        #self.frame=cv.QueryFrame(self.capture)
        #cv.SaveImage("hh.jpg",self.frame)                
        #self.frame=cv.LoadImage("camli.jpg")        
        self.small = cv.CreateImage(self.strip_size, cv.IPL_DEPTH_8U, 3)        
        self.hsv_frame = cv.CreateImage(self.strip_size, cv.IPL_DEPTH_8U, 3)        
        self.thresholded = cv.CreateImage(self.strip_size, cv.IPL_DEPTH_8U, 1)
        self.thresholded2 = cv.CreateImage(self.strip_size, cv.IPL_DEPTH_8U, 1)               
        self.width_thres=0.3*self.strip_size[0]*255
        self.height_thres=0.05*self.strip_size[1]        
        self.loadHSV()
        self.state='r'

        #lock for self.frame I/O        
        #thread.start_new_thread(self.getImg,())
        self.wall=[]
        self.lock=1
        self.target=0
        self.sss=0
        
        """"""
    def run(self):
        while True:
            if self.pipe_vision.poll(0.05):
                #print "roger..."
                #command from logic
                cmd=self.pipe_vision.recv()
                if len(cmd)==1: #set new state
                    #print "current state",cmd
                    self.state=cmd
                else: #ask for obj
                    #print "vision send",self.target
                    self.pipe_vision.send(self.target)
            if self.state == 'r':
                self.FindCircle()
            else:                
                self.FindWall(self.state)
                #print "wall",self.target
                
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
        

    def getImg(self):           
        while self.killed==False:
            #print "wow"
            if self.lock==0:
                #self.frame = cv.QueryFrame(self.capture)
                #print "new"
                self.lock=1            
                #cv.SaveImage(str(time.time())+"calimg.jpg", self.frame)
                #cv.LoadImage("calimg.jpg", self.frame)
                #time.sleep(self.step)                
                #print "get"
                #no need for this many computing power
        print "close camera"
        
    def FindCircle(self):        
        #need to process the latest one
        self.frame = cv.QueryFrame(self.capture)
        #cv.SaveImage("wosd.jpg",self.frame)
        cv.Resize(self.frame, self.small)
        #print "save   "
        if self.lock==1 :             
            #cv.CvtColor(self.frame[range(self.size[0]/2-self.strip_size[0]/2,self.size[0]/2+self.strip_size[0]/2),range(self.strip_size[1])], self.hsv_frame, cv.CV_BGR2HSV)            
            cv.CvtColor(self.small, self.hsv_frame, cv.CV_BGR2HSV)
            #cv.CvtColor(self.frame, self.hsv_frame, cv.CV_BGR2HSV)
            #self.lock=0            
            cv.InRangeS(self.hsv_frame, self.r0min, self.r0max, self.thresholded)
            cv.InRangeS(self.hsv_frame, self.r1min, self.r1max, self.thresholded2)
            cv.Or(self.thresholded, self.thresholded2, self.thresholded)                                           
            # pre-smoothing improves Hough detector
            #cv.Smooth(self.thresholded, self.thresholded, cv.CV_GAUSSIAN, 9, 9)
            self.circles = cv.CreateMat(self.strip_size[0], 1, cv.CV_32FC3)            
            #cv.SaveImage("ha.jpg", self.thresholded)
            cv.HoughCircles(self.thresholded, self.circles, cv.CV_HOUGH_GRADIENT, 2, 120, 100, 40, 20, 200)
            self.target=self.circles.height
            if self.target>=1 and self.sss==0:
                #cv.SaveImage(str(time.time())+"wowo.jpg",self.small)
                print "vision found",time.time()
                self.sss=1
            #print "hooo",self.circles.height        
    
    def FindWall(self,state):        
        #need to process the latest one
        self.frame = cv.QueryFrame(self.capture)
        if self.lock==1 :        
            cv.CvtColor(self.frame, self.hsv_frame, cv.CV_BGR2HSV)
            #self.lock=0
            if state=='y':
                cv.InRangeS(self.hsv_frame, self.y0min, self.y0max, self.thresholded)
            else:
                cv.InRangeS(self.hsv_frame, self.b0min, self.b0max, self.thresholded)
            #cv.SaveImage("hh.jpg",self.thresholded)
            #cv.Resize(self.hsv_frame, self.small)
            #cv.SaveImage("gg.jpg",self.hsv_frame)
                        
            # simple horizontal prejoction
            #cv.Reduce(self.thresholded,self.rowsum, 1, cv.CV_REDUCE_SUM);
            self.rowsum=np.sum(np.asarray(self.thresholded[:,:],dtype=np.int16),axis=1)
            #camera rotated 90
            #self.rowsum=np.sum(np.asarray(self.thresholded[:,:],dtype=np.int16),axis=0)
            start=[-1,-1]
            end=[-1,-1]
            maxlen=[0,0]
            kill=0
            for i in range(self.strip_size[1]):
                if self.rowsum[i]>self.width_thres:                    
                    if start[0]==-1:
                        start[0]=i 
                        kill=0
                    elif kill==0:
                        end[0]=i
                        maxlen[0]+=1
                else:
                    kill=1
                    if maxlen[0]!=0:
                        #end of the line
                        if maxlen[0]>maxlen[1]:
                            maxlen[1]=maxlen[0]
                            start[1]=start[0]
                            end[1]=end[0]
                        else:
                            maxlen[0]=0
                            start[0]=-1
                            end[0]=-1
            #print maxlen,start,end
            if maxlen[1]>=self.height_thres:
                self.wall=(start[1],end[1])
                self.target=1
                #self.display()
                #cv.SaveImage("ha.jpg",self.frame)
            else:
                self.wall= []
                self.target=0
       
                    
    def display(self):
        self.numobj=0
        if self.state=='r' and self.circles!=None:
            self.numobj=self.circles.height
            if self.circles.height != 0:    
                for i in xrange(self.circles.height):
                    circle = self.circles[i, 0]
                    radius = int(circle[2])
                    center = (int(circle[0]), int(circle[1]))
                    #print self.circles.height,center
                    cv.Circle(self.frame, center, radius, (0, 0, 255), 3, 8,0)
        elif self.state=='y' or self.state=='b':
            if self.wall!=[]:
                self.numobj=1
                #cv.Rectangle(self.frame,(self.wall[0],0),(self.wall[1],self.strip_size[0]),(0, 0, 255),5)#rotate
                cv.Rectangle(self.frame,(0,self.wall[0]),(self.strip_size[0],self.wall[1]),(0, 0, 255),5)#rotate
