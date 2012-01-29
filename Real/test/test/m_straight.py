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
while time.time()-st<180:
    print "go======================="
    while not player.SendState('v','r'):True
    while not player.SendState('c',('G',127)):True    
    
    state=player.DetectStuck(8)
    if state==-1:
        print "stuck detected"
        player.GetOutStuck(2)
    else:
        player.GetNewPlace(2)
        print "time out"
    
#while not player.SendState('c',('S',127)):True    
    
"""
time.sleep(4)
while not player.SendState(player.pipe_lc,('S',1)):True
st2=time.time()
while not player.SendState(player.pipe_lc,('G',-127)):True
time.sleep(4)
while not player.SendState(player.pipe_lc,('S',1)):True
st3=time.time()
"""

#print "Foward ",st2-st1,"   Backward ",st3-st2

#player.GetBall()

"""
st=time.time()
state=0
player.timeout=10
while state>=0 and time.time()-st<player.timeout:    
    player.SendState('v','found?')                                    
    while not player.pipe_lv.poll(0.05):True
    state=player.pipe_lv.recv()
print "stuck...."
while not player.SendState(player.pipe_lc,('G',-70)):True
#player.SendState(player.pipe_lc,('S',1))    
print "dones"

"""
"""
while time.time()-st<=170:
    player.GetBall()
    player.SendState(player.pipe_lc,('PP',127))
    print "ppp"
"""

player.Close()

