import Arduino as ard
import multiprocessing, time

############### A)Control Automation###############
class Control(multiprocessing.Process):
    def __init__(self, pipe=None):
        multiprocessing.Process.__init__(self)   

        self.pipe_logic = pipe 
        self.pipe_control, self.pipe_ard = multiprocessing.Pipe()
        
        self.ard = ard.Arduino(self.pipe_ard)        
        
        self.motors = [Motor(self, 0), Motor(self, 1)]#[left,right]
        self.cservo = Servo(self, 7)
        #front-left,back-left,back-right,front-right
        self.bp = [DigitalSensor(self, 24),DigitalSensor(self, 30), DigitalSensor(self, 28), DigitalSensor(self, 26) ]
        self.switch = DigitalSensor(self, 22)
        self.ir=AnalogSensor(self,4)
        self.bp_val = [1, 1, 1, 1]
        self.ir_val = [0, 0, 0, 0]
        self.sensorcount = 0        

        self.angle = 0         
        self.vs_default = 127
        self.vs_start = 127
        self.vt_default = 90
        self.vt_adjust = 70
        self.motorstate = ''
        self.prestate = ''
        self.ballcount = 0
        self.switchon=1
        self.lastdir=1
        self.lastangle=1

    def run(self):
        #self.pipe_logic.send("start")
        #print "send start",time.time()
        while True:
            #received command
            if self.pipe_logic.poll(0.05):
                #may have an additional msg to kill the first one
                while self.pipe_logic.poll():
                    (self.motorstate, num) = self.pipe_logic.recv()
                #receive command from Logic
                #print "Ms:",self.motorstate,len(self.motorstate)                    
                if len(self.motorstate) == 1:
                    #execute move 
                    if self.motorstate == 'G':
                        self.GoStraight(num)                    
                    elif self.motorstate == 'T':
                        self.GoTurn(num)
                    elif self.motorstate == 't':
                        self.GoTurn2(num)
                    elif self.motorstate == 'B':
                        self.ThrowBall()
                    elif self.motorstate == 'S':
                        self.Stop()
                    elif self.motorstate=='U':
                        self.test()
                    self.prestate = self.motorstate                    
                    self.pipe_logic.send(True)
                    #print "send motor",time.time()
                elif len(self.motorstate) == 2:
                    #return changed bumper val
                    if self.motorstate[0]=='B':  
                        self.pipe_logic.send(self.bp_val)
                    elif self.motorstate[0]=='I':
                        self.pipe_logic.send(self.ir_val)
                elif len(self.motorstate) == 3:
                    #return switch val
                    self.GetSwitch()
                    self.pipe_logic.send(self.switchon)                    
                    #print "send",self.switchon
            else:
                #update the sensors
                self.GetBumper(0)
                self.GetIR(0)
                #self.GetSensor()

    def test(self):
        self.motors[0].setVal(127)
        self.motors[1].setVal(127)
        #detect bumpers
        bumped=False
        """
        while bumped==False:
            if con.bp[24].getValue()==
        """

    ##################  2) Control Navigation:   ###############################
    def GoStraight(self,speed):
        #self.dir= 1,go forward; -1,backward        
        if speed==100:
            #backward to get out of stuck
            speed=-self.lastdir*120            
        startmotor = 1        
        #print "t2s",self.prestate,time.time()
        if speed<0:
            direction=-1
        else:
            direction=1

        if self.prestate == 'T':
            #from turn to straight
            if self.lastangle==-1:
                startmotor = 0            
            #print "compensate"
            self.motors[startmotor].setVal(speed)
            time.sleep(0.1)
            self.motors[1 - startmotor].setVal(speed)
        else:
            #print "go1 "
            #print "s_speed",speed-direction*speed/2,direction,speed
            self.motors[startmotor].setVal(speed/2)
            #print "go2 "
            self.motors[1 - startmotor].setVal(speed)
            time.sleep(0.1)
            #print "go3 "
            self.motors[startmotor].setVal(speed)

        #time.sleep(0.1)
        #print "later"
        #print "go ",speed
        #at least started        
        self.lastdir=direction

        #print "go parallel"
        
        
    """      
    def GoTurn(self, angle,option):
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
    
    def GoTurn(self):
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
    """                               
    def GoTurn(self, angle):
        #angle >0 ,turn right;<0 ,turn left
        self.motors[0].setVal(-angle)            
        self.motors[1].setVal(angle)

        if angle > 0:
            #to start up
            self.lastangle=1
        else:
            self.lastangle=-1
        time.sleep(0.3)        
        self.Stop()
        time.sleep(0.5)
        #print "stop",time.time()

    def GoTurn2(self, angle):
        #angle >0 ,turn right;<0 ,turn left
        self.motors[0].setVal(-angle)            
        self.motors[1].setVal(angle)

        if angle > 0:
            #to start up
            self.lastangle=1
        else:
            self.lastangle=-1
        time.sleep(0.8)        
        self.Stop()
        #print "stop",time.time()

    def GoTurn3(self, angle):
        #angle >0 ,turn right;<0 ,turn left
        if angle > 0:
            #to start up
            self.motors[0].setVal(0)
            self.motors[1].setVal(angle)
            self.lastangle=1
        else:
            self.motors[1].setVal(0)
            self.motors[0].setVal(angle)
            self.lastangle=-1
        time.sleep(0.3)        
        self.Stop()
        #time.sleep(0.3)

        #time.sleep(0.4)
        #self.Stop()
        
    def ThrowBall(self):
        print "throw it"
        self.cservo.setAngleT(80)
    
    def Stop(self):
        self.motors[0].setVal(0)
        self.motors[1].setVal(0)

    ##################  2) Control Sensors:   ###############################
    def AddCommand(self, command, portNum, delay, wait): 
        #implemement a nice schedule instead of multiple thread competing
        #print "add com: ",command,time.time()
        self.pipe_control.send((portNum, command, delay, wait))                               
        if wait:
            while not self.pipe_control.poll(0.1): True
            tt=self.pipe_control.recv()
            #print "papa:",tt
            return tt
           
    def GetSwitch(self):
        self.switchon = self.switch.getValue()
        #print "sw: ", switchon
        #return switchon
    
    def GetSensor(self):
        #self.sensorcount=2
        if self.sensorcount == 4:
            self.sensorcount = 0
        self.GetBumper(self.sensorcount)
        """
        if self.sensorcount==0 or self.sensorcount==5:
            self.sensorcount=0
            self.GetBumper(self.sensorcount)
        else:
            self.GetIR(self.sensorcount-4)
        """
        self.sensorcount += 1
        
    def GetBumper(self, num):
        self.bp_val[num] = self.bp[num].getValue()                
        print "Bumper",num,self.bp_val[num],time.time()        
            

    def GetIR(self, num):
        self.ir_val[num] = self.ir.getValue()
        print "IR",num,self.ir_val[num],time.time()


