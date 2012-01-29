import cv
import sys
sys.path.append("../Logic")
import Logic as ll
import time 

player=ll.Logic()
###############  1) wait for the digital switch
while not player.control.ControlConnect(): True # Wait for the arduino to open port

#print "nothing"
"""
while player.control.switchon==1 or player.control.switchon==-1000: 
    player.control.ControlSwitch()    
"""

#1. naive	
"""
print "go "
player.control.start()
player.control.setState('G')
time.sleep(5)
print "stop"
player.control.setState('S')
print "close"
player.close()
print "what else"
"""

#2. find and charge at the ball
#player.vision.start()
st=time.time()
player.vision.FindCircle()
if player.vision.target==0:
    player.control.motors[0].setVal(0)
    player.control.motors[1].setVal(80)                                        
    while player.vision.target==0:
        player.vision.FindCircle()
    player.control.motors[0].setVal(80)
print "found",time.time()-st
time.sleep(6)
player.close()
player.control.ard.close()

"""
player.vision.start() 
player.control.start()
while time.time()-player.st<player.total:
    player.findObj()
"""

#3. Catch the ball  
#player.start()

#player.control.ControlConnect(0)
