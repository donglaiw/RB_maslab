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
st=time.time()
player.GetBall()
time.sleep(10)


"""
while time.time()-st<=170:
    player.GetBall()
    player.GetOutStuck()

"""
#player.Close()