###############Servo Class###############
class Servo:
    def __init__(self, _control, _port):
        self.control = _control
        self.portNum = _port
    def setAngle(self, angle):
        command = "S%(port)02d%(angle)03d" % {'port': self.portNum, 'angle':angle}
        self.control.AddCommand(command, self.portNum, 0.1, False)
###############Motor Class###############
class Motor:
    def __init__(self, _control, _num):
        self.control = _control
        self.motorNum = _num
        self.ID = "M{0}".format(_num)
    def setVal(self, val): #val between 0 and 127
        if val<0:
            val=127-val
        command = "M%(num)01d%(val)03d" % {'num': self.motorNum, 'val':val}
        self.control.AddCommand(command, self.ID, 0.1, False)
###############Analog Sensor Class###############
class AnalogSensor:
    def __init__(self, _control, _port):
        self.control = _control
        self.portNum = _port
    def getValue(self): #Returns a voltage value
        command = "A%(port)02d" % {'port': self.portNum}
        value = self.control.AddCommand(command, self.portNum, 0.1, True) 
        if not value == '':
            try:
                val = int(value) * 5.0 / 1023 #Converts the signal to a voltage
            except:
                val = -1000                            
        else:
            val = -1000
        return val        
###############Digital Sensor Class###############
class DigitalSensor:
    def __init__(self, _control, _port):
        self.control = _control
        self.portNum = _port
    def getValue(self): #Returns a voltage value
        command = "D%(port)02d" % {'port': self.portNum}
        value = self.control.AddCommand(command, self.portNum, 0.15, True)
        if not value == '':
            try:
                val = int(value)
            except:
                val = -1000
                print value
        else:
            val = -1000
        return val
