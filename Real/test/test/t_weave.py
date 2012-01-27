from scipy import weave
import numpy as np
import cv, numpy

class TT: 
    def __init__(self):
        self.val=30

""""""
mat = cv.CreateMat(2, 2, cv.CV_32FC1)
cv.Set(mat, 7) 
a=103
#b=cv.LoadImage("9.jpg")
#bbb = numpy.asarray(b[:,:])
bbb=np.zeros(3,int)
ccc=np.ones(3,int)
#print b,bbb
bb = numpy.asarray(mat)
c=[1]


code = """
          for (int i=0; i<50; ++i){ 
               a+=1;
          }
          //
          bbb[0]=ccc[0];
          ccc[0]=abs(-100);          
    """     
#print bb.val,result
weave.inline(code, ['a','bbb','ccc'])
print bbb,ccc

