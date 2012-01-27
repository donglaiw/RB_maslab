import sys
sys.path.append("../Logic")
import Logic as ll
sys.path.append("../Control")
import Control as cc
import multiprocessing,time


pipe_lc, pipe_control = multiprocessing.Pipe()
control = cc.Control(pipe_control)
#connect ardiuno
control.ard.connect()
while not control.ard.portOpened: True
control.ard.start()
control.start()
time.sleep(5)
print "start it "
pipe_lc.send(("G",1))
while not pipe_control.poll(0.1):
    pipe_lc.send(("PP",1))
    while not pipe_lc.poll(0.1): True
    state=pipe_lc.recv()
    if state[2]+state[3]>1:


"""
while True:
    pipe_lc.send(("PP",0))
"""

"""
player=ll.Logic()
#Open Ardiuno connection
player.Connect()

player.SwitchOn()
#find ball
#player.GetBall()

#dump ball
while True:
    #print "want  ",time.time()    
    player.GetBumper()
    time.sleep(5)
    print "do it========================"
    #print "get ",player.bp_val,"   ",time.time()
#print "goo",time.time()
#print "wooo"
player.Close()

"""






#Sensor broke...
#player.SwitchOn()


"""

control = cc.Control(0.1)
###############  1) wait for the digital switch
control.ControlConnect()

print "waiting for switch"

while control.switchon==1 or control.switchon==-1000: 
    control.ControlSwitch()

print "done "
control.close()
"""
"""
print "ation go !!!"
control.motors[0].setVal(50)
control.motors[1].setVal(50)
time.sleep(3)
print "wake"
control.motors[0].setVal(0)
control.motors[1].setVal(0)

control.killed=True
control.ard.close()
"""


"""

while True:
    time.sleep(5)
    print "send"
    control.conn_control.send(time.time())
    break
control.conn_control.send(0)
#control.ard.close()
"""
