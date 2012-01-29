#calibration of IR sensor
#distance 10 2.25-2.3
#distance 20 1.31

import sys
sys.path.append("../Control")
import Control
import Sensor
import time

ard=Control.Arduino()
IR=Sensor.AnalogSensor(ard,4)
bumper=Sensor.DigitalSensor(ard,30)
motor0=Sensor.Motor(ard,0)
motor1=Sensor.Motor(ard,1)
ard.start()

while not ard.portOpened: True # Stand by waiting for Arduino to get ready

# move straight until it hits the wall
distance=0
   
motor0.setVal(100)
motor1.setVal(100)
print "test done"
#motor1.setVal(100)
cc=0
while distance<2:
    time.sleep(0.1)
    cc=cc+1
    distance=IR.getValue()
    print str(cc)+"  dis  "+str(distance)

print '##################################################################'

# stop 
#motor0.setVal(0)
#motor1.setVal(0)

#time.sleep(1)

# turn right

motor0.setVal(0)
motor1.setVal(-99)
time.sleep(1)


# move on

motor0.setVal(0)
motor1.setVal(0)


ard.close()

