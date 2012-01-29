import sys
sys.path.append("../Vision")
sys.path.append("../Control")

_debug=0

if _debug==1:
    import s_Vision as vv
    import s_Control as cc
else:
    import Vision as vv
    import Control as cc



import numpy as np
import random
import threading, thread,time

class Logic(threading.Thread):
    def __init__(self,step=1):
        threading.Thread.__init__(self)        
        self.control = cc.Control(0.1)
        self.vision = vv.Vision(0.1)
        self.states = ['r', 'b', 'y']
        self.current_st = 'r'
        self.ballcount = 0
        self.step=step
        self.target=0
        self.killed=False
        
    def close(self):        
        self.vision.killed=True            
        self.control.killed=True
        self.killed=True
        print "kill command"
        
    def run(self): 
        # sensor threads were started in _init_ in vision/control before the game start 
        # main thread queues  
        #self.vision.start() #handle image processing
        #self.control.start() #handle motor movement
        while self.killed==False:
            if sum([self.control.bp_val[0],self.control.bp_val[3]])!=0:      
                # front direction          
                self.getOutStuck()                        
            self.getBall()           
            #self.dumpBall()
            print "success"
            break
        print "logic done"
        
    def getBall(self):                
        while self.killed==False:# and self.control.new==0:            
            #find ball
            self.findObj()      
            print "step 1"    
            #track ball            
            #get ball: go go go
            self.control.setState('G')
            while  sum([self.control.bp_val[0],self.control.bp_val[3]])==0 and self.killed==False: True

            #move back            
            if  sum([self.control.bp_val[0],self.control.bp_val[3]])!=0:                
                self.getOutStuck()
            self.control.dir=1
            break
        self.setState('y')
        
        """
        if self.control.new==1:
            self.ballcount+=1
            self.control.new=0
            self.current_st = 'y'
        """
                
    def dumpBall(self):        
        while self.killed==False:                        
            # find yellow wall
            self.findObj()
            # go to wall    
            self.control.setState('G')
            while  sum([self.control.bp_val[0],self.control.bp_val[3]])==0 and self.killed==False: True
            #self.control.setState('S')
            # throw ball
            print "throw"
            self.control.setState('T')    
            self.ballcount=0
            #move back
            if  sum([self.control.bp_val[0],self.control.bp_val[3]])!=0:                
                self.getOutStuck()
            self.control.dir=1
            break
        self.setState('r')
            
    def setState(self,state):
        self.current_st = state
        self.vision.state= state
    """                
    def setarget(self):
        self.target=self.vision.target
        self.vision.target=0      
    """
        
    def findObj(self):
        #clear out in case vision.target still contains last result          
        self.vision.target=0
        #time.sleep(0.1)
        if self.vision.target==0:
            self.control.motorstate='T'
        while self.vision.target==0 and self.killed==False:#True
            print "rotate"
        if self.vision.target!=0:
            print "Ball Found"
        
        
        
    def trackObj(self):
        
        self.findObj()
        #print "sooo",self.target
        self.control.goStraight()
        while self.killed==False:
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
        while out!=0 and self.killed==False:
            self.control.goTurn(15)
            out =  sum([self.control.bp_val[0],self.control.bp_val[3]])
            print "rotate to get out of stuck",self.control.x,self.control.y,self.control.angle,out
        
        """
        print "try to get out"
        self.control.dir = -1
        self.control.setState('G')
        while  sum([self.control.bp_val[0],self.control.bp_val[3]])!=0 and self.killed==False: True
        self.control.dir = 1
        self.control.setState('T')
        #time.sleep(2)
        #self.control.goTurn(30)
