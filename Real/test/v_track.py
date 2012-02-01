import sys
sys.path.append('../')
import Logic as ll

player=ll.Logic(180)

player.Connect()


state=player.RotFindObj('r',100)
print state

player.close()
