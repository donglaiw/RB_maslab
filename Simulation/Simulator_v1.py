from PIL import Image, ImageDraw
import math, random
import time
import Img2Gif
import sys
sys.path.append("Logic/")
import Logic as ll
import Util
import numpy as np

class Simulator_v1():
    def __init__(self):
        self.bg = Image.new("RGB", (600, 600), (255, 255, 255))            
        #self.circles = [[random.randint(100, 500), random.randint(100, 500), 5, 0] for x in xrange(4)]
        #print self.circles
        self.circle_r=4
        #x,y,detected(1: right of center,-1: left of center)
        #self.circles =[[480, 300, 0], [113, 112, 0], [306, 285, 0], [412, 474, 0]]  
        self.circles =[[120, 200, 0], [150, 290, 0], [250, 225, 0], [425, 190, 0], [375, 340, 0], [305, 460, 0], [255, 360, 0]]                
        self.draw = ImageDraw.Draw(self.bg)
        self.st = time.time()
        self.total = 10
        self.player = ll.Logic(self)
        self.ratio=5/self.player.control.width_h  
        self.imgs = [Image.new("RGB", (600, 600), (255, 255, 255)) for i in xrange(self.total)] 
        self.bdpt = None
        #self.campt = None
        self.cenpt = None
        self.cur = [0, 0, 0]
        #self.sensorangle = [0, 0]
  
        
    def display(self):
        thres = 0
        while  thres < self.total:                    
            #1. update car pos
            #car pos/angle
            self.cur = [self.player.control.x, self.player.control.y, self.player.control.angle]            
            #car boundary
            self.bdpt=self.findcarCorner(self.cur)
            #cat mid frontier
            self.frontmid = [0.5*(self.bdpt[3][0]+self.bdpt[0][0]), 0.5*(self.bdpt[3][1]+self.bdpt[0][1])]                        
            #cat sensor lines                                 
            self.cenpt = self.findcarSensor()   
            """                     
            self.CheckBall() 
            """            
            """
            if self.player.control.thrown:
                self.ThrowBall()         
                self.player.control.thrown=False 
            """            
            
            #3. display            
            self.drawbg()
            self.drawcar()                
            self.imgs[thres] = self.bg.copy()            
            #print self.imgs[thres].getpixel((1,1))                       
            print "Frame", thres,"  vision: ",self.player.vision.target
            
            #4. update player            
            self.player.Strategy0()
            
            #self.player.Strategy1()
            #self.player.Strategy2()
            
            #self.bg.save(str(thres) + "ha.png", "PNG")
            #print "frame", thres
            thres += 1
        
    ########################################## 1. Logic Check       ###############################
    def CheckBall(self):        
        for i in range(len(self.circles) - 1,-1, -1):
            if Util.ptwithin([self.bdpt[2],self.bdpt[0],self.bdpt[1],self.circles[i][:2]])!=0 and Util.ptwithin([self.bdpt[0],self.bdpt[2],self.bdpt[3],self.circles[i][:2]])!=0: 
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
        self.draw.rectangle([0, 0, 600, 600], fill=(0,0,0), outline=1)
        pos=[(100,125),(300,150),(300,100),(510,100),(450,225),(450,450),(375,400),(375,500),(200,500),(200,435),(100,350)]
        self.draw.polygon(pos,fill=(255,255,255),outline=1)                
        self.draw.rectangle([250, 275, 300, 325], fill=(0, 0, 0), outline=1)        
        self.draw.line([300, 200, 300, 150],fill=(0, 0, 0))
        self.draw.line([300, 200, 370, 200],fill=(0, 0, 0))
        self.draw.line([100, 125, 100, 350],fill=(255, 255, 0))            
                    
        #draw unpicked balls
        for i in range(len(self.circles)):
            self.drawcircle(self.circles[i])                              
    
    def drawcircle(self, circle):
        self.draw.setfill(1)
        self.draw.ellipse([circle[0] - self.circle_r, circle[1] - self.circle_r, circle[0] + self.circle_r, circle[1] + self.circle_r], fill=(255, 255, 255), outline=128)
    
    def drawcar(self):
        #draw body       
        for i in range(3):
            self.draw.line([self.bdpt[i][0], self.bdpt[i][1], self.bdpt[i+1][0], self.bdpt[i+1][1]], fill=(0,255,0))      
        #print "haa",self.bdpt      
        
        # the sensor is represented as the red segment at the top        
        self.draw.line([self.bdpt[3][0], self.bdpt[3][1], self.bdpt[0][0], self.bdpt[0][1]], fill=(255, 255, 0))        
        
        #draw sensorline
        self.draw.line([self.frontmid[0], self.frontmid[1], self.cenpt[0][0], self.cenpt[0][1]], fill=(255, 255, 0))                
        self.draw.line([self.frontmid[0], self.frontmid[1], self.cenpt[1][0], self.cenpt[1][1]], fill=(255, 255, 0))
        
        self.draw.line([self.cenpt[0][0], self.cenpt[0][1], self.cenpt[1][0], self.cenpt[1][1]], fill=(255, 255, 0))
        self.draw.line([self.cenpt[2][0], self.cenpt[2][1], self.cenpt[3][0], self.cenpt[3][1]], fill=(255, 255, 0))
        
        
    def findcarCorner(self,cur):
        # the ################
        an = cur[2] / 180 * math.pi        
        rotate = np.matrix([[math.cos(an), -math.sin(an)], [math.sin(an), math.cos(an)]])
        x = cur[0]
        y = cur[1]
        wh = self.player.control.width_h
        hh = self.player.control.height_h        
        pt = [[[x], [y]] + b for b in [(rotate * [[-wh], [hh]]), (rotate * [[-wh], [-hh]]), (rotate * [[wh], [-hh]]), (rotate * [[wh], [hh]])] ]
        pt2 = [i for b in pt for i in b.tolist()]
        return [[pt2[i][0],pt2[i+1][0]] for i in range(0,len(pt2),2)]                    
    
    #should use vision.findcircle    
    def findcarSensor(self):        
        an = map(lambda x:Util.adjust_angle(x),[self.cur[2] + self.player.control.eatangle, self.cur[2] - self.player.control.eatangle])
        #self.sensorangle=an
        sinan = [math.sin(a / 180 * math.pi) for a in an]
        cosan = [math.cos(a / 180 * math.pi) for a in an]
        pt =  [[0, 0]] * 4
        anrange = self.player.control.sensorrange        
        x_sensor = self.frontmid[0]
        y_sensor = self.frontmid[1]
        for i in xrange(2):
            pt[i] = [x_sensor-anrange[1]*sinan[i], y_sensor+anrange[1]*cosan[i]]
        for i in xrange(2):
            pt[i+2] = [x_sensor-anrange[0]*sinan[i], y_sensor+anrange[0]*cosan[i]]                
        return pt           

    def CheckCollision(self,bdpt):        
        center_x = int(self.player.control.x)
        center_y = int(self.player.control.y)
        len = self.player.control.width_h
        wid = self.player.control.height_h
        diag = 2*int(math.sqrt (len*len + wid*wid)) #half the diagnol
                
        j=max(center_y - diag, 0)        
        stuck=0
        while j < center_y+diag and stuck==0:
        #for j in range(center_y - diag, center_y + diag): 
            i=max(center_x - diag, 0)        
            while i < center_x + diag and stuck==0:               
            #for i in range(center_x - diag, center_x + diag):
                test1 = Util.SameSide(bdpt[0], bdpt[2], bdpt[1], [i,j])
                test2 = Util.SameSide(bdpt[0], bdpt[2], bdpt[3], [i,j])
                if test1==True and test2==True:
                    if self.bg.getpixel((i,j)) == (0,0,0):              
                        stuck=1  
                i=i+1
            j=j+1
        print i,j   
        return stuck


#random.seed()
s = Simulator_v1()
s.display()        
Img2Gif.writeGif('haha.gif', s.imgs, duration=0.1, dither=0)