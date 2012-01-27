import sys
sys.path.append("../Logic")
import Logic as ll
import time 


player=ll.Logic()
#Open Ardiuno connection
player.Connect()

#find ball
st=time.time()
while time.time()-st<180:
    print "go======================="
    while not player.SendState('v','r'):True
    while not player.SendState('c',('G',127)):True    
        
    #monitor IR
    player.GetIr()    
    while player.ir_val[0]<2:
        player.GetIr()
        print "hha",player.ir_val[0]
    print "turn"
    for i in range(4):
        while not player.SendState('c',('T',100)):True
   
   
player.Close()

