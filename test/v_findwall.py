import sys
sys.path.append("../Logic")
import Logic as ll
import time 


player=ll.Logic()
#Open Ardiuno connection
player.Connect()
player.SwitchOn()
#dump ball

while not player.SendState('v','y'):True
time.sleep(1)
print "wake"
player.DumpBall()
time.sleep(5)
#player.Close()

