import numpy as np
import time
import math
import threading

class Vision():
    def __init__(self):
        self.x = 0
        self.y = 0
        self.frame = None
        
        self.HSV = [[0, 50, 0, 10, 180, 256,
                   150, 50, 0, 256, 180, 256]] * 3
        self.killed=False
        self.circles=[]
        self.wall=[]
        self.state='r'
        self.target=0
                        
    def findObj(self):
        #print "vision"
        if self.state != '':
            if self.state == 'r':
                self.findCircle()                
                self.target=len(self.circles)                
            else:
                self.findWall(self.state)
                self.target=len(self.wall)
                
    def findCircle(self):
        #found = []          
        self.circles = []
        """
        while self.frame == None and self.killed==False:
            #print "no img"
            pass
        """         
        #print "so..",self.circles
        for i in range(len(self.frame[3])):
            tmp=self.ptwithin(self.frame[:3] + [self.frame[3][i][:2]])
            #print i,tmp,self.frame[:3] + [self.frame[3][i][:2]]   
            if tmp!=0:
                #print tmp
                #found.append([i,tmp])
                self.circles=[tmp]
                #print i,self.frame[:3] + [self.frame[3][i][:2]], found
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
        #print "noo",self.SameSide(v[0], v[1], v[2],  v[3]),v[0], v[1], v[2],  v[3]
        if self.SameSide(v[0], v[1], v[2],  v[3]):
            #print "noo",self.findLR(v[0], v[1], v[2],  v[3])
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


