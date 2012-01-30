import numpy as np
import time
import math
import sys
sys.path.append('../')
import Util


class Vision():
    def __init__(self,simulator):
        self.sim=simulator
        self.x = 0
        self.y = 0
        self.frame = None
        self.preframe = self.frame          
        self.killed=False
        self.circles=[]
        self.wall=[]        
        self.target=0
                        
    def run(self,state):
        #print "vision"
        self.GetImg()        
        self.CheckStuck()

        if self.target!=-1:
            if state == 'r':
                self.FindCircle()                                            
            else:
                self.FindWall()                
            
        self.preframe = self.frame
    
    def GetImg(self):
        self.frame = [self.sim.cenpt[0], self.sim.cenpt[1], [self.sim.cur[0], self.sim.cur[1]], self.sim.circles]
                
    def CheckStuck(self):
        if self.preframe!= None and self.frame[2][0]==self.preframe[2][0] and self.frame[2][1]==self.preframe[2][1]:
            self.target=-1         
    def FindCircle(self):
        #found = []          
        self.circles = []
        for i in range(len(self.frame[3])):
            self.target=Util.ptwithin(self.frame[:3] + [self.frame[3][i][:2]])
            #just get the first nonzero one if there is any
            if self.target!=0:
                break        
        
    def FindWall(self):                 
        if self.frame[0][1] == 500 and self.frame[1][1] == 500:
            self.wall=[1]
        else:
            self.wall=[]
        self.target=len(self.wall)


