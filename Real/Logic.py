import sys
import Vision as vv
import Control as cc
import numpy as np
import random
import multiprocessing,time

class Logic(multiprocessing.Process):
    def __init__(self,total):
        multiprocessing.Process.__init__(self)  
        self.pipe_lv, self.pipe_vision = multiprocessing.Pipe()
        self.pipe_lc, self.pipe_control = multiprocessing.Pipe()
        self.control = cc.Control(self.pipe_control)
        self.vision = vv.Vision(self.pipe_vision)
        self.vision.start() #handle image processing

        self.switchon=1
        self.target=0
        self.total=total
        self.timeout_straight=5
        self.timeout_turn=7  #for 16 discrete turns
        self.timeout_nav=20
        self.timeout_track=10
        self.s1=self.timeout_turn+self.timeout_nav
        self.timeout_s1=280
        self.st=0; 
        self.dump=0;


############################################1 Process communicaiton ######################################
    def Connect(self):
        self.control.connect()
        while not self.control.portOpened: 
            time.sleep(1)
            self.control.connect()
        self.control.start()

    
    def Close(self):       
        while not self.SendState('c',('O',0)):True
        self.control.close()
        self.control.terminate()
        self.vision.terminate()
        self.terminate()
    
    def SendState(self,option,msg):
        # wrapper to avoid flushing the pipe: only send msg when the pipe is empty
        # need time out control
        sent=True
        if option=='v':                        
            """
            vision msg:
            '?: ask for current status
            target=
            -1: stuck
            (1,2,3): red ball in the (left,center,right)
            (4,5,6): yellow wall in the (left,center,right)
            """
            if not self.pipe_vision.poll(0.05):
                self.pipe_lv.send(msg)
            else:
                sent=False
            #print sent,msg
        else:
            #hard code the function without args
            """
            control msg:
            'N':Navigation 
            'T':Turn a small angle left
            't':Turn a small angle right
            'U':Tune a smaller angle left
            'u':Tune a smaller angle right
            'G':Go straight
            'A':Align Wall for throw ball
            'B':Throw Ball
            'W':Get Switch
            'K':Get Out of Stuck
            'O':stop ball rolleri
            'S':stop it
            'M':turn 180
            """
            if not self.pipe_control.poll(0.05):
                self.pipe_lc.send(msg)
            else:
                sent=False            
            #print sent,self.pipe_lc.poll(0.05),msg,time.time()
        return sent

    #persistent: must sent out and must wait until the response received
    def SendState2(self,option,msg):
        tmp=''
        if option=='c':             
            while not self.SendState('c',msg):True            
        elif option=='v':
            while not self.SendState('v',msg):True            
            while not self.pipe_lv.poll(0.05): True
            tmp=self.pipe_lv.recv()
        return tmp
   
    def SwitchOn(self):        
        tmp='1'       
        while tmp!='0':
            self.SendState('c',('W',2)) 
            while not self.pipe_lc.poll(0.1): True
            tmp=self.pipe_lc.recv()
            print "sss.",tmp,len(tmp)
    
