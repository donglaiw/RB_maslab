import serial
import multiprocessing, time

############### A)Control Automation###############
class Control(multiprocessing.Process):
    def __init__(self,pipe=None):
        # process communication
        multiprocessing.Process.__init__(self)   
        self.pipe_logic = pipe
        
        # Arduino Connection
        self.portOpened = False

    def run(self):        
        while True:
            # parse the command
            if self.pipe_logic.poll(0.1):
                #in order to function job killing 
                while self.pipe_logic.poll():
                    (command,wait)=self.pipe_logic.recv()
                #Write Command
                self.port.flush()
                try:
                    self.port.write(command)                                    
                except:
                    print "write ard error"
                print "Roger "+command,time.time()
                #Pause so the arduino can process                    
                #Read from arduino
                if wait:
                    fromArd=''
                    while len(fromArd) == 0 or (fromArd[0]!='d' and fromArd[0]!='0'):
                        fromArd = self.port.readline()
                    print "res ",fromArd,len(fromArd),fromArd[0],time.time()
                    self.port.flush()
                    self.pipe_logic.send(fromArd[0])                                              
                #self.pipe_logic.flush()            

    def connect(self):
        print "call for duty"
        for i in range(0,5):
            try:
                self.port=serial.Serial(port='/dev/ttyACM'+str(i), baudrate=9600, timeout=0)
                time.sleep(2) #Allows the arduino to initialize
                self.port.flush()
                self.portOpened=True
                print "connected"
                break        
            except:
                print "Arduino not connected",i

    def close(self):
        print "closing adriuno"
        self.port.flush()
        self.port.close()        

