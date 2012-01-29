import numpy as np
import time
import math
import threading

class Vision(threading.Thread):
    def __init__(self,starttime,total):
        threading.Thread.__init__(self)        
        self.x = 0
        self.y = 0
        self.frame = None
        
        self.HSV = [[0, 50, 0, 10, 180, 256,
                   150, 50, 0, 256, 180, 256]] * 3
        self.st = starttime
        self.total = total
        self.circles=[]
        self.wall=[]
        self.state='r'
        self.target=0
        self.step=1
                        
    def run(self):
        while time.time()-self.st<self.total:
            if self.state != '':
                if self.state == 'r':
                    self.findCircle()
                    self.target=len(self.circles)
                    #print self.state,self.target
                else:
                    self.findWall(self.state)
                    self.target=len(self.wall)
        print "Vision done"
        
    def findCircle(self):
        self.circles = []
        while self.frame == None and time.time()-self.st<self.total:
            #print "no img"
            pass                    
        for ii in range(len(self.frame[3])):
            #print "yo",ii,self.frame[3],len(self.frame[3])
            #self.frame[3][ii]
            if ii < len(self.frame[3]):
                tmp=self.ptwithin(self.frame[:3] + [self.frame[3][ii][:2]])            
                if tmp!=0:
                    self.circles=[tmp]
                    #print ii,self.frame[:3] + [self.frame[3][i][:2]], found
                    break        
    
    def findLR(self, p1, p2, a, b):
        v1=(p1 - a)/math.sqrt(np.dot(p1 - a,p1 - a))
        v2=(p2 - a)/math.sqrt(np.dot(p2 - a,p2 - a))
        v0=(b - a)
        if np.dot(v0,v1)>=np.dot(v0,v2):
            return 1
        else:
            return -1
    
    def findWall(self, state):                 
        if self.frame[0][1] == 500 and self.frame[1][1] == 500:
            self.wall=[1]
        else:
            self.wall=[]

    def ptwithin(self, v):                
        #v : two bd lines, center,query pt
        for i in range(3):
            v[i] = np.array(v[i])
        #print "noo",v
        if self.SameSide(v[0], v[1], v[2],  v[3]):
            #print "noo",v
            return self.findLR(v[0], v[1], v[2],  v[3])
        else:
            return 0

    def SameSide(self, p1, p2, a, b):
        cp1 = np.cross(b - a, p1 - a)
        cp2 = np.cross(b - a, p2 - a)
        if cp1*cp2 <= 0 and np.dot(b - a, p1 - a)>=0 and np.dot(b - a, p2 - a)>=0:
            return True
        else:
            return False
