import time, multiprocessing,random
 
class Logic(multiprocessing.Process):
    def __init__(self):
        multiprocessing.Process.__init__(self)
        self.st =time.time() 
        self.conn_control, self.conn_ard = multiprocessing.Pipe()       
        self.ard=Vision(self.conn_ard)
        self.ard.start()
        self.currstate=1

    def run(self):
        cc=0
        for i in range(10):
            self.conn_control.send(i)
        print "all sent"
        """
        while time.time()-self.st<50000:

            if self.conn_control.poll(0.1):
                if self.conn_control.recv()==1:
                    #print "move on"
                    self.currstate=3-self.currstate
                    self.conn_control.send(self.currstate)
            else:
                pass#print "logic re nothing"

            if not self.conn_ard.poll(0.05):
                tt="do",cc            
                self.conn_control.send(tt)
                print self.ard.state,self.ard.getx(),tt
                cc+=1
        """              
        print "exit logic"
        

class Vision(multiprocessing.Process):
    def __init__(self,conn_ard):
        multiprocessing.Process.__init__(self)
        self.state=1
        self.pipe=conn_ard

    def run(self):
        time.sleep(10)
        print "wake"
        while True:
            if self.pipe.poll(0.5):
                rr=self.pipe.recv()
                #self.changex()
                print self.state ,"II    ========",rr
                #time.sleep(0.2)
            
            """
            if self.pipe.poll(0.1):
                self.state=self.pipe.recv()
                #print "new state"
            if self.state==1:
                time.sleep(0.2) 
                hh=random.randint(0,1)
                self.pipe.send(hh)
                #print "find ball",hh
            else:
                time.sleep(0.2) 
                hh=random.randint(0,1)
                self.pipe.send(hh)
                #print "find wall",hh
            """
    def changex(self):
        self.state+=1   
    def getx(self):
        return self.state
  
if __name__ == "__main__":
    player=Logic()
    player.start()    

    """
    time.sleep(5)
    print "term vision"
    player.ard.terminate()
    time.sleep(5)
    print "term all"
    player.terminate()
    """
