import numpy as np
import time
import math
import sys
sys.path.append('../')
import Util


class Controller():
    def __init__(self,simulator):
        self.sim=simulator
        self.width_h = 10
        self.height_h = 12
        self.x = 340
        self.y = 150
        self.angle = 270.0
        self.camangle = 30.0
        self.eatangle = 20.0
        #self.sensorlen = 2*self.height_h
        self.sensorrange = [40, 160]
        self.bp_val = [1, 1, 1, 1]# 1 means off
        self.ir_val = [0, 0, 0, 0]
        self.thrown = False         
        
        
        self.straightstep = 20        
        self.anglestep = 30
                
        self.count=0
        self.new=0
        self.lastdir=1
        self.nomove=0
        self.msg=['','']
        
        
       
    def run(self):
        if self.msg[0]=='G':
            self.GoStraight(self.msg[1])
        elif self.msg[0]=='T':
            self.GoTurn(self.msg[1])                                    
            
    def GetIR(self):
        pass
            
    def GoStraight(self,direction):
        #check if next step collides into obstacles
        an=self.angle/180*math.pi
        tmpx=self.x - direction*self.straightstep * math.sin(an)
        tmpy=self.y + direction*self.straightstep * math.cos(an)
        bdpt=self.sim.findcarCorner([tmpx,tmpy,self.angle])        
        if self.sim.CheckCollision(bdpt)==0:
            print "go",tmpx,tmpy,bdpt           
            self.x = tmpx
            self.y = tmpy
            self.lastdir=direction
        
   
    def GoTurn(self, angle_ratio):
        new_an=self.angle + angle_ratio*self.anglestep
        bdpt=self.sim.findcarCorner([self.x,self.y,new_an])
        if self.sim.CheckCollision(bdpt)==0:               
            self.angle=Util.adjust_angle(new_an)
            print "turn"
                
    """
    def adjust(self,angle):
        an=(self.angle+angle)/180*math.pi
        self.x -= self.dir*self.step * math.sin(an)
        self.y += self.dir*self.step * math.cos(an)
    """
    def ThrowBall(self):
        self.thrown = True
    
    def Stop(self):
        pass

