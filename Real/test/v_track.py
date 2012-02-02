import sys
sys.path.append('../')
import Logic as ll

player=ll.Logic(180)

player.Connect()


#state=player.RotFindObj('r',100)
state=player.NavFindObj('r',100)
print state

"""
state=1
player.TrackObj('r',state,5)
"""
player.Close()
