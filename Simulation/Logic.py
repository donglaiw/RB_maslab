import Vision as vv
import Control as cc
import numpy as np
import random

class Logic():
    def __init__(self):                
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
        if self.state=='r':
            self.getBall()           
        else:
            self.dumpBall()
               
    def getBall(self):                
        #while  time.time() - self.st < self.total:# and self.control.new==0:
        if self.target==0:
            self.findObj()      
            print "step 1"    
        #track obj              
        #capture obj
        elif self.target==1:
            self.control.goStraight()            
        elif sum([self.control.bp_val[0],self.control.bp_val[3]])!=0:                
            self.getOutStuck()
            self.setState('y')
               
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
        self.control.goTurn(15)
        self.vision.findObj()
        self.target=self.vision.target
        if self.target==1:
            print "Ball Found"
            self.target=2
        
    def trackObj(self):        
        self.findObj()
        #print "sooo",self.target
        self.control.goStraight()
        #while time.time() - self.st < self.total:
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
