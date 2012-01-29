code='''
/*
labeling scheme
+-+-+-+
|d|c|e|
+-+-+-+
|b|a| |
+-+-+-+
| | | |
+-+-+-+
a is the center pixel of a neighborhood.  in the 3 versions of
connectedness:
4:  a connects to b and c  >>>>>>>> pick this
6:  a connects to b, c, and d
8:  a connects to b, c, d, and e
*/

/*
   for( int i = 0; i < 5; i++ )     {    
   printf("%d,",aa[i]);
   }
   
   memset(aa,0,sizeof(ushort)*5);
   
   for( int i = 0; i < 5; i++ )     {    
   printf("%d,",aa[i]);
   }

    memset(label,0,sizeof(ushort)*hh*ww);
    memset(count,0,sizeof(ushort)*maxnumcl[0]);
    memset(labeltable,0,sizeof(ushort)*maxnumcl[0]);
	memset(lhmin,0,sizeof(ushort)*maxnumcl[0]);
	memset(lhmax,0,sizeof(ushort)*maxnumcl[0]);
	memset(lwmin,0,sizeof(ushort)*maxnumcl[0]);
	memset(lwmax,0,sizeof(ushort)*maxnumcl[0]);
*/
    int hindex=0,hindex2=0,windex=0,ntable=0,cc=0;
    int b, c,i0; 
    for( int i = 0; i < hh; i++ )     {    
        windex=0;   
        for( int j = 0; j < ww; j++ ) 
        {    
            if ((mat[hindex+windex]>=thres[0] && mat[hindex+windex]<=thres[3] 
                 && mat[hindex+windex+1]>=thres[1] && mat[hindex+windex+1]<=thres[4]
                 && mat[hindex+windex+2]>=thres[2] && mat[hindex+windex+2]<=thres[5]
                 ) 
                 ||
                (mat[hindex+windex]>=thres[6] && mat[hindex+windex]<=thres[9] 
                 && mat[hindex+windex+1]>=thres[7] && mat[hindex+windex+1]<=thres[10]
                 && mat[hindex+windex+2]>=thres[8] && mat[hindex+windex+2]<=thres[11]
                 )                  
                 )              
                 
                /* if (mat[hindex+windex]>0)*/
            {                
           //printf("%d,%d,%d,%d,%d,%d,%d,%d,%d \\n",i,j,(int)windex/3,mat[hindex+windex],mat[hindex+windex+1],mat[hindex+windex+2],mat2[hindex+windex],mat2[hindex+windex+1],mat2[hindex+windex+2]);
           //printf("%d,%d,%d,%d \\n",i,j,windex,mat[hindex+windex]);
                 cc+=1;
                //if it's 1, get the neighboring pixels b, c                
                if ( j == 0 ){ 
                    b = 0; 
                }else{
                b = label[hindex2+j-1];
                while (b!=labeltable[b]){
                      b=labeltable[b];
                }                                    
                }
                if ( i == 0 ){ 
                    c = 0; 
                }else {
                    c = label[hindex2+j-ww];
                  while (c!=labeltable[c]){
                      c=labeltable[c];
                    }                
                }                                        
                    
                // b and c are labeled
                if ( b!=0 && c!=0 ) 
                {   
                    //simple add the new pixel in
                    label[hindex2+j] = b;
                    count[b] += 1;         
                    lhmax[b]=lhmax[b]>i?lhmax[b]:i;
                    lwmin[b]=lwmin[b]<j?lwmin[b]:j;
                    lwmax[b]=lwmax[b]>j?lwmax[b]:j;
                    if ( b != c ){
                    //need to connect b and c
                        labeltable[c] = b;                            
                    }                    
                } 
                else if ( b!=0 ){             // b is object but c is not
                    label[hindex2+j] = b;
                    count[b] += 1;
                    lhmax[b]=lhmax[b]>i?lhmax[b]:i;
                    lwmin[b]=lwmin[b]<j?lwmin[b]:j;
                    lwmax[b]=lwmax[b]>j?lwmax[b]:j;                    
                    }
                else if ( c!=0 ){               // c is object but b is not
                    label[hindex2+j] = c;
                    count[c] += 1;
                    lhmax[c]=lhmax[c]>i?lhmax[c]:i;
                    lwmin[c]=lwmin[c]<j?lwmin[c]:j;
                    lwmax[c]=lwmax[c]>j?lwmax[c]:j;
                    }
                else 
                {                      
                    // b, c not object - new object
                    //   label and put into table
                    ntable+=1;
                    labeltable[ ntable ] = ntable;
                    lhmin[ntable]=i;
                    lhmax[ntable]=i;
                    lwmin[ntable]=j;
                    lwmax[ntable]=j;                    
                    label[hindex2+j]  =  ntable;
                    count[ntable]    = 1;                    
                } 
            }
            windex+=3;                        
    }
        hindex+=ww*3; 
        hindex2+=ww; 
    }
    
    printf("haha %d woo",cc);
    
    // consolidate component table
    for( int i = 1; i <= ntable; i++ ){
        if (count[i]!=0 && labeltable[i]!=i){       
            i0=i ;
            while  (labeltable[i0]!=i0){
                    i0=labeltable[i0];
                    count[i]=count[i]+count[i0];
                    count[i0]=0;
                    //label(label(:)==i0)=i;
                    lhmax[i]=lhmax[i]>lhmax[i0]?lhmax[i]:lhmax[i0];
                    lhmin[i]=lhmin[i]<lhmin[i0]?lhmin[i]:lhmin[i0];
                    lwmax[i]=lwmax[i]>lwmax[i0]?lwmax[i]:lwmax[i0];
                    lwmin[i]=lwmin[i]<lwmin[i0]?lwmin[i]:lwmin[i0];

            }
            //label(label(:)==i)=i0;
            count[i0]=count[i0]+count[i];
            count[i]=0;        
			lhmax[i0]=lhmax[i];
			lhmin[i0]=lhmin[i];
			lwmax[i0]=lwmax[i];
			lwmin[i0]=lwmin[i];           
        }                                                                                                     
    }
    //no need to reinitialize everything 
    maxnumcl[0]=ntable+1;
        
'''
#label==0 doesn't count
import cv
import numpy as np
from scipy import weave
ww=640            
hh=480

