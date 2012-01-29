import sys
sys.path.append("../Logic")
import Logic as ll
import time 


player=ll.Logic()
#Open Ardiuno connection
player.Connect()

#player.SwitchOn()
for i in range(10):
    while not player.SendState('c',('BB',1)):True
    player.GetBumper()
    print i,"  ppp...",player.bp_val[0],time.time()

"""
st=time.time()
while time.time()-st<180:
    print "go======================="
    while not player.SendState('v','r'):True
    #while not player.SendState('c',('G',127)):True    
    
    print "wowow",player.bp_val[0]
    while player.bp_val[0]==1:
        while not player.SendState('c',('BB',1)):True
        player.GetBumper()
        print player.bp_val[0],time.time()
    
    print "back"
    #while not player.SendState('c',('G',100)):True
    print "turn"
    for i in range(4):
        #while not player.SendState('c',('T',100)):True
        pass
"""
#player.Close()

