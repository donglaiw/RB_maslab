import numpy as np
import time,threading
import math


class Control(threading.Thread):
    def __init__(self,starttime,total):
        threading.Thread.__init__(self)
        self.width_h = 30
        self.height_h = 20
        self.x = 249
        self.y = 200
        self.angle = 300.0
        self.camangle = 30.0
        self.eatangle = 10.0
        self.bp_val = [0, 0, 0, 0]
        self.ir_val = [0, 0, 0, 0]
        self.thrown = False
        self.ballnum = 0 
        self.st_step = 10
        self.an_step = 10
        self.st = starttime
        self.total = total
        self.count=0
        self.new=0
        self.dir=1
        self.motorstate=''
        self.step=1
    
    def getBallCount(self):
        return 1
    
    def run(self):
        while time.time()-self.st<self.total:
            #ordered by freq
            if self.motorstate!='':                         
                if self.motorstate=='G':
                    self.goStraight()                    
                elif self.motorstate=='T':
                    self.goTurn()
                elif self.motorstate=='B':
                    self.throwBall()
                elif self.motorstate=='S':
                    self.stop()  
        print "Control done"     

    def goStraight(self):        
        while time.time()-self.st<self.total:
            an=self.angle/180*math.pi
            self.x -= self.dir*self.st_step * math.sin(an)
            self.y += self.dir*self.st_step * math.cos(an)
            time.sleep(self.step)
            #print "go straight",self.x,self.y,self.angle
        """
        while sum(self.control.bumper())==1:
            #only rotate
            a=1
        """
    def setState(self,state):                   
            self.motorstate=state
        
    def st_angle(self,angle):
        if angle > 360:
            angle -= 360
        elif angle < 0:
            angle += 360
        return angle
             
    def goTurn(self):
        #print "angle : ",self.angle 
        self.angle += self.an_step
        self.angle=self.st_angle(self.angle)
        time.sleep(self.step)
        
    """
    def adjust(self,angle):
        an=(self.angle+angle)/180*math.pi
        self.x -= self.dir*self.step * math.sin(an)
        self.y += self.dir*self.step * math.cos(an)
    """
    def throwBall(self):
        self.thrown = True                            
    
    def stop(self):
        return True
        
