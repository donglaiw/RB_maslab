import sys
sys.path.append("../Vision")
sys.path.append("../Control")

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
        self.bp_val=None

    def Connect(self):
        self.control.ard.connect()
        while not self.control.ard.portOpened: True
        self.control.ard.start()

    def SwitchOn(self):
        tmp=self.control.GetSwitch()
        #while True:
        while tmp==1 or tmp==-1000:
            #print tmp
            tmp=self.control.GetSwitch()
    
    def SendState(self,option,msg):
        # need time out control
        sent=True
        if option=='v':            
            if not self.pipe_vision.poll(0.1):
                self.pipe_lv.send(msg)
            else:
                sent=False
        else:
            if not self.pipe_control.poll(0.1):
                self.pipe_lc.send(msg)
            else:
                sent=False
            print sent,"sending..",msg
        return sent


    def Close(self):        
        self.control.ard.terminate()
        self.control.terminate()
        self.vision.terminate()
        #self.terminate()
        #Close Ardiuno connection
        self.control.ard.close()

    def run(self):             
        # main thread 
        while True:
            """
            self.GetBumper()
            if sum([self.bp_val[0],self.bp_val[3]])!=0:      
                # front direction blocked          
                self.GetOutStuck()                        
            """
            self.GetBall()           
            #self.DumpBall()
            print "success"
            break
        print "logic done"
        
    def GetBumper(self):
        self.SendState('c',("PP",0))
        while not self.pipe_lc.poll(0.1): True
        self.bp_val=self.pipe_lc.recv()
    """
    def SetVision(self,state):
        self.pipe_lv.send(state)

    def GetVision(self):
        #not congested
        if not self.pipe_vision.poll(0.05):
            self.pipe_lv.send('do')
        while not self.pipe_lv.poll(0.05): True
        #self.pipe_lv.flush()
    """    
        
    def GetBall(self):                
        #find ball

        self.FindObj()      
        print "step 1",time.time()
        #track ball 
           
        #get ball: go go go        
        #submit until success 
        while not self.SendState('c',('G',127)):True
        time.sleep(10)
        """
        self.GetBumper()
        while  sum([self.bp_val[0],self.bp_val[3]])==0 and : True
        #move back            
        if  sum([self.bp_val[0],self.bp_val[3]])!=0:                
            self.GetOutStuck()        
        """
        #while not self.SendState('v','y'):True
        
        """
        if self.control.new==1:
            self.ballcount+=1
            self.control.new=0
            self.current_st = 'y'
        """
                
    def DumpBall(self):        
        print "move"
        # find yellow wall
        self.FindObj()
        print "found"
        # go to wall    
        while not self.SendState('c',('G',127)):True
        #time.sleep(10)

        while  sum([self.bp_val[0],self.bp_val[3]])==0 : True
        print "stuck",self.bp_val
        if self.bp_val[0]==0:
            self.SendState('c',("S",0))    
        else:
            self.SendState('c',("S",1)) 
        #self.control.setState('S')        
        # throw ball
        #print "throw"
        self.SendState('c',('B',0))    
        time.sleep(4)
        #self.ballcount=0
        #move back
        """
        if  sum([self.bp_val[0],self.bp_val[3]])!=0:                
            self.GetOutStuck()
        """
        self.SendState('v','r')

       
    def FindObj(self):
        #clear out in case vision.target still contains last result
        self.SendState('v','found?')
        while not self.pipe_lv.poll(0.05): True
        state=self.pipe_lv.recv()
        print "first try"
        st=time.time()
        if state==0:
            self.SendState('c',("T",1))
            #print "rotate"
            while state==0 and time.time()-st<=20:
                self.SendState('c',("T",1))              
                self.SendState('v','found?')                                    
                while not self.pipe_lv.poll(0.05):True
                state=self.pipe_lv.recv()
                #print "now .. try ",state
            if state==0:
                #get out of stuck
                self.GetOutStuck()
                self.FindObj()            
        print "Obj Found"
        
        
    def TrackObj(self):        
        self.FindObj()
        #print "sooo",self.target
        self.control.GoStraight()
        while True:
            #self.control.goTurn(15*(2*random.randint(0, 1)-1))            
            if self.vision.target==0:
                self.control.adjust(self.target)
                self.vision.FindObj()
            else:
                self.target=self.vision.target
            #print "rotate",self.control.angle,self.target
        print "Ball Found"
                
    def GetOutStuck(self):
        """
        out = 1
        while out!=0 and :d
            self.control.goTurn(15)
            out =  sum([self.bp_val[0],self.bp_val[3]])
            print "rotate to get out of stuck",self.control.x,self.control.y,self.control.angle,out
        
        """
        print "try to get out"
        self.SendState('c',("G",-99))
        time.sleep(10) 
        print "back"
        #while  sum([self.bp_val[0],self.bp_val[3]])!=0: True
        #self.control.setState('T')
        #time.sleep(2)
        self.SendState('c',("T",1))

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

