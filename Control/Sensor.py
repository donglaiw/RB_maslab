###############Servo Class###############
class Servo:
    def __init__(self, _arduino, _port):
        self.arduino = _arduino
        self.portNum = _port

    def setAngle(self,angle):
        command ="S%(port)02d%(angle)03d" %{'port': self.portNum, 'angle':angle}
        self.arduino.addCommand(command, self.portNum, 0.5, False)
        #self.arduino.removeCommand(self.portNum)
        
###############Analog Sensor Class###############
class AnalogSensor:
    def __init__(self, _arduino, _port):
        self.arduino = _arduino
        self.portNum = _port

    def getValue(self): #Returns a voltage value
        command ="A%(port)02d" %{'port': self.portNum}
        value = self.arduino.addCommand(command, self.portNum, 0.5, True) 
        if not value=='':
            voltageVal = int(value)*5.0/1023 #Converts the signal to a voltage
        else:
            voltageVal = -1000

        #self.arduino.removeCommand(self.portNum)
        return voltageVal
        
###############Motor Class###############
class Motor:
    def __init__(self, _arduino, _num):
        self.arduino = _arduino
        self.motorNum = _num
        self.ID = "M{0}".format(_num)

    def setVal(self,val): #val between 0 and 255
        command ="M%(num)01d%(val)03d" %{'num': self.motorNum, 'val':val}
        self.arduino.addCommand(command, self.ID, 0.5, True)
        #self.arduino.removeCommand(self.ID)


###############Digital Sensor Class###############
class DigitalSensor:
    def __init__(self, _arduino, _port):
        self.arduino = _arduino
        self.portNum = _port

    def getValue(self): #Returns a voltage value
        command ="D%(port)02d" %{'port': self.portNum}
        value = self.arduino.addCommand(command, self.portNum, 0.15, True)
        if not value=='':
            try:
                val = int(value)
            except:
                val=-1000
                print value
        else:
            val = -1000

        #self.arduino.removeCommand(self.portNum)
        return val
