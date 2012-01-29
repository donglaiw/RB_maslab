import serial
import threading, thread, time, Queue
import Sensor as ss

timeout = 2
############### A)Control Automation###############
class Control(threading.Thread):
    def __init__(self,step=1):
        threading.Thread.__init__(self)    
        self.ard=Arduino()
        self.ard.start()
        #[left,right]
        self.motors=[ss.Motor(self.ard,0),ss.Motor(self.ard,1)]         
        self.cservo=ss.Servo(self.ard,7)
        self.bp=[ss.DigitalSensor(self.ard,24),ss.DigitalSensor(self.ard,26),ss.DigitalSensor(self.ard,28),ss.DigitalSensor(self.ard,30)]
        self.switch=ss.DigitalSensor(self.ard,22)
        self.ir=ss.AnalogSensor(self.ard,7)
        self.bp_val = [0, 0, 0, 0]
        self.ir_val = [0, 0, 0, 0]        
        self.dir=1        
        self.angle=0         
        self.vs_default=100
        self.vs_start=90
        self.vt_default=40
        self.vt_adjust=100        
        self.motorstate=''
        self.prestate=''
        self.step = step 
        self.switchon=1
        self.killed=False        
        #thread.start_new_thread(self.ControlBumper,())
        #thread.start_new_thread(self.ControlIR,())        
        #thread.start_new_thread(self.ControlCounter,())

    ################## 1) Independent Threads:   ###############################
    def ControlConnect(self):
        time.sleep(0.5)
        return self.ard.portOpened
    
    def ControlSwitch(self):
        time.sleep(0.5)        
        self.switchon= self.switch.getValue()
        print "sw: ",self.switchon
    
    def ControlBumper(self):
        while self.killed==False:
            for i in range(4):
                self.bp_val[i]=self.bp[i].getValue()
            time.sleep(0.5)
        
    def ControlIR(self):
        while self.killed==False:
            self.ir_val[0]=self.ir.getValue()
            time.sleep(1)

    #def ControlCounter(self):
    def setState(self,state):                   
            self.prestate=self.motorstate
            self.motorstate=state

    def run(self):
        while self.killed==False:   
            #ordered by freq
            #print time.time(),self.motorstate
            if self.motorstate!='':                
                if self.motorstate=='G':
                    self.goStraight()                    
                elif self.motorstate=='T':
                    #containing stop
                    self.goTurn()
                elif self.motorstate=='B':
                    self.throwBall()
                elif self.motorstate=='S':
                    self.stop()
                self.motorstate=''     
        
        self.ard.close()
        print "close control"          

    ##################  2) ControlMotor:   ###############################
    def goStraight(self):
        #self.dir= 1,go forward; -1,backward
        startmotor=0
        if self.prestate=='T' and self.angle<=0:
            #from turn to straight
            startmotor=1
        print "wawa"
        self.motors[startmotor].setVal(self.vs_start)
        #time.sleep(0.1)
        print "later"
        self.motors[1-startmotor].setVal(self.vs_default)
        #compensating
        time.sleep(0.1)        
        self.motors[1-startmotor].setVal(self.vs_start)
        print "go parallel"
        
    """      
    def goTurn(self, angle,option):
        #option=1 turn forward
        #option=-1 turn backward
        #option=0 turn at site
        
        #angle>0,turn right
        if angle>0:
            if option==1:
                self.lmotor.setVal(TBD)
            else if option==-1:
                self.rmotor.setVal(-TBD)
                else:
                    self.lmotor.setVal(TBD)
                self.rmotor.setVal(-TBD)
                
        #angle<0,turn light
        else:
            if option==1:
                self.rmotor.setVal(TBD)
            else if option==-1:
                self.lmotor.setVal(-TBD)
                else:
                    self.rmotor.setVal(TBD)
                    self.lmotor.setVal(-TBD)            
    """        
    def goTurn(self):
        #angle >0 ,turn right;<0 ,turn left
        if int(abs(self.angle))==1:
            #adjusting during going straight
            if self.angle>0:
                self.motors[1].setVal(self.vt_adjust)
                time.sleep(0.1)
                self.motors[1].setVal(self.vs_default)
            else:
                self.motors[0].setVal(self.vt_adjust)
                time.sleep(0.1)
                self.motors[0].setVal(self.vs_default)
        else:
            #from stop to turn
            if self.angle>0:
                self.motors[1].setVal(0)
                self.motors[0].setVal(self.vt_default)                                    
            else:
                self.motors[0].setVal(0)    
                self.motors[1].setVal(self.vt_default)
                           
    def throwBall(self):
        self.cservo.setAngleT(80)
    
    def stop(self):
        self.motors[0].setVal(0)
        self.motors[1].setVal(0)
        
