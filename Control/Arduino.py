import serial
import multiprocessing, time, Queue

class Arduino(multiprocessing.Process):
    def __init__(self,conn_ard):
        multiprocessing.Process.__init__(self)
        self.pipe = conn_ard
        self.timeout=2         
        self.portOpened = False
        #wait for connection

    def run(self):        
        while True:
            #should protect connection lost...
            # parse the command
            if self.pipe.poll(0.1):
                (portNum,command,delay,wait)=self.pipe.recv()
                #Write Command
                self.port.flush()
                self.port.write(command)                    
                #print "Roger "+command,wait,time.time()
                #Pause so the arduino can process                    
                time.sleep(delay)                    
                #Read from arduino
                if wait:
                    fromArd = self.port.readline()
                    #print fromArd," aa ",time.time()
                    self.port.flush()
                    self.pipe.send(fromArd)                                              
                #self.pipe.flush()            
            """
            else:
                print "no ard"
            """

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
