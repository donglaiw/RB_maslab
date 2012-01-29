from PIL import Image, ImageDraw
import math, random
import time
import Img2Gif
import thread
import sys
sys.path.append("../Logic/")

import Logic_nothread as ll
import numpy as np

class Simulator():
    def __init__(self):
        self.bg = Image.new("RGB", (600, 600), (255, 255, 255))            
        #self.circles = [[random.randint(100, 500), random.randint(100, 500), 5, 0] for x in xrange(4)]
        #print self.circles
        self.circle_r=5
        #x,y,detected(1: right of center,-1: left of center)
        self.circles =[[480, 300, 0], [113, 112, 0], [306, 285, 0], [412, 474, 0]]                 
        self.draw = ImageDraw.Draw(self.bg)
        self.st = time.time()
        self.total = 10
        self.step = 1
        self.player = ll.Logic()
        self.player.vision.step=self.step
        self.player.control.step=self.step
        self.ratio=5/self.player.control.width_h  
        self.imgs = [Image.new("RGB", (600, 600), (255, 255, 255)) for i in xrange(int(self.total/self.step))] 
        self.bdpt = None
        self.campt = None
        self.cenpt = None
        self.cur = [0, 0, 0]        
        
    def display(self):
        thres = 0
        cc=0
        tt = time.time()        
        while  tt - self.st < self.total:
            if tt - self.st >= thres:
                self.cur = [self.player.control.x, self.player.control.y, self.player.control.angle]
                self.findcarCorner()
                self.CheckCollision()
                #print self.bdpt
                self.campt = self.findcarSensor(self.player.control.camangle)
                self.cenpt = self.findcarSensor(self.player.control.eatangle)
                self.CheckBall() 
                self.player.vision.frame = [self.cenpt[0], self.cenpt[1], [self.cur[0], self.cur[1]], self.circles]
                #print self.player.vision.frame
                #print self.bdpt,self.campt,self.cenpt,self.cur                                               
                if self.player.control.thrown:
                    self.ThrowBall()         
                    self.player.control.thrown=False           
                self.drawbg()
                self.drawcar()                
                #print self.cur[0],self.cur[1],thres
                self.imgs[cc] = self.bg.copy()
                self.player.run()
                #self.bg.save(str(thres) + "ha.png", "PNG")
                #print "frame", thres,self.player.vision.frame[3]
                thres += self.step
                cc+=1
            tt = time.time()
        
    ########################################## 1. Logic Check       ###############################
    def CheckCollision(self):
        for i in range(4):
            if self.bdpt[i][0] < 100 or self.bdpt[i][0] > 500 or self.bdpt[i][1] < 100 or self.bdpt[i][1] > 500:
                self.player.control.bp_val[i] = 1
                delta=[0,0]
                for j in range(2):
                    if self.bdpt[i][j] < 100 or self.bdpt[i][j] > 500:
                        delta[j] = self.bdpt[i][j] - 500 + int(self.bdpt[i][j] < 100) * 400                
                for j in range(4):
                    self.bdpt[j][0] -= delta[0]
                    self.bdpt[j][1] -= delta[1]
                self.cur[0] -= delta[0]
                self.cur[1] -= delta[1]
                #print "Collision",i,"th bumper sensor",self.cur
            else:
                self.player.control.bp_val[i] = 0
        #print self.player.control.bp_val
                

    def CheckBall(self):        
        for i in range(len(self.circles) - 1,-1, -1):
        #for i in range(1):
            #print i,[self.bdpt[1],self.bdpt[0],self.bdpt[2]],[self.bdpt[3],self.bdpt[2],self.bdpt[0]]
            #print self.bdpt
            """
            print "bb:",self.player.vision.ptwithin([self.bdpt[2],self.bdpt[0],self.bdpt[1],self.circles[i][:2]])
            time.sleep(2)            
            print "cc:",self.player.vision.ptwithin([self.bdpt[0],self.bdpt[2],self.bdpt[3],self.circles[i][:2]])
            """
            if self.player.vision.ptwithin([self.bdpt[2],self.bdpt[0],self.bdpt[1],self.circles[i][:2]])!=0 and self.player.vision.ptwithin([self.bdpt[0],self.bdpt[2],self.bdpt[3],self.circles[i][:2]])!=0: 
                #print self.circles,self.player.vision.frame
                del self.circles[i]
                #self.player.control.new=1
                self.player.control.ballnum+=1
                print "got it",self.circles                               

    def ThrowBall(self):
        if self.player.ballnum>0:
            throwpt = [(self.bdpt[3][0] + self.bdpt[0][0]) / 2, (self.bdpt[3][1] + self.bdpt[0][0][1]) / 2]
            self.circles.append([throwpt[0] + 0.1 * (throwpt[0] - self.cur[0]), throwpt[1] + 0.1 * (throwpt[1] - self.cur[1])])
        
    
    ########################################## 2. Plotting Function ###############################
    def drawbg(self):
        #draw boundary
        self.draw.rectangle([100, 100, 500, 500], fill=(255, 255, 255), outline=1)
        self.draw.line([100, 500, 500, 500], fill=(255, 255, 0))
        
        #draw unpicked balls
        for i in range(len(self.circles)):
            self.drawcircle(self.circles[i])                               
    
    def drawcircle(self, circle):
        self.draw.setfill(1)
        self.draw.ellipse([circle[0] - self.circle_r, circle[1] - self.circle_r, circle[0] + self.circle_r, circle[1] + self.circle_r], fill=(255, 255, 255), outline=128)
    
    def drawcar(self):
        #draw body       
        for i in range(3):
            self.draw.line([self.bdpt[i][0], self.bdpt[i][1], self.bdpt[i+1][0], self.bdpt[i+1][1]], fill=0)            
        # the sensor is represented as the red segment at the top        
        self.draw.line([self.bdpt[3][0], self.bdpt[3][1], self.bdpt[0][0], self.bdpt[0][1]], fill=(255, 255, 0))        
        
        #draw sensorline
        self.draw.line([self.cur[0], self.cur[1], self.cenpt[0][0], self.cenpt[0][1]], fill=(255, 255, 0))                
        self.draw.line([self.cur[0], self.cur[1], self.cenpt[1][0], self.cenpt[1][1]], fill=(255, 255, 0))
        
        self.draw.line([self.cur[0], self.cur[1], self.campt[0][0], self.campt[0][1]], fill=128)                
        self.draw.line([self.cur[0], self.cur[1], self.campt[1][0], self.campt[1][1]], fill=128)
        """"""
        
    def findcarCorner(self):
        # the ################
        an = self.cur[2] / 180 * math.pi        
        rotate = np.matrix([[math.cos(an), -math.sin(an)], [math.sin(an), math.cos(an)]])
        x = self.cur[0]
        y = self.cur[1]
        wh = self.player.control.width_h
        hh = self.player.control.height_h        
        pt = [[[x], [y]] + b for b in [(rotate * [[-wh], [hh]]), (rotate * [[-wh], [-hh]]), (rotate * [[wh], [-hh]]), (rotate * [[wh], [hh]])] ]
        pt2 = [i for b in pt for i in b.tolist()]
        self.bdpt = [[pt2[i][0],pt2[i+1][0]] for i in range(0,len(pt2),2)]
    
    
    #should use vision.findcircle    
    def findcarSensor(self, angle):
        an = map(lambda x:self.player.control.st_angle(x),[self.cur[2] + angle, self.cur[2] - angle])
        tanan = [math.tan(a / 180 * math.pi) for a in an]                
        pt = [[0, 0]] * 2
        const = [100, 500]        
        for i in xrange(2):
            pp = [0, 0]
            if int(an[i]) % 180 == 0:
                yp = 0                
            else:                                              
                if an[i] < 180:
                    #yp = self.cur[1] + (2*(int(an[i])<90)-1)*(self.cur[0] - 100) / tanan[i]
                    yp = self.cur[1] + (self.cur[0] - 100) / tanan[i]
                else:
                    #yp = self.cur[1] + (2*(int(an[i])>270)-1)*(500 - self.cur[0]) / tanan[i]                                    
                    yp = self.cur[1] - (500 - self.cur[0]) / tanan[i]
                    pp[0] = 1     
                               
            if int(an[i]) % 180 == 90:
                xp = 0
            else:    
                if an[i] < 270 and an[i] > 90:
                    xp = self.cur[0] + tanan[i] * (self.cur[1] - 100)
                else:
                    xp = self.cur[0] - tanan[i] * (500 - self.cur[1])
                    pp[1] = 1
                
            if yp <= 500 and yp >= 100:
                pt[i] = [const[pp[0]], yp]
            else:
                pt[i] = [xp, const[pp[1]]]
        return pt
                

