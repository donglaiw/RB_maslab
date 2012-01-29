import cv
import sys
sys.path.append("../Logic")
sys.path.append("../Control")
import Control as cc
import Logic as ll
import time 


player=ll.Logic()
#Open Ardiuno connection
player.Connect()

player.SendState('c','U')


player.Close()
