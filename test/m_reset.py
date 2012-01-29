import sys
sys.path.append("../Motor")
import Control as cc
import time



con = cc.Control(time.time(),1000)
while not con.ard.portOpened: True # Stand by waiting for Arduino to get ready


con.motors[1].setVal(0)

