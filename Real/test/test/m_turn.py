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
st=time.time()
print "turn======================="
while time.time()-st<8:
    while not player.SendState('c',('T',100)):True
    #print "turn"
    #time.sleep(10)
time.sleep(5)
"""
#player.GetBall()


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

