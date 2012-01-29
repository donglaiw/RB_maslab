import cv
import sys
sys.path.append("../Control")
import Control as cc

import time 


control = cc.Control(0.1)
###############  1) wait for the digital switch
while not control.ControlConnect(): True # Wait for the arduino to open port

print "waiting "
while True:
#while control.switchon==1 or control.switchon==-1000: 
    control.ControlSwitch()
"""
print "ation go !!!"
control.motors[0].setVal(50)
control.motors[1].setVal(50)
time.sleep(3)
print "wake"
control.motors[0].setVal(0)
control.motors[1].setVal(0)
"""
""""""
#control.ControlConnect(0)
