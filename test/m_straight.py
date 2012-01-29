import cv
import sys
sys.path.append("../Logic")
import Logic as ll
import time 


player=ll.Logic()
#Open Ardiuno connection
player.Connect()
player.SwitchOn()
#find ball
player.SendState(player.pipe_lc,('G',127))
time.sleep(5)
#player.GetBall()

"""
while time.time()-st<=170:
    player.GetBall()
"""
player.Close()

