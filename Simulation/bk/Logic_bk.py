import sys
sys.path.append("../Vision")
sys.path.append("../Control")

import s_Vision_nothread as vv
import s_Control_nothread as cc

import numpy as np
import random
import threading, thread,time

class Logic():
    def __init__(self):
        threading.Thread.__init__(self)        
        self.control = cc.Controller()
        self.vision = vv.Vision()
        self.states = ['r', 'b', 'y']
        self.current_st = 'r'
        self.ballcount = 0
        self.killed=False        
        self.target=0
        
    
    def run(self): 
        # sensor threads were started in _init_ in vision/control before the game start 
        # main thread queues  
        while self.killed==False:
            self.getBall()           
            #self.dumpBall()
            print "success"
            #break        

    def close(self):        
        self.vision.killed=True            
        self.control.killed=True
        self.killed=True
        
    def getBall(self):                
        #while  time.time() - self.st < self.total:# and self.control.new==0:
        if sum([self.control.bp_val[0],self.control.bp_val[3]])!=0:                
            self.getOutStuck()            
        #print "go get it"            
        self.findObj()      
        print "step 1"    
        #track obj            
        self.control.goStraight()            
        #break
        self.setState('y')
        
        """
        if self.control.new==1:
            self.ballcount+=1
            self.control.new=0
            self.current_st = 'y'
        """
                
    def dumpBall(self):        
        #while  time.time() - self.st < self.total and self.current_st == 'y':                                    
        if sum([self.control.bp_val[0],self.control.bp_val[3]])!=0:                
            self.getOutStuck()
        # go to wall
        self.findObj()    
        self.control.goStraight()
        # throw ball
        print "throw"
        self.control.throwBall()    
        self.ballcount=0
        self.setState('r')
        #break
        
    def setState(self,state):
        self.current_st = state
        self.vision.state = state
        
    def findObj(self):        
        self.vision.findObj()
        #print "sooo",self.target
        while self.vision.target==0 and self.killed==False:#time.time() - self.st < self.total:
            #self.control.goTurn(15*(2*random.randint(0, 1)-1))
            self.control.goTurn(15)
            self.vision.findObj()
            print "rotate",self.control.angle,self.target
        if self.vision.target!=0:
            print "Ball Found"
        #self.target=self.vision.target
        
    def trackObj(self):
        
        self.findObj()
        #print "sooo",self.target
        self.control.goStraight()
        while time.time() - self.st < self.total:
            #self.control.goTurn(15*(2*random.randint(0, 1)-1))            
            if self.vision.target==0:
                self.control.adjust(self.target)
                self.vision.findObj()
            else:
                self.target=self.vision.target
            #print "rotate",self.control.angle,self.target
        print "Ball Found"
                
    def getOutStuck(self):
        """
        out = 1
        while out!=0 and time.time() - self.st < self.total:
            self.control.goTurn(15)
            out = sum(self.control.bp_val)
            print "rotate to get out of stuck",self.control.x,self.control.y,self.control.angle,out
        
        """
        print "try to get out"
        self.control.dir=-1
        self.control.goStraight()
        self.control.dir=1
        #time.sleep(2)
        self.control.goTurn(30)
            
            
