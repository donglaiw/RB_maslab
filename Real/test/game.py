import sys
sys.path.append("../Logic")
import Logic as ll
import time 


player=ll.Logic()
#Open Ardiuno connection
player.Connect()

#Waiting for switch
#player.SwitchOn()

#GO!GO!!GO!!!
player.start()     
st=time.time()
while time.time()-st<180:True
print "exiting..."

#Close Process and Ardiuno connection
player.Close()     

