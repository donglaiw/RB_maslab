import sys
sys.path.append("../Vision")
import Vision as vv
from Tkinter import *
import time
from PIL import Image,ImageTk
import cv
class MaxLengthEntry(Entry):
    # base class for validating entry widgets
    def __init__(self, master, value="",maxlength=3, **kw):
        apply(Entry.__init__, (self, master), kw)
        self.__value = value
        self.maxlength = maxlength
        
        self.__variable = StringVar()
        self.__variable.set(value)
        self.__variable.trace("w", self.__callback)
        self.config(textvariable=self.__variable)
    
    def setval(self,value):
        self.__variable.set(value)
        
    def __callback(self, *dummy):
        value = self.__variable.get()
        newvalue = self.validate(value)
        if newvalue is None:
            self.__variable.set(self.__value)
        elif newvalue != value:
            self.__value = newvalue
            self.__variable.set(newvalue)
        else:
            self.__value = value

    def validate(self, value):
        if self.maxlength:
            value = value[:self.maxlength]
        return value
         
class Calibrate():
    def __init__(self):
        self.root = Tk()
        self.cali_type = IntVar()
        self.hsvEntry=[Entry()]*12
        self.Imgbox=[Label()]*2
        self.objLabel=Label()
        self.dispsize=(160,120) 
        self.vision=vv.Vision(0.1)
        self.state=['r','y','b']
        self.setUp()

           
    def setUp(self):
        self.root.option_add('*font', ('verdana', 10, 'bold'))
        self.root.title('BotKiller Calibration')        
        self.createHSV(0)
        self.createHSV(1) 
        self.createButtons()
        self.createRadioButtons()
        self.createTxtbox()        
        self.createImgbox()
        #print self.cali_type.get()
        self.root.mainloop()
        
    def createTxtbox(self):
        frametxt = Frame(self.root)        
        self.objLabel=Label(frametxt,text="num of detection: 0")        
        frametxt.pack()
              
    def createImgbox(self):
        frameimg = Frame(self.root)
        self.Imgbox[0] = Label(frameimg)
        self.Imgbox[1] = Label(frameimg)
        self.displayImage()        
        frameimg.pack()
       
    def displayImage(self):
        if self.cali_type.get()==0:
            self.vision.FindCircle()
        else:
            self.vision.FindWall(self.state[self.cali_type.get()])
        self.vision.state=self.state[self.cali_type.get()]
        self.vision.display()
        if self.vision.frame!=None:
            img_pil = Image.fromstring("RGB", self.vision.size, self.vision.frame.tostring()).resize(self.dispsize)
            img_pil2 = Image.fromstring("L", cv.GetSize(self.vision.thresholded), self.vision.thresholded.tostring()).resize(self.dispsize)
            
            img_tk1=ImageTk.PhotoImage(img_pil)
            img_tk2=ImageTk.PhotoImage(img_pil2)
            
            self.Imgbox[0]["image"]=img_tk1
            self.Imgbox[0].photo = img_tk1
            self.Imgbox[0].pack(side=LEFT)
    
            self.Imgbox[1]["image"]=img_tk2
            self.Imgbox[1].photo = img_tk2
            self.Imgbox[1].pack(side=RIGHT)
            
            self.objLabel["text"]="num of detection: "+str(self.vision.numobj)
            self.objLabel.pack(side=LEFT)
        else:
            print "no input"

    def createRadioButtons(self):
        """
        frameradio = Frame(self.root)
        Radiobutton(frameradio, text="Calibrate Red Ball", variable=self.cali_type, value=0,command=self.changeHSV()).pack(side=LEFT)
        Radiobutton(frameradio, text="Calibrate Yellow Wall", variable=self.cali_type, value=1,command=self.changeHSV()).pack(side=LEFT)
        Radiobutton(frameradio, text="Calibrate Blue Wall", variable=self.cali_type, value=2,command=self.changeHSV()).pack(side=LEFT)
        frameradio.pack()
        """
        Radiobutton(self.root, text="Calibrate Red Ball", variable=self.cali_type, value=0,command=self.changeHSV).pack(side=LEFT)
        Radiobutton(self.root, text="Calibrate Yellow Wall", variable=self.cali_type, value=1,command=self.changeHSV).pack(side=LEFT)
        Radiobutton(self.root, text="Calibrate Blue Wall", variable=self.cali_type, value=2,command=self.changeHSV).pack(side=LEFT)
    
    def changeHSV(self):
        for j in range(12):
            self.hsvEntry[j].setval(self.vision.hsv[self.cali_type.get()][j])
        
        #print "changed"
                

    def createButtons(self):
        framebutton = Frame(self.root)
        Button(framebutton, text="Calibrate",command=self.setHsv).pack(side=LEFT)
        Button(framebutton, text="Save",command=self.saveHsv).pack(side=LEFT)
        framebutton.pack()
        
    def setHsv(self):
        #print "hh: set",self.cali_type.get()
        for i in xrange(12):
            self.vision.hsv[self.cali_type.get()][i]=float(self.hsvEntry[i].get().strip())
        self.vision.setThres()            
        self.displayImage()

    def saveHsv(self):
        a=open(str(self.cali_type.get())+".cal","w")
        #print self.cali_type.get()       
        for i in xrange(12):
            a.write(str(self.vision.hsv[self.cali_type.get()][i])+",")
        a.close()
        
    def createHSV(self,index):
        framehsv = Frame(self.root)
        #Create a Label in textFrame
        Label(framehsv,text="HSV "+str(index)+":   H:").pack(side = LEFT)
        self.hsvEntry[index*6] = MaxLengthEntry(framehsv,value=self.vision.hsv[self.cali_type.get()][index*6],width=3)        
        self.hsvEntry[index*6].pack(side = LEFT)
        
        Label(framehsv,text="-").pack(side = LEFT)
        self.hsvEntry[index*6+3] = MaxLengthEntry(framehsv,value=self.vision.hsv[self.cali_type.get()][index*6+3],width=3)
        self.hsvEntry[index*6+3].pack(side = LEFT)
        
        Label(framehsv,text="S:").pack(side = LEFT)    
        self.hsvEntry[index*6+1] = MaxLengthEntry(framehsv,value=self.vision.hsv[self.cali_type.get()][index*6+1],width=3)             
        self.hsvEntry[index*6+1].pack(side = LEFT)
        Label(framehsv,text="-").pack(side = LEFT)
        self.hsvEntry[index*6+4] = MaxLengthEntry(framehsv,value=self.vision.hsv[self.cali_type.get()][index*6+4],width=3)              
        self.hsvEntry[index*6+4].pack(side = LEFT)
        
        Label(framehsv,text="V:").pack(side = LEFT)    
        # Create an hsv1 Widget in framehsv
        self.hsvEntry[index*6+2] = MaxLengthEntry(framehsv,value=self.vision.hsv[self.cali_type.get()][index*6+2],width=3)
        self.hsvEntry[index*6+2].pack(side = LEFT)             
        Label(framehsv,text="-").pack(side = LEFT)
        self.hsvEntry[index*6+5] = MaxLengthEntry(framehsv,value=self.vision.hsv[self.cali_type.get()][index*6+5],width=3)
        self.hsvEntry[index*6+5].pack(side = LEFT)              
        framehsv.pack()

    def quit(self):
        self.root.destroy()


cali=Calibrate()
