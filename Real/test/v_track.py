import sys
sys.path.append('../')
import Logic as ll

player=ll.Logic(180)

player.Connect()

while not player.SendState('v','c'):True
#state=player.RotFindObj('r',100)
print "lllll"
state=player.NavFindObj('r',100)
print state
#time.sleep(10)
state=1
player.TrackObj('r',state,5)
"""
"""
player.Close()