############################################2 Ball & Wall ######################################
    #main strategy:
    def run(self): 
        # initialize rubberband and clear initial visual stuck detection

        self.st=time.time()
        self.SendState2('c',('o',0))
        
        # stage 1: eat as many red balls as possible: navi+ball
        
        print "Stage I.......................",time.time()-self.st
        while not self.SendState('v','r'):True
        while True:
            self.FindObj('r')
        """
        """
        
        """
        # stage 2: dedicate to find yellow wall
        print "Stage II.......................",time.time()-self.st
        while not self.SendState('v','y'):True
        found=0
        while found!=4:
            found=self.FindObj('y')
        print "obj found"
        self.DumpBall()
        print "dump"
        """
        # stage 3: stay around:one step out+ball+back
        #self.DumpBall()
        """
        if time.time()-self.st<20:        
            #not much time left
            self.DumpBall()
        else:
        while time.time()-self.st>20:        
            pass
        self.DumpBall()
        """
        
        #while not self.SendState('c',('N',False)):True
        """
        while True:
            while not self.SendState('c',('A',True)):True
        """

    def FindObj(self,obj):
        #1. find obj
        state=self.RotFindObj(self.timeout_turn)
        if state==0:            
            #nothing in the view
            state=self.NavFindObj(self.timeout_nav)
        
        #2.track obj 
        if state>0:
            if obj=='r':
                state=self.TrackRedBall(state,self.timeout_track)
            else:
                state=self.TrackYellowWall(self.timeout_track)

        print "done tracking...",state
        return state

    def RotFindObj(self,timeout):        
        #ogj: wall or ball
        print "1:  start rot find obj"
        state=self.SendState2('v','?')                                    
        if state<=0:
            # get started
            self.SendState('c',("T",1))            
            # 1. Big Move            
            st=time.time()
            while state ==0 and time.time()-st<=timeout:
                self.SendState('c',("T",1))
                state=self.SendState2('v','?')                                    
                if state>0:
                    self.pipe_lc.send(('S',0))
                elif state==-1:
                    #may be screwed and no more rot find
                    self.SendState2('c',('K',1))
                    #vision may screw up during sharp turns 
                #print state,"lll"
            #1.1: kill the last Turn
            print "rot obj done",state
        if state>0:
            self.SendState2('c',('u',1))
        return state
    
    def NavFindObj(self,timeout):
        print "2:   start navigation",time.time()
        state=self.SendState2('v','?')                                    
        if state<=0:
            self.SendState2('c',('N',0))
            st=time.time()
            while state ==0 and time.time()-st<=timeout:
                #check vision
                state=self.SendState2('v','?')
                #print state,"popo"
                if state==-1:
                    self.SendState2('c',('K',1))
                    state=0
                elif state>=1: 
                    self.pipe_lc.send(('S',0))
        self.AlignObj(state)
        return state

    def TrackYellowWall(self,timeout):   
        while not self.SendState('v','y'):True
        self.SendState2('c',('L',1))
        #ogj: wall or ball
        print "1:  start rot find obj",time.time()
        state=self.SendState2('v','?')                                    
        if state<4:
            # get started            
            self.SendState('c',("t",1))            
            # 1. Big Move            
            st=time.time()
            while state !=-1 and state!=4 and time.time()-st<=timeout:
                self.SendState('c',("t",1))
                state=self.SendState2('v','?')                                   
                #print state,"now",time.time()
                if state>3:
                    self.pipe_lc.send(('S',0))
                elif state==-1:
                    self.SendState2('c',('K',1))
                    state=0
                    #vision may screw up during sharp turns 
                #print state,"lll"
        if state==4:
            self.SendState2('c',("T",1))            
            self.SendState2('c',('A',1))
        return state

    def TrackRedBall(self,state,timeout):
        #1.suppose we stop in time and the ball is still in the vision                 
        #self.AlignObj(state)
        #2 clear out stuck detection
        print "3:   Start Tracking",time.time()
        
        while not self.SendState('v','c'):True
        #3 go until wall collision or state=4(close to obj) by vision
        pre_s=state
        st=time.time()
        cc=0
        while state!=-1 and state!=4 and time.time()-st<timeout:
            self.AlignObj(state)
            state=self.SendState2('v','?')
            #print "track state",state
            if state==0:
                #print "lose track,undo last adjust until timeout"
                self.AlignObj(4-pre_s)
                cc+=1
                if time.time()-st>timeout or cc>3:
                    self.SendState2('c',('C',1))
                    cc=0
            else:
                pre_s=state
            #print state,"receive"
        if state==4:
            self.pipe_lc.send(('S',0))
            self.SendState2('c',('G',0))
            time.sleep(1.5)
            print "got it "
        elif state==-1:
            self.SendState2('c',('K',1))

        return state

    def AlignObj(self,state):
        if state!=2:
            if state==1:
                self.SendState('c',('U',1))
            elif state==3:
                self.SendState('c',('u',1))
    
    def DumpBall(self):
        print "start dumping!!!!!!!"
        #4. throw ball
        self.SendState2('c',('B',1))
        #5. get out of stuck 
        self.SendState2('c',('K',1))
        print "dumped..."
       
    
        
        

if __name__ == "__main__":

    player=Logic(180)
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
    """
    """
