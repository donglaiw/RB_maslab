import cv
import sys
sys.path.append("../Logic")
sys.path.append("../Control")
import Control as cc
import Logic as ll
import time 


player=ll.Logic()
#Open Ardiuno connection
player.Connect()

#player.SwitchOn()

#print "goo",time.time()
player.SendState(player.pipe_lc,('G',1))
"""
time.sleep(5)
player.SendState(player.pipe_lc,('T',1))
time.sleep(5)
player.SendState(player.pipe_lc,('S',1))
"""
time.sleep(10)
print "wooo"
player.Close()





"""

control = cc.Control(0.1)
###############  1) wait for the digital switch
control.ControlConnect()

print "waiting for switch"

while control.switchon==1 or control.switchon==-1000: 
    control.ControlSwitch()

print "done "
control.close()
"""
"""
print "ation go !!!"
control.motors[0].setVal(50)
control.motors[1].setVal(50)
time.sleep(3)
print "wake"
control.motors[0].setVal(0)
control.motors[1].setVal(0)

control.killed=True
control.ard.close()
"""


"""

while True:
    time.sleep(5)
    print "send"
    control.conn_control.send(time.time())
    break
control.conn_control.send(0)
#control.ard.close()
"""
