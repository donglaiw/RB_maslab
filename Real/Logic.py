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
        self.vision.start() #handle image processing

        self.switchon=1
        self.target=0
        self.timeout_straight=5
        self.timeout_turn=7  #for 16 discrete turns
        self.timeout_back=1.5
        self.timeout_new=2
        self.timeout_nav=80
        self.st=0; 
        self.dump=0;

    def Connect(self):
        self.control.connect()
        while not self.control.portOpened: 
            time.sleep(1)
            self.control.connect()
        self.control.start()

    def run(self):             
        # stage 1: find yellow wall and dump balls
        self.st=time.time()
        #while not self.SendState('c',('N',False)):True
        """
        while True:
            while not self.SendState('c',('A',True)):True
        """
        while not self.SendState('c',('o',False)):True
        while not self.SendState('v','c'):True
        #self.GoUntilStuck()
        while True:
            #print "ball"
            self.GetBall()
            print "nav"
            self.Nav2YellowWall()
    
    def Close(self):       
        while not self.SendState('c',('O',False)):True
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
            'G':Go straight until stuck
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
            while not self.SendState('c',(msg,True)):True            
            while not self.pipe_lc.poll(0.05): True
            tmp=self.pipe_lc.recv()
        elif option=='v':
            while not self.SendState('v',msg):True            
            while not self.pipe_lv.poll(0.05): True
            tmp=self.pipe_lv.recv()
        return tmp
   
    def SwitchOn(self):        
        tmp='1'       
        while tmp!='0':
            self.SendState('c',('W',True)) 
            while not self.pipe_lc.poll(0.1): True
            tmp=self.pipe_lc.recv()
            print "sss.",tmp,len(tmp)
    
    def Nav2YellowWall(self):
        #start navigation
        print "send Nav...."
        st=time.time()

        while time.time()-st<self.timeout_nav:
            #check vision
            self.SendState('v','?')
            while not self.pipe_lv.poll(0.05):True
            state=self.pipe_lv.recv()
            #print state,"popo"
            if state==-1:
                #stuck
                self.SendState2('c','K')
                #pass
            elif state>=1 and state<=3:
                #detect red ball
                self.pipe_lc.send(('S',False))
                self.GetBall()
                """
                self.AlignBall(state)
                self.GoUntilStuck()
                """
                print "...balll..."
            elif state>=4 and time.time()-self.st>0 and self.dump==0:
                #self.pipe_lc.send(('S',False));
                #detect yellow wall
                print "dump...."
                #self.DumpBall(state)
                #self.dump=1
            #elif state==0: keep moving
            while not self.SendState('c',('N',False)):True
   
    def GoUntilStuck(self):
        #3.get ball: go go go until stuck+get stuck                 
        while not self.SendState('c',('G',False)):True                
        #3.1 go a default time
        time.sleep(3)
        #while not self.SendState('c',('S',1)):True        
        #3.2 go until wall collision by bumper/vision
        state=0
        while state>=0:
            self.SendState('v','?')
            while not self.pipe_lv.poll(0.05):True      
            state=self.pipe_lv.recv()
        self.SendState2('c','K')

    def GetBall(self):
        #0 set vision state        
        #1. find ball
        #print "get started....."
        #state=self.FindObj([0,4,5,6])
        state=self.FindObj([0])
        #print state
        if state<=0:            
            self.SendState2('c','K')
            #print "haha",state,time.time()    
        elif state>=1 and state<=3:
            #2.align ball/ track ball is not practical in small distance... 
            self.AlignBall(state)
            self.GoUntilStuck()
        else:
            #self.pipe_lc.send(('S',False));
            #detect yellow wall
            print "dump...."
            #self.DumpBall(state)
            #self.dump=1

        #print "done........"
    def DumpBall(self,state):
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
       
    def FindObj(self,obj):         
        state=self.SendState2('v','?')
        print "vision answer"
        if state<=0:
            # get started
            self.SendState('c',("T",True))            
            # 1. Big Move            
            st=time.time()
            while state in obj and time.time()-st<=self.timeout_turn:
                self.SendState('c',("T",True))
                self.SendState('v','?')                                    
                while not self.pipe_lv.poll(0.05):True
                state=self.pipe_lv.recv()
                if self.pipe_lc.poll(0.05):
                    while self.pipe_lc.poll():
                        pp=self.pipe_lc.recv()
                #print state,"lll"
            #1.1: kill the last Turn
            #self.pipe_lc.send(('S',False))
            print "obj found"
        return state
    
    def AlignWall(self,state):
        #take it easy...? what if obstacles in between
        if state!=5:
            if state==4:
                self.SendState2('c','U')
            else:
                self.SendState2('c','u')
        """
        #1 check where we are
        while not self.SendState('v','?'):True
        while not self.pipe_lv.poll(0.05):True
        state=self.pipe_lv.recv()
        """
        
    def AlignBall(self,state):
        #take it easy...? what if obstacles in between
        if state!=2:
            if state==1:
                self.SendState2('c','U')
            else:
                self.SendState2('c','u')


        

if __name__ == "__main__":

    player=Logic()
    #Open Ardiuno connection
    player.Connect()
    #Waiting for switch
    player.SwitchOn()
    #GO!GO!!GO!!!
    print "wowow"
    player.start()     
    st=time.time()
    while time.time()-st<180:True
    print "exiting..."

    #Close Process and Ardiuno connection
    player.Close()     
    """
    """