############### B) Control Arduino Connection###############
#Handles all messages incoming from the various servo and motor classes, and adds them to the queueHandler
class Arduino(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.commandDict = {} 
        self.responseDict = {}
        self.commandQueue = Queue.Queue()
        self.lock = threading.Lock()
        self.portOpened = False
        self.killReceived = False #So a force quit will work

    def run(self):
        print "Connecting"
        self.portOpened = self.connect()
        try:
            queueThread = threading.Thread(target=self.queueHandler())
            queueThread.start()
        except Exception as errorText:
            print errorText

    def connect(self):
        if self.portOpened: self.close()
        for i in range(0,5):
            try:
                self.port=serial.Serial(port='/dev/ttyACM'+str(i), baudrate=9600, timeout=0)
                time.sleep(2) #Allows the arduino to initialize
                self.port.flush()
                break        
            except:
                print "Arduino not connected"
                    
        print "Connected"
        return True

    def close(self):
        if self.portOpened:
            print "closing"
            self.port.flush()
            self.port.close()            
            self.portOpened = False
            thread.exit()
        
    def addCommand(self, command, portNum, delay, waitForResponse): #Actuators get the command sent over and over
        #The port is used as a unique identifier, since it's counterproductive to be sending different commands to the same port
        #Delay exists because if there is no pause after a command is sent, the arduino effectively does nothing.
        #However, the best delay may be different between the different commands.
        
        self.lock.acquire()
        self.responseDict[portNum]=''
        self.commandDict[portNum] = [command,delay]
        self.lock.release()

        if waitForResponse:
            initTime = time.time()
            while ((self.responseDict[portNum]=='') and (time.time()-initTime<timeout)): True
            return self.responseDict[portNum]

    def removeCommand(self,portNum):
        #Only required if you want the port to send no commands to the actuator at all
        #Add command changes the command being sent to the port, but isn't very good at removing a commands entirely
        self.lock.acquire()
        del self.commandDict[portNum]
        self.lock.release()

    def updateQueue(self):
        self.queue = Queue.Queue()
        #Can theoretically add a command while this is happening, thus the locking
        self.lock.acquire()
        for portNum,command in self.commandDict.iteritems():
            self.queue.put((portNum,command[0]))
        self.lock.release()

    def queueHandler(self):
        if not self.portOpened: thread.exit()
        while self.portOpened and not self.killReceived:
            
            self.updateQueue()
            #print str(self.queue.qsize())+"  nowwww "
            while not self.queue.empty():
                (portNum,command)=self.queue.get_nowait()

                #Write Command
                self.port.flush()
                self.port.write(command)
                print str(self.queue.qsize())+"  doo "+command

                #Pause so the arduino can process
                delayParam = float(self.commandDict[portNum][1])
                time.sleep(delayParam) #<---maybe
                
                print str(self.queue.qsize())+"  dothis "
                #Read from arduino
                fromArd = self.port.readline()
                self.port.flush()
                self.responseDict[portNum]=fromArd #To make sure commandDict isn't changed by this thread
                time.sleep(.1)
                print "done"
                #remove
                del self.commandDict[portNum]
                #print "{0} : {1}".format(command,fromArd)

            self.portOpened=self.port.isOpen()
