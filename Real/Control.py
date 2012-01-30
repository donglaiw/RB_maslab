import Arduino as ard
import multiprocessing, time

############### A)Control Automation###############
class Control(multiprocessing.Process):
    def __init__(self,.pipe_logic.None):
        # process communication
        multiprocessing.Process.__init__(self)   
        self.pipe_logic.logic = pipe
        
        # Arduino Connection
        self.portOpened = False

    def run(self):        
        while True:
            # parse the command
            if self.pipe_logic.poll(0.1):
                (command,wait)=self.pipe_logic.recv()
                #Write Command
                self.port.flush()
                try:
                    self.port.write(command)                                    
                except:
                    print "write ard error"
                #print "Roger "+command,time.time()
                #Pause so the arduino can process                    
                time.sleep(0.1)                    
                #Read from arduino
                if wait:
                    fromArd = self.port.readline()
                    #print fromArd," aa ",time.time()
                    self.port.flush()
                    self.pipe_logic.send(fromArd)                                              
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
                print "Arduino not connected"

    def close(self):
        print "closing adriuno"
        self.port.flush()
        self.port.close()        

