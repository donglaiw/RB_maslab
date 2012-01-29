import numpy as np
import time,threading
import math


class Controller():
    def __init__(self):
        self.width_h = 30
        self.height_h = 20
        self.x = 478.10691469272416
        self.y = 282.08483439816064
        self.angle = 290.0
        self.camangle = 30.0
        self.eatangle = 10.0
        self.bp_val = [0, 0, 0, 0]
        self.ir_val = [0, 0, 0, 0]
        self.thrown = False
        self.ballnum = 0 
        self.step = 20
        self.killed=False
        self.count=0
        self.new=0
        self.dir=1
    
    def getBallCount(self):
        return 1
    
    def goStraight(self):        
        #while time.time()-self.st<self.total:
        an=self.angle/180*math.pi
        self.x -= self.dir*self.step * math.sin(an)
        self.y += self.dir*self.step * math.cos(an)
        #time.sleep(1)
        """
        if self.dir==-1:
            print "go back",self.x,self.y
            self.x -= self.dir*self.step * math.sin(an)
            self.y += self.dir*self.step * math.cos(an)                
            print "now",self.x,self.y                                 
            #break
        """
        #print "go straight",self.x,self.y,self.angle

        """
        while sum(self.control.bumper())==1:
            #only rotate
            a=1
        """
    def st_angle(self,angle):
        if angle > 360:
            angle -= 360
        elif angle < 0:
            angle += 360
        return angle
             
    def goTurn(self, angle):
        #print "angle : ",self.angle 
        self.angle += angle
        self.angle=self.st_angle(self.angle)
        time.sleep(1)
    """
    def adjust(self,angle):
        an=(self.angle+angle)/180*math.pi
        self.x -= self.dir*self.step * math.sin(an)
        self.y += self.dir*self.step * math.cos(an)
    """
    def throwBall(self):
        self.thrown = True                            
