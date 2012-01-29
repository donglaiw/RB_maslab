import sys
sys.path.append("../Control")
import Control
import Sensor
import time




ard=Control.Arduino()
motor0=Sensor.Motor(ard,0) #0 is the qik number
motor1=Sensor.Motor(ard,1) #1 is the qik number
ard.start()

while not ard.portOpened: True # Stand by waiting for Arduino to get ready


# Task 1 move in the straight line
motor0.setVal(100)
motor1.setVal(100)

time.sleep(3)

#Task 2  turn in a circle for 180 degree
  #  r=2 inch,b=13 inch
 
motor0.setVal(100)
motor1.setVal(100)

time.sleep(3)
 
# Task 3 move in the straight line back to home
motor0.setVal(100)
motor1.setVal(100)

time.sleep(3)

ard.close()
