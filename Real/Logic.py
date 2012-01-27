import sys
import Vision as vv
import Control as cc
import numpy as np
import random
import multiprocessing,time

class Logic(multiprocessing.Process):
    def __init__(self):
        multiprocessing.Process.__init__(self)  
        self.pipe_lv, self.pipe_vision = multiprocessing.Pipe()
        self.pipe_lc, self.pipe_control = multiprocessing.Pipe()
        self.control = cc.Control(self.pipe_control)
        self.vision = vv.Vision(self.pipe_vision)
        self.control.start() #handle motor movement
        self.vision.start() #handle image processing

        self.states = ['r', 'b', 'y']
        self.current_st = 0
        self.ballcount = 0
        self.target=0
        self.bp_val=[1,1,1,1]
        self.ir_val=[0,0,0,0]
        self.timeout_straight=5
        self.timeout_turn=5  #for 16 discrete turns
        self.timeout_back=1.5
        self.timeout_new=2
       

    def Connect(self):
        self.control.ard.connect()
        while not self.control.ard.portOpened: True
        self.control.ard.start()

    def SwitchOn(self):        
        tmp=1       
        while tmp==1 or tmp==-1000:
            self.SendState('c',('SSS',1)) 
            while not self.pipe_lc.poll(0.1): True
            tmp=self.pipe_lc.recv()
            #print tmp
    
    def SendState(self,option,msg):
        # wrapper to avoid flushing the pipe: only send msg when the pipe is empty
        # need time out control
        sent=True
        if option=='v':                        
            if not self.pipe_vision.poll(0.05):
                self.pipe_lv.send(msg)
            else:
                sent=False
            #print "shoot vision",sent    
        else:
            #print "shoot vision",sent    
            #if not self.pipe_control.poll(0.05) and self.pipe_lc.poll(0.01):
            if not self.pipe_control.poll(0.05):
                self.pipe_lc.send(msg)
                #tmp=self.pipe_lc.recv()                
            else:
                sent=False            
            #print sent,self.pipe_lc.poll(0.05),msg,time.time()
        return sent


    def Close(self):        
        self.control.ard.terminate()
        self.control.terminate()
        self.vision.terminate()
        self.terminate()
        #Close Ardiuno connection
        self.control.ard.close()

    def run(self):             
        # main thread 
        while True:
            self.GetBall()
            #print "get ball",time.time()           
            #self.DumpBall()
            #print "dump ball",time.time()        
            
    def GetBall(self):
        #0 set vision state        
        while not self.SendState('v','r'):True                
        #1. find ball
        print "start ball"        
        state=self.FindObj()
        while state<=0:            
            # state==0:nothing here ; state==-1: get stuck
            if state==0:
                #print "time out"
                self.GetNewPlace(self.timeout_new)
            else:
                #print "stuck..."
                self.GetOutStuck(self.timeout_back)
            #print "haha",state,time.time()    
            state=self.FindObj()                  
        #print "step 1",time.time()
        #2.align ball/ track ball is not practical in small distance... 
        #self.AlignBall()   
        #3.get ball: go go go                 
        while not self.SendState('c',('G',127)):True                
        #3.1 go a default time
        #time.sleep(3)
        #while not self.SendState('c',('S',1)):True        
        #3.2 go until wall collision by bumper/vision
        state=self.DetectStuck(self.timeout_straight)
        if state==0:
            self.GetNewPlace(self.timeout_new)
        else:
            self.GetOutStuck(self.timeout_back)
        """
        if state==-1:
            self.GetOutStuck(self.timeout_back)
        """
        #while  sum([self.bp_val[0],self.bp_val[3]])==2:True
        #print self.bp_val
        #self.DetectStuck()    

    def DumpBall(self):
        #0 set vision state        
        while not self.SendState('v','y'):True
        #1. find yellow wall
        #print "do it ",time.time()
        state=self.FindObj()
        #print "so...  ",state
        if state>0:            
            #2. go to wall
            print "go to wall"
            while not self.SendState('c',('G',127)):True
            #Strategy 1: Aim right+ not seen+ go 1.5s
            #time.sleep(3)                    
            #Strategy 2: Go+until stuck            
            state=self.DetectStuck(5)
            #3. align wall
            print "align wall"
            self.AlignWall()
            #4. throw ball
            #print "throw"
            while not self.SendState('c',('B',0)):True
            print "throw"
            time.sleep(5)    
            #self.ballcount=0       
            #5. move back
            self.GetOutStuck(self.timeout_back)
       
    def FindObj(self):         
        while not self.SendState('v','found?'):True
        while not self.pipe_lv.poll(0.05): True
        state=self.pipe_lv.recv()
        #print "vision answer"
        if state<=0:
            # get started
            self.SendState('c',("T",100))            
            # 1. Big Move            
            st=time.time()
            while state==0 and time.time()-st<=self.timeout_turn:
                self.SendState('c',("T",100))
                #print "ask vision......",time.time()
                while not self.SendState('v','found?'):True                                    
                while not self.pipe_lv.poll(0.05):True
                state=self.pipe_lv.recv()
                #state=0
                
                #print "answer vision......",state,time.time()
                #print "now .. try ",state,time.time()
            #1.1: kill the last Turn
            #print "sup....",state
            self.pipe_lc.send(('',0))
            #1.2: just compensate back
            #while not self.SendState('c',("T",-100)):True
        return state
    
    def AlignWall(self):
        #1 use bumper to see which
        #2 try both direction
        while not self.SendState('c',('t',127)):True
        time.sleep(0.3)    
        while not self.SendState('c',('t',-127)):True
        time.sleep(0.3)    
        self.SendState('c',('S',0))
        
    def AlignBall(self):
        #suppose FindObj() find the red ball in the view
        while not self.SendState('v','found?'):True                                    
        while not self.pipe_lv.poll(0.05):True
        state=self.pipe_lv.recv()
        state+=int(state==0)*120
        #x:0-159
        if state>50 and state<110:
            return 
        elif state<50:
            while not self.SendState('c',("T",-60)):True
        elif state>110: 
            while not self.SendState('c',("T",60)):True
        #better to do recursion
        """    
        self.SendState('v','found?')                                    
        while not self.pipe_lv.poll(0.05):True
        state=self.pipe_lv.recv()
        """        

    def GetBumper(self):
        while not self.SendState('c',("BB",0)):True
        while not self.pipe_lc.poll(0.1): True
        self.bp_val=self.pipe_lc.recv()
        print self.bp_val,time.time()

    def GetIr(self):
        while not self.SendState('c',("II",0)):True
        while not self.pipe_lc.poll(0.1): True
        self.ir_val=self.pipe_lc.recv()
        print self.ir_val,time.time()

    def DetectStuck(self,timeout):
        # stuck detection during straight move
        print "detect stuck"
        state=0        
        st=time.time()
        #1. use bumper
        #while  sum([self.bp_val[0],self.bp_val[3]])==0 : True
        #2. use vision
        while state>=0 and time.time()-st<timeout:    
            self.SendState('v','found?')                                    
            while not self.pipe_lv.poll(0.05):True
            state=self.pipe_lv.recv()
            #print "detecting ....",state 
        return state
                
    def GetOutStuck(self,duration):
        print "try to get out"
        while not self.SendState('c',('G',100)):True
        #self.SendState('v','rr')
        time.sleep(duration)                        
        #self.DetectStuck()        
        while not self.SendState('c',('T',random.randint(100,127))):True
        #while not self.SendState('c',('T',random.randint(100,127))):True 
        #go one direction to the end
        #while not self.SendState('c',('T',random.randint(100,127))):True

    def GetNewPlace(self,duration):
        print "try to find new place"
        aa=2*random.randint(0,1)-1
        self.GetOutStuck(duration/3)
        while not self.SendState('c',('t',aa*random.randint(90,110))):True
        while not self.SendState('c',('G',120)):True   
        #time.sleep(1)                       
        self.DetectStuck(duration)        
        

if __name__ == "__main__":

    player=Logic()
    #Open Ardiuno connection
    player.Connect()

    #Waiting for switch
    player.SwitchOn()

    #GO!GO!!GO!!!
    player.start()     
    st=time.time()
    while time.time()-st<180:True
    print "exiting..."

    #Close Process and Ardiuno connection
    player.Close()     

