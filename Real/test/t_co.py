import sys
sys.path.append('../')
import time
import Control as cc
a=cc.Control()
a.connect()
while not a.portOpened: 
    time.sleep(3)
    a.connect()

