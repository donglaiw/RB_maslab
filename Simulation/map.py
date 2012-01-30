from PIL import Image, ImageDraw
import numpy as np
import sys,math
sys.path.append("Logic/")
import Logic as ll
import Util

class Simulator():
    def __init__(self):
        self.bg = Image.new("RGB", (600, 600), (0, 0, 0))            
        self.circle_r=4
        #x,y,detected(1: right of center,-1: left of center)
        self.circles =[[120, 200, 0], [150, 290, 0], [250, 225, 0], [425, 190, 0], [375, 340, 0], [305, 460, 0], [255, 360, 0]]                 
        self.draw = ImageDraw.Draw(self.bg)
        self.player = ll.Logic()

        
 
    def display(self):
        thres = 0
        cc=0
        self.cur = [self.player.control.x, self.player.control.y, self.player.control.angle]
        self.findcarCorner()
        #self.campt = self.findcarSensor(self.player.control.camangle)
        self.cenpt = self.findcarSensor(self.player.control.eatangle)
        self.drawbg()

        self.drawcar()                
        self.bg.show()


            
    ########################################## 2. Plotting Function ###############################
    
    
    def drawbg(self):
        #draw boundary
        
        ###############
        #self.draw.rectangle([100, 100, 500, 500], fill=(255, 255, 255), outline=1)
        #self.draw.line([100, 500, 500, 500], fill=(255, 255, 0))
        ###############        
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
            self.draw.line([self.bdpt[i][0], self.bdpt[i][1], self.bdpt[i+1][0], self.bdpt[i+1][1]], fill=0)            
        # the sensor is represented as the red segment at the top        
        self.draw.line([self.bdpt[3][0], self.bdpt[3][1], self.bdpt[0][0], self.bdpt[0][1]], fill=(255, 255, 0))  
        
              
        
        #draw sensorline
        self.draw.line([self.frontmid[0], self.frontmid[1], self.cenpt[0][0], self.cenpt[0][1]], fill=(255, 255, 0))                
        self.draw.line([self.frontmid[0], self.frontmid[1], self.cenpt[1][0], self.cenpt[1][1]], fill=(255, 255, 0))
        
        #self.draw.line([self.frontmid[0], self.frontmid[1], self.campt[0][0], self.campt[0][1]], fill=128)                
        #self.draw.line([self.frontmid[0], self.frontmid[1], self.campt[1][0], self.campt[1][1]], fill=128)
        
        
        
        
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
        
        ######Middle of the frontier#######
        self.frontmid = [0.5*(self.bdpt[3][0]+self.bdpt[0][0]), 0.5*(self.bdpt[3][1]+self.bdpt[0][1])]

    
     
    #should use vision.findcircle     
    def findcarSensor(self, angle):
        an = map(lambda x:Util.adjust_angle(x),[self.cur[2] + angle, self.cur[2] - angle])
        tanan = [math.tan(a / 180 * math.pi) for a in an]
        sinan = [math.sin(a / 180 * math.pi) for a in an]
        cosan = [math.cos(a / 180 * math.pi) for a in an]
        pt = [[0, 0]] * 2
        sensorlength = 3*self.player.control.height_h
        x_sensor = self.frontmid[0]
        y_sensor = self.frontmid[1]
        for i in xrange(2):
            pt[i] = [x_sensor-sensorlength*sinan[i], y_sensor-sensorlength*cosan[i]]
                
        return pt    
        
        
        
        
        """
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
        """

 
                
if __name__ == "__main__":
    s = Simulator()
    
    s.display() 
           
