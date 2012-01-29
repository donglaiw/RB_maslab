import sys
sys.path.append("../Control")
import Control
import Sensor
import time

ard=Control.Arduino()
Bumper=Sensor.DigitalSensor(ard,22)
 
ard.start()

while not ard.portOpened: True # Stand by waiting for Arduino to get ready

tmp=Bumper.getValue()
while True:
    time.sleep(0.5)
    tmp=Bumper.getValue()
    print time.time(),tmp

