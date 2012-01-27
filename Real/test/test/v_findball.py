import cv
import sys
sys.path.append("../Logic")
import Logic as ll
import time 


player=ll.Logic()
#Open Ardiuno connection
player.Connect()
#player.SwitchOn()
#find ball
player.GetBall()
#clean the vision stuck
#while not player.SendState('v','r'):True

"""
print "find it......................."
player.FindObj()
print "found"
while not player.SendState('c',('G',127)):True

state=player.DetectStuck(8)
if state==-1:
    player.GetOutStuck(1)
"""

"""
time.sleep(2)
"""
"""
while time.time()-st<180:
    player.GetBall()
"""
#player.Close()