s = Simulator()

s.display()        
Img2Gif.writeGif('haha.gif', s.imgs, duration=0.1, dither=0)
print "close"

""""""
"""
s.cur=[450,300,0]
s.campt = s.findcarSensor(s.player.control.camangle)
s.cenpt = s.findcarSensor(s.player.control.eatangle)
s.findcarCorner()
s.drawbg()  
s.drawcar()  
        
s.bg.show()
"""



#s.cenpt = s.findcarSensor(s.player.control.eatangle)


#s.player.vision.frame = [s.cenpt[0], s.cenpt[1], [s.cur[0], s.cur[1]], s.circles]
#print s.player.vision.findObj('r')
"""
s.cur=[485.26828610093656, 282.08483439816064, 290.0]
s.bdpt=[[479.47879140045984, 317.11601588825124], [441.8910865690235, 303.4352101552245], [462.4122951685637, 247.05365290807], [500.0, 260.73445864109675]]
s.CheckBall()
#s.cur=[286.86291501, 286.86291501 ,135.0]
"""

"""
s.campt = s.findcarSensor(s.player.control.camangle)
s.cenpt = s.findcarSensor(s.player.control.eatangle)
s.drawcar()            
s.drawcircle(s.circles[0])
s.bg.show()
s.CheckBall()
"""
