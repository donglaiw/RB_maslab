import cv
import sys
sys.path.append("../Logic")
import Logic as ll
import time 


player=ll.Logic()
#Open Ardiuno connection
player.Connect()

print "goo",time.time()
player.SendState(player.pipe_lc,('B',1))
time.sleep(10)

print "wooo"
player.Close()


