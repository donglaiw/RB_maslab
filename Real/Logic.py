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
        self.timeout_turn=5  #for 16 discrete turns
        self.timeout_back=1.5
        self.timeout_new=2
        self.timeout_nav=180
       

    def Connect(self):
        self.control.connect()
        while not self.control.portOpened: 
            time.sleep(1)
            self.control.connect()
        self.control.start()

    def run(self):             
        # stage 1: find yellow wall and dump balls
        #while not self.SendState('c',('N',Falise)):True
        while True:
            self.Nav2YellowWall()
            #self.GetBall()
        """
        """

    def Close(self):        
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
            """
            if not self.pipe_control.poll(0.05):
                self.pipe_lc.send(msg)
            else:
                sent=False            
            #print sent,self.pipe_lc.poll(0.05),msg,time.time()
        return sent
    
    def SwitchOn(self):        
        tmp=1       
        while tmp!=0:
            self.SendState('c',('W',True)) 
            while not self.pipe_lc.poll(0.1): True
            tmp=self.pipe_lc.recv()
    
    def Nav2YellowWall(self):
        #start navigation
        st=time.time()
        while not self.SendState('c',('N',False)):True
        while time.time()-st<self.timeout_nav:
            #check vision
            print "ask........"
            while not self.SendState('v','?'):True
            while not self.pipe_lv.poll(0.05):True
            state=self.pipe_lv.recv()
            print state,"wooooooooooooooooo"
            if state==-1:
                #stuck
                self.GetOutStuck()
            elif state==1:
                #detect red ball
                #self.AlignBall()
                pass
            elif state>=2:
                #detect yellow wall
                print "dump...."
                self.DumpBall(state)
            #elif state==0: keep moving
   

    def GetBall(self):
        #0 set vision state        
        #1. find ball
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
        #2.align ball/ track ball is not practical in small distance... 
        #self.AlignBall()   
        #3.get ball: go go go                 
        while not self.SendState('c',('G',False)):True                
        #3.1 go a default time
        #time.sleep(3)
        #while not self.SendState('c',('S',1)):True        
        #3.2 go until wall collision by bumper/vision
        self.GetOutStuck(self.timeout_back)

    def DumpBall(self,state):
        #1. visually align the yellow wall after detected
        self.AlignWall(state)
        #2. physically align the yellow wall
        while not self.SendState('c',('A',True)):True            
        while not self.pipe_lc.poll(0.05): True
        tmp=self.pipe_lv.recv()
        print  "aaaa"
        #3. visually check for special cases when bumpers fail

        #4. throw ball
        while not self.SendState('c',('B',True)):True
        while not self.pipe_lc.poll(0.05): True
        tmp=self.pipe_lv.recv()
        print  "bbb"

        #5. get out of stuck 
        while not self.SendState('c',('K',True)):True
        while not self.pipe_lc.poll(0.05): True
        tmp=self.pipe_lv.recv()
        print  "kkk"

       
    def FindObj(self):         
        while not self.SendState('v','?'):True
        while not self.pipe_lv.poll(0.05): True
        state=self.pipe_lv.recv()
        #print "vision answer"
        if state<=0:
            # get started
            self.SendState('c',("T",False))            
            # 1. Big Move            
            st=time.time()
            while state==0 and time.time()-st<=self.timeout_turn:
                self.SendState('c',("T",False))
                self.SendState('v','?')                                    
                while not self.pipe_lv.poll(0.05):True
                state=self.pipe_lv.recv()
            #1.1: kill the last Turn
            self.pipe_lc.send(('',0))
            #while not self.SendState('c',("T",-100)):True
        return state
    
    def AlignWall(self,state):
        #take it easy...? what if obstacles in between
        if state!=5:
            if state==4:
                while not self.SendState('c',('U',False)):True
            else:
                while not self.SendState('c',('u',False)):True
        """
        #1 check where we are
        while not self.SendState('v','?'):True
        while not self.pipe_lv.poll(0.05):True
        state=self.pipe_lv.recv()
        """
        
    def AlignBall(self):
        #suppose FindObj() find the red ball in the view
        while not self.SendState('v','?'):True                                    
        while not self.pipe_lv.poll(0.05):True
        state=self.pipe_lv.recv()
        state+=int(state==0)*120
        #x:0-159
        if state>50 and state<110:
            return 
        elif state<50:
            while not self.SendState('c',("T",False)):True
        elif state>110: 
            while not self.SendState('c',("T",False)):True
        #better to do recursion
        """    
        self.SendState('v','found?')                                    
        while not self.pipe_lv.poll(0.05):True
        state=self.pipe_lv.recv()
        """        


        

if __name__ == "__main__":

    player=Logic()
    #Open Ardiuno connection
    print "cc"
    player.Connect()
    print "ahha"
    #Waiting for switch
    #player.SwitchOn()

    #GO!GO!!GO!!!
    player.start()     
    st=time.time()
    while time.time()-st<180:True
    print "exiting..."

    #Close Process and Ardiuno connection
    player.Close()     

