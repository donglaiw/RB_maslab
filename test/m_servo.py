import sys
sys.path.append("../Control")
import Control as cc
import time



con = cc.Control(0.1)
while not con.ard.portOpened: True # Stand by waiting for Arduino to get ready


con.cservo.setAngle(155)
time.sleep(3)

con.cservo.setAngle(80)
print "send"
#con.cservo.setAngle(80)
#container.setAngle(20)
"""
print "move it "
#container.setAngle(-20)
"""
"""
cc=0
while True:
    container.setAngle(60)
    while cc<1000:
        cc+=1
    cc=0
    
    time.sleep(0.5)
    container.setAngle(-60)
    #time.sleep(0.5)
    while cc<100:
        cc+=1
    cc=0
    break

print "done "
    #time.sleep(0.5)
    #print "wake"
#container.setAngle(-20)
"""
#con.ard.close()
#ard.close()
