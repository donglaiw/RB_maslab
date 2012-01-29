import cv
import sys
sys.path.append("../Logic")
import Logic as ll
import time 


player=ll.Logic()
#Open Ardiuno connection
player.Connect()
player.SwitchOn()
print "start"

player.timeout=2
player.SendState('c',("T",1))
st=time.time()
cc=0
while time.time()-st<=player.timeout:
    #player.SendState('c',("T",1))              
    player.SendState('v','found?')
    print "sent"                                    
    while not player.pipe_lv.poll(0.05):True
    state=player.pipe_lv.recv()
    cc+=1
    print cc,time.time()-st,state

print str(cc)+"pictures taken"
player.Close()

