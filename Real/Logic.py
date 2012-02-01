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
        self.s1=self.timeout_turn+self.timeout_nav
        self.timeout_s1=100
        self.st=0; 
        self.dump=0;


############################################1 Process communicaiton ######################################
    def Connect(self):
        self.control.connect()
        while not self.control.portOpened: 
            time.sleep(1)
            self.control.connect()
        self.control.start()

    def run(self):             
        while not self.SendState('c',('o',0)):True
        while not self.SendState('v','c'):True
        # stage 1: eat as many red balls as possible: navi+ball
        """
        while time.time()-self.st+self.s1<self.timeout_s1:
            self.FindRedBall()
        """
        # stage 2: dedicate to find yellow wall
        """
        found=0
        while found==0:
            found=self.FindYellowWall()
        """
        # stage 3: stay around:one step out+ball+back

        self.st=time.time()
        #while not self.SendState('c',('N',False)):True
        """
        while True:
            while not self.SendState('c',('A',True)):True
        """
        #self.GoUntilStuck()
        while True:
            #print "ball"
            self.GetBall()
            print "nav"
            self.Nav2YellowWall()
    
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
            while not self.SendState('c',(msg,1)):True            
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
    def FindObj(self,obj):
        #1. find ball
        state=self.RotFindObj(obj,self.timeout_turn)
        if state==0:            
            #nothing in the view
            state=self.NavFindObj(obj,self.timeout_nav)
        
        #2.track ball 
        if state>0:
            self.TrackObj(obj,state)

    def RotFindObj(self,obj,timeout):        
        #ogj: wall or ball
        while not self.SendState('v',obj):True
        print "rot 2 find obj"
        state=self.SendState2('v','?')                                    
        print "state.."
        if state<=0:
            # get started
            self.SendState('c',("T",1))            
            # 1. Big Move            
            st=time.time()
            while state ==0 and time.time()-st<=timeout:
                self.SendState('c',("T",1))
                self.SendState('v','?')                                    
                while not self.pipe_lv.poll(0.05):True
                state=self.pipe_lv.recv()
                if state==-1:
                    self.SendState2('c','K')
                    state=0
                    time.sleep(1.5)
                    #vision may screw up during sharp turns 
                #print state,"lll"
            #1.1: kill the last Turn
            self.pipe_lc.send(('S',0))
            print "rot obj done"
        return state
    
    def NavFindObj(self,obj,timeout):
        #start navigation
        print "nav 2 find obj"        
        while not self.SendState('v',obj):True
        st=time.time()
        while state ==0 and time.time()-st<=timeout:
            #check vision
            self.SendState('v','?')
            while not self.pipe_lv.poll(0.05):True
            state=self.pipe_lv.recv()
            #print state,"popo"
            if state==-1:
                #stuck,in case ir can't detect it
                self.SendState2('c','K')
                while not self.SendState('c',('N',0)):True
                state=0
            elif state>=1: 
                self.pipe_lc.send(('S',0))
                break;   
        return state

   
    def TrackObj(self,obj,state):
        #1.suppose we stop in time and the ball is still in the vision                 
        self.AlignObj(obj,state)
        while not self.SendState('c',('G',0)):True                
        #2 go a default time
        time.sleep(0.1)
        #3 go until wall collision or state=4(close to obj) by vision
        state=0
        while state!=-1 and state!=4:
            self.SendState('v','?')
            while not self.pipe_lv.poll(0.05):True      
            state=self.pipe_lv.recv()
            self.AlignObj(state)
            print state
        if state==4:
            if obj=='r':
                time.sleep(1.5)
                print "got it "
            else:
                #using IR for final fine align
                self.DumpBall()
                print "dump it "

    def AlignObj(self,state):
        if state!=2:
            if state==1:
                self.SendState2('c','U')
            else:
                self.SendState2('c','u')
    
    def DumpBall(self):
        #1. visually align the yellow wall after detected
        #self.AlignWall(state)
        #2. physically align the yellow wall
        self.SendState2('c','A')
        #3. visually check for special cases when bumpers fail
        #4. throw ball
        self.SendState2('c','B')
        #5. get out of stuck 
        self.SendState2('c','K')
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
