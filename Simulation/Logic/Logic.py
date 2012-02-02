import sys
sys.path.append("Control/")
sys.path.append("Vision/")
import Util
import Vision as vv
import Control as cc

import numpy as np
import random,math
class Node():
    def __init__(self,root,id,num_children):
        self.visited=False
        self.ch=[None]*num_children
        self.parent=root
        self.id=id
        for i in range(num_children):
            self.ch[i]=Node(self,i,num_children)
        
    
class Logic():
    def __init__(self,simulator):
        self.control = cc.Controller(simulator)
        self.vision = vv.Vision(simulator)
        self.states = ['r', 'b', 'y']
        self.current_st = 'r'
        self.ballcount = 0
        self.killed=False        
        self.target=0
        self.stuck=0 #stay out of collision by using Simulator to check if next move valid
        self.irfront=0                      
        #steps to keep functions in sequence
        
        
        self.st0_timeout=12 # make a 360 degree turn        
        self.st0_timecount=0 # time count of strategy 0
        self.gos_step=0 # steps to get out of stuck
        self.fb_step=0 # steps to eat ball 
        self.np_step=0 # steps to find new place


    #Left rules: Turn left
    def Strategy0(self):        
        #Strategy 0: blindly to find balls
        self.vision.run('r')                 
        """
        #self.vision.target: 
        -1,visually stuck; 
        0,find nothing;
        1,found on the left;
        2,found on the right
        3,found in the center
        """        
        if self.vision.target==-1:
            self.fb_step=0
            self.GetOutStuck()
        elif self.fb_step==1:
            #in the mode of going straight to get the ball
            self.control.msg=['G',1]
        elif self.vision.target==0:
            if self.st0_timecount<self.st0_timeout:
                self.control.msg=['T',1]
                self.st0_timecount+=1
            else:
                #time out and need to go somewhere else
                self.FindNewPlace()
        else:
            self.EatBall()                            
                    
        #a little loose in terms of left/right/front/back stuck                    
        self.control.run()

    def GetOutStuck(self):
        if self.gos_step<=1:
            #two steps of going back
            self.control.msg=['G',-self.control.lastdir]
            self.gos_step += 1
            print "back..."     
        else:                
            #self.control.msg=['T',random.randint(-90,90)]
            self.control.msg=['T',1]
            self.gos_step = 0            
               
    
    def FindNewPlace(self):        
        if self.np_step==0:
            self.control.msg=['T',random.randint(-10,10)]
            self.np_step=1
        else:    
            self.st0_timecount=0
            self.np_step=0
            self.control.msg=['G',1]
        
    def EatBall(self):    
        self.st0_timecount=0;                    
        if self.fb_step==0:
            #align ball
            if self.vision.target==1:
                self.control.msg=['T',1/3]
            elif self.vision.target==2:
                self.control.msg=['T',-1/3]
            else:
                self.fb_step=1
        else:
            self.control.msg=['G',1]