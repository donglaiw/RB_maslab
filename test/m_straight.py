import sys
sys.path.append("../Control")
import Control as cc
import time



con = cc.Control(0.1)
while not con.ard.portOpened: True # Stand by waiting for Arduino to get ready




print "right"
con.motors[0].setVal(120)
con.motors[1].setVal(120)
time.sleep(5)
con.motors[0].setVal(0)
con.motors[1].setVal(0)
""""""
#con.lmotor.setVal(100)
"""
con.goStraight() 
print "now go go go"
time.sleep(100)
con.lmotor.setVal(0)
con.rmotor.setVal(0)
"""
con.ard.close()
print "close"