"""
img=cv.LoadImage("1ha.jpg")
mat=np.asarray(img[:,:],dtype=np.uint8)
"""

img=cv.LoadImage("img/1.jpg")
hsv_frame = cv.CreateImage((ww,hh), cv.IPL_DEPTH_8U, 3)
cv.CvtColor(img, hsv_frame, cv.CV_BGR2HSV)
mat=np.asarray(hsv_frame[:,:],dtype=np.uint8)

thres=np.uint8([0,100,100,10,250,255,150,100,100,179,250,255])
label=np.zeros((ww,hh),np.uint16)
maxnumcl=np.array([1000],np.uint16)
count=np.zeros(maxnumcl[0],np.uint16)
labeltable=np.zeros(maxnumcl[0],np.uint16)
lhmin=np.zeros(maxnumcl[0],np.uint16)
lhmax=np.zeros(maxnumcl[0],np.uint16)
lwmin=np.zeros(maxnumcl[0],np.uint16)
lwmax=np.zeros(maxnumcl[0],np.uint16)
"""
aa=np.zeros(5,np.uint16)
aa[1]=5
aa[2]=10
aa[3]=20
aa[4]=30
"""
weave.inline(code, ['mat','thres','ww','hh','label','count','labeltable','lhmin','lhmax','lwmin','lwmax','maxnumcl'])

print [[count[i],lhmin[i],lhmax[i],lwmin[i],lwmax[i]] for i,e in enumerate(count) if e != 0]
cv.Circle(img, (73,196), 23, (0, 0, 255), 3, 8,0)

cv.SaveImage("img/1oo.jpg",img)
