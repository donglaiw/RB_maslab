import Arduino as ard
import multiprocessing, time

timeout = 2
############### A)Control Automation###############
class Control(multiprocessing.Process):
    def __init__(self, pipe=None):
        multiprocessing.Process.__init__(self)   

        self.pipe_logic = pipe 
        self.pipe_control, self.pipe_ard = multiprocessing.Pipe()
        
        self.ard = ard.Arduino(self.pipe_ard)        
        
        self.motors = [Motor(self, 0), Motor(self, 1)]#[left,right]
        self.cservo = Servo(self, 7)
        self.bp = [DigitalSensor(self, 30),DigitalSensor(self, 24), DigitalSensor(self, 28), DigitalSensor(self, 26) ]
        self.switch = DigitalSensor(self, 22)
        #self.ir=AnalogSensor(self,7)

        self.bp_val = [0, 0, 0, 0]
        #self.ir_val = [0, 0, 0, 0]
        self.sensorcount = 0        

        self.angle = 0         
        self.vt_default = 127
        self.vt_adjust = 127
        self.motorstate = ''
        self.prestate = ''
        self.ballcount = 0

    def run(self):
        while True:
            if self.pipe_logic.poll(0.05):
                #receive command from Logic
                (self.motorstate, num) = self.pipe_logic.recv()
                if len(self.motorstate) == 2:
                    #return changed bumper val  
                    self.pipe_logic.send(self.bp_val)                                       
                print self.motorstate
                #ordered by freq            
                if self.motorstate == 'G':
                    self.GoStraight(num)                    
                elif self.motorstate == 'T':
                    self.GoTurn(num)
                elif self.motorstate == 'B':           
                    self.ThrowBall()
                elif self.motorstate == 'S':
                    self.Stop(num)
                elif self.motorstate=='U':
                    self.test()
                self.prestate = self.motorstate
                self.motorstate = ''
            else:
                #update the sensors
                #print "nooo1"
                #self.GetSensor()
                #pass

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
        startmotor = 1
        print "t2s",self.prestate,time.time()
        if self.prestate == 'T' and self.angle <= 0:
            #from turn to straight
            startmotor = 0
            print "compensate"
            self.motors[startmotor].setVal(speed)
            time.sleep(0.5)
        else:
            self.motors[startmotor].setVal(speed)
        #time.sleep(0.1)
        print "later"
        self.motors[1 - startmotor].setVal(speed)
        """
        #compensating
        time.sleep(0.1)        
        self.motors[startmotor].setVal(self.vs_default*direction)
        """
        print "go parallel"
        
        
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
        if angle > 0:
            #to start up
            self.motors[0].setVal(0)            
            self.motors[1].setVal(self.vt_adjust)
            time.sleep(0.7)
            self.motors[1].setVal(0)
        else:
            self.motors[1].setVal(0)
            self.motors[0].setVal(self.vt_adjust)
            time.sleep(0.7)
            self.motors[0].setVal(0)
            print "stop it"

    def ThrowBall(self):
        print "throw it"
        self.cservo.setAngle(155)
        time.sleep(3)
        self.cservo.setAngle(80)
    
    def Stop(self,num):
        if num==2:
            self.motors[0].setVal(0)
            self.motors[1].setVal(0)
        else:
            self.motors[num].setVal(0)
        

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
        switchon = self.switch.getValue()
        print "sw: ", switchon
        return switchon
    
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
        if (num==0 or num==3) and self.bp_val[num]==0:
            print num,self.bp_val[num]
            

    def GetIR(self, num):
        self.ir_val[num] = self.ir.getValue()

    #def ControlCounter(self):

###############Servo Class###############
class Servo:
    def __init__(self, _control, _port):
        self.control = _control
        self.portNum = _port
    def setAngle(self, angle):
        command = "S%(port)02d%(angle)03d" % {'port': self.portNum, 'angle':angle}
        self.control.AddCommand(command, self.portNum, 0.15, False)

###############Motor Class###############
class Motor:
    def __init__(self, _control, _num):
        self.control = _control
        self.motorNum = _num
        self.ID = "M{0}".format(_num)
    def setVal(self, val): #val between 0 and 255
        command = "M%(num)01d%(val)03d" % {'num': self.motorNum, 'val':val}
        self.control.AddCommand(command, self.ID, 0.15, False)
###############Analog Sensor Class###############
class AnalogSensor:
    def __init__(self, _control, _port):
        self.control = _control
        self.portNum = _port
    def getValue(self): #Returns a voltage value
        command = "A%(port)02d" % {'port': self.portNum}
        value = self.control.AddCommand(command, self.portNum, 0.15, True) 
        if not value == '':
            try:
                val = int(value) * 5.0 / 1023 #Converts the signal to a voltage
            except:
                val = -1000
                print value            
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
