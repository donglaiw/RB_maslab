import numpy as np
import math


def ptwithin(v):                
    #v : two bd lines, center,query pt
    for i in range(3):
        v[i] = np.array(v[i])
            
    if SameSide(v[0], v[1], v[2],  v[3]):
        #whether it's centered
        #find the pt @ 1/3 of the line segment between normalized v[0]-v[2],v[1]-v[2]
        newv1= v[2]+(v[1]-v[2])*math.sqrt(np.dot(v[0] - v[2],v[0] - v[2]))/math.sqrt(np.dot(v[1]-v[2],v[1]-v[2]))       
        if SameSide(v[0], 3*v[0]/4+newv1/4, v[2],  v[3]):
            return 1
        elif SameSide(3*v[0]/4+newv1/4, v[0]/4+3*newv1/4, v[2],  v[3]):
            return 3
        else:
            return 2
    else:
        #not in the range
        return 0

"""
a is the corner pt
p1-a,p2-a are the two rays starting from a
b is the query point

Check if b is within the triangle of p1-a-p2  
"""
def SameSide( p1, p2, a, b):
    cp1 = np.cross([b[0]-a[0], b[1]-a[1]], [p1[0]-a[0], p1[1]-a[1]])
    cp2 = np.cross([b[0]-a[0], b[1]-a[1]], [p2[0]-a[0], p2[1]-a[1]])
    #cp2 = np.cross(b-a, p2-a)
    #if cp1*cp2 <= 0 and np.dot(b - a, p1 - a)>=0 and np.dot(b - a, p2 - a)>=0:
    if cp1*cp2 <= 0 and np.dot([b[0]-a[0], b[1]-a[1]], [p1[0]-a[0], p1[1]-a[1]])>=0 and np.dot([b[0]-a[0], b[1]-a[1]], [p2[0]-a[0], p2[1]-a[1]])>=0:
        return True
    else:
        return False

def FindLR( p1, p2, a, b):
    #a: ref pt
    #p1,p2: bd pt
    #b: query pt 
    v1=(p1 - a)/math.sqrt(np.dot(p1 - a,p1 - a))
    v2=(p2 - a)/math.sqrt(np.dot(p2 - a,p2 - a))
    v0=(b - a)
    if np.dot(v0,v1)>=np.dot(v0,v2):
        return 1
    else:
        return -1
def adjust_angle(angle):
    if angle > 360:
        angle -= 360
    elif angle < 0:
        angle += 360
    return angle
