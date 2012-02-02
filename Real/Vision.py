import multiprocessing, thread, time
import cv
import string
import numpy as np
from scipy import weave
#opencv HSV: 0-179,0-255,0-255

class Vision (multiprocessing.Process):
    def __init__(self, pipe):
        #1. process communication
        multiprocessing.Process.__init__(self)  
        self.pipe_vision = pipe
        self.target = 0

        #2. image caputuring
        self.capture = cv.CaptureFromCAM(0)
        """
        #useless...
        cvSetCaptureProperty(self.capture, cv.CV_CAP_PROP_FRAME_WIDTH, 160);
        cvSetCaptureProperty(self.capture, cv.CV_CAP_PROP_FRAME_HEIGHT,120);
        """
        self.frame=cv.QueryFrame(self.capture)
        #cv.SaveImage("hh.jpg",self.frame)                
        self.camsize = (640, 480)        
        self.sample_size = (160, 120)
        self.small_size=(80,60,3)
        self.step=self.sample_size[0]/self.small_size[0]
        self.hsv = [[0] * 12] * 4        
        self.loadHSV()
        self.state='y'

        #3. for circle
        self.sample = cv.CreateImage(self.sample_size, cv.IPL_DEPTH_8U, 3)        
        self.hsv_frame = cv.CreateImage(self.sample_size, cv.IPL_DEPTH_8U, 3)
        self.hsv_np=None
        self.circles = np.array([0] * 102, np.uint16) #the largest circle
        self.thresholded =None
        self.thresholded2 =None
        self.dis_small = None        

        self.circle_thres = self.sample_size[0] * self.sample_size[1] / 1600
        self.label = np.zeros(self.sample_size, np.uint16)
        self.maxnumcl = np.array([1000], np.uint16)
        self.count = np.zeros(self.maxnumcl[0], np.uint16)
        self.labeltable = np.zeros(self.maxnumcl[0], np.uint16)
        self.lhmin = np.zeros(self.maxnumcl[0], np.uint16)
        self.lhmax = np.zeros(self.maxnumcl[0], np.uint16)
        self.lwmin = np.zeros(self.maxnumcl[0], np.uint16)
        self.lwmax = np.zeros(self.maxnumcl[0], np.uint16)
        
        #3.1 blue line
        self.blueline = np.zeros(self.sample_size[0], np.uint16)
        self.blue_thres = int(0.01* self.sample_size[1])
        #print self.blue_thres
              
        #3.2. yellow/green wall
        self.wall = []
        self.width_thres_y = 0.7 * self.small_size[0]
        self.width_thres_g = 0.05 * self.small_size[0]
        self.height_thres = 0.06 * self.small_size[1]        
        self.w_count=np.zeros(3, np.uint8)


        #5. for stuck
        self.small = np.zeros(self.small_size, np.uint8)
        self.same_thres = 15
        self.diff_count = np.zeros(1, np.uint16)
        self.stuck_thres = self.small_size[0] * self.small_size[1] / 100
        self.stuck_acc=0
        self.stuck_acc_thres=10
        
        #6. set C-code
        self.GenCode()

        #7. debug drawing mode
        self.Init_Binary()
        self.saved=0
              
    def run(self):
        #self.frame = cv.QueryFrame(self.capture)
        while True:
            #1. check for logical communication
            if self.pipe_vision.poll(0.05):             
                #command from logic
                rec=self.pipe_vision.recv()             
                #print "vision got sent",rec
                if rec=='?':
                    """
                    if self.target!=0:
                        print self.target,"sent"
                    """
                    self.pipe_vision.send(self.target)
                elif rec=='c':
                    print "clear out"
                    self.stuck_acc=0
                    self.target=0
                else:
                    self.state=rec
                    self.stuck_acc=0
                    self.target=0

            #print "0: " ,self.state
            #2. vision process
            self.frame = cv.QueryFrame(self.capture)
            #print "111: " ,time.time()
            if self.frame!=None:
                cv.Resize(self.frame,self.sample)
                cv.CvtColor(self.sample, self.hsv_frame, cv.CV_BGR2HSV)
                self.hsv_np= np.asarray(self.hsv_frame[:, :], dtype=np.uint8)

                #2.1 check for stuck
                self.CheckStuck()
                self.Copy()
                #print "2: ",time.time()
                if self.stuck_acc >= self.stuck_acc_thres:
                    #if accumulates, send out the alarm to logic
                    self.target = -1
                    self.stuck_acc = self.stuck_acc_thres                                                
                    #print "alarm ...........target"
                else:
                    self.target=0
                    #2.2 check for obj
                    self.FindLine()
                    if self.state=='r':
                        self.FindCircle()
                    else:
                        self.FindWall('y')                
                #print "3: ",time.time()
            else:
                print "no img"


################################################# 1 Obj Detection #######################################
    def loadHSV(self):


        for i in range(4):
            a = open(str(i)+".cal")
            line = a.readline().split(",")
            self.hsv[i] = [string.atoi(x) for x in line[:-1]]
            a.close()
        

        self.setThres()
    

    def Copy(self):          
        mat = self.hsv_np
        mat2 = self.small
        ww = self.small_size[0]            
        hh = self.small_size[1]
        step=self.step
        weave.inline(self.codecopy, ['mat', 'mat2', 'ww', 'hh', 'step'])
    
    def FindCircle(self):        
        mat=self.hsv_np
        thres = np.uint8(self.hsv[0])
        ww = self.sample_size[0]            
        hh = self.sample_size[1]
        thres_size = self.circle_thres
        label = self.label
        maxnumcl = self.maxnumcl
        count = self.count
        labeltable = self.labeltable
        lhmin = self.lhmin
        lhmax = self.lhmax
        lwmin = self.lwmin
        lwmax = self.lwmax
        circle = self.circles      
        #blue line filtering
        self.FindLine()
        blueline = self.blueline  
        #print "wawa",self.maxnumcl
        weave.inline(self.codecircle, ['mat', 'thres', 'ww', 'hh', 'label', 'count', 'labeltable', 'lhmin', 'lhmax', 'lwmin', 'lwmax', 'maxnumcl', 'thres_size', 'circle', 'blueline'])
        #print "haha",self.maxnumcl
        #self.circle = circle
        #self.maxnumcl = maxnumcl
        #print [e for e in count if e>10],thres_size        
        #print count
        #print circle[0],circle[1],circle[2]
        #print self.circles[0],self.circles[1]
        self.target=lhmin[0]        
        if self.target>0:
            print "found ball!!!!!!!!!!!!!!!!!!!",time.time()               
            """
            cv.SaveImage(str(time.time())+"r.jpg",self.sample)
            self.state='r'
            self.display()
            cv.SaveImage(str(time.time())+"rr.jpg",self.sample)
            self.saved=1
            """
        """
        if self.target!=0:
            self.display()
            print "save"
            cv.SaveImage(str(time.time())+"ww.jpg",self.small)
        """
        
    def FindWall(self,opt):
        #threshold+rowsum+findRect
        mat = self.small
        if opt=='y':
            thres = np.uint8(self.hsv[1])
            w_thres = self.width_thres_y
        else:
            thres = np.uint8(self.hsv[3])
            w_thres = self.width_thres_g

        ww = self.small_size[0]            
        hh = self.small_size[1]
        h_thres = self.height_thres
        blueline=self.blueline/self.step
        w_count=self.w_count
        #print thres
        weave.inline(self.codewall, ['mat', 'thres', 'w_thres', 'h_thres', 'ww', 'hh', 'blueline','w_count'])
        #print maxlen ,self.height_thres
        self.target = blueline[0]
        #print "wall: ",w_count,self.target,w_thres/3
        if self.target>0:
            print "found wall!!!!!!!!!!!!!!!!!!!",self.wall
        
        
        """
        if self.target>0 :
            if opt=='y':
                # check yellow closer?
                self.FindWall2(opt)
                print "found wall!!!!!!!!!!!!!!!!!!!",self.wall
                if self.wall!=[] and self.wall[1]>4*hh/5:
                    self.target=4
            
            if self.saved==0:
                cv.SaveImage(str(time.time())+"kkppy.jpg",self.small)
                self.state=opt
                self.display()
                cv.SaveImage(str(time.time())+"kkppyy.jpg",self.small)
                self.saved=2
         """
        
            
    def FindLine(self):
        #threshold+rowsum+findRect
        mat = self.hsv_np
        thres = np.uint8(self.hsv[2])
        ww = self.sample_size[0]            
        hh = self.sample_size[1]
        b_thres = self.blue_thres
        blueline = self.blueline
        weave.inline(self.codeline, ['mat', 'thres', 'b_thres', 'ww', 'hh', 'blueline'])
        #print self.blueline
    
    def CheckStuck(self):          
        mat = self.hsv_np
        mat2 = self.small
        thres = self.same_thres
        ww = self.small_size[0]            
        hh = self.small_size[1]
        diffcount = self.diff_count
        step=self.step        
        weave.inline(self.codestuck, ['mat', 'mat2','thres',  'ww', 'hh', 'diffcount','step'])
        #print self.diff_count[0],self.stuck_thres
        if self.diff_count[0] < self.stuck_thres:
            self.stuck_acc+=1
            #print self.stuck_acc
        else:
            self.stuck_acc = 0
        #print self.stuck_acc,time.time()
        
################################################# 2 calibration display #######################################
    def display(self):
        self.numobj = 0
        if self.state == 'r':
            self.numobj = 0
            i=0
            while self.circles[3*i] != 0:
                radius = int(self.circles[i * 3 + 2])
                #print "circle", i, radius, int(self.circles[i * 3]), int(self.circles[i * 3 + 1])
                center = (int(self.circles[i * 3]), int(self.circles[i * 3 + 1]))
                #print self.circles.height,center
                cv.Circle(self.sample, center, radius, (0, 0, 255), 3, 8, 0)
                self.numobj +=1
                i+= 1
        elif self.state == 'y' or self.state == 'g':
            self.numobj = self.w_count
            if self.wall != []:
                cv.Resize(self.sample,self.dis_small)
                #print self.wall,"wooo"
                cv.Rectangle(self.dis_small, (0, self.wall[0]), (self.small_size[0], self.wall[1]), (0, 0, 255), 5)
        elif self.state== 'b':
            #blue line
            for i in range(self.sample_size[0]):
                cv.Set2D(self.sample, self.blueline[i], i, (0,0,0,0)); 
                if self.blueline[i] > self.blue_thres:
                    cv.Set2D(self.sample, self.blueline[i] - self.blue_thres, i, (0,0,0,0)) 
                    self.numobj = 1

    def setThres(self):  
        self.r0min = cv.Scalar(self.hsv[0][0], self.hsv[0][1], self.hsv[0][2], 0)
        self.r0max = cv.Scalar(self.hsv[0][3], self.hsv[0][4], self.hsv[0][5], 0)
        
        self.r1min = cv.Scalar(self.hsv[0][6], self.hsv[0][7], self.hsv[0][8], 0)
        self.r1max = cv.Scalar(self.hsv[0][9], self.hsv[0][10], self.hsv[0][11], 0)
        
        self.y0min = cv.Scalar(self.hsv[1][0], self.hsv[1][1], self.hsv[1][2], 0)        
        self.y0max = cv.Scalar(self.hsv[1][3], self.hsv[1][4], self.hsv[1][5], 0)
        
        self.b0min = cv.Scalar(self.hsv[2][0], self.hsv[2][1], self.hsv[2][2], 0)
        self.b0max = cv.Scalar(self.hsv[2][3], self.hsv[2][4], self.hsv[2][5], 0)            

        self.g0min = cv.Scalar(self.hsv[3][0], self.hsv[3][1], self.hsv[3][2], 0)
        self.g0max = cv.Scalar(self.hsv[3][3], self.hsv[3][4], self.hsv[3][5], 0)            

    def Init_Binary(self):
        self.thresholded = cv.CreateImage(self.sample_size, cv.IPL_DEPTH_8U, 1)
        self.thresholded2 = cv.CreateImage(self.sample_size, cv.IPL_DEPTH_8U, 1)
        self.dis_small = cv.CreateImage(self.small_size[:2], cv.IPL_DEPTH_8U, 3)        
        self.thres_small = cv.CreateImage(self.small_size[:2], cv.IPL_DEPTH_8U, 1)

    def ThresWall(self, state):        
        #need to process the latest one        
        if state == 'y':
            cv.InRangeS(self.hsv_frame, self.y0min, self.y0max, self.thresholded)
            #cv.InRangeS(self.dis_small, self.y0min, self.y0max, self.thres_small)
        elif state=='b':
            cv.InRangeS(self.hsv_frame, self.b0min, self.b0max, self.thresholded)
            #cv.InRangeS(self.dis_small, self.b0min, self.b0max, self.thres_small)
        elif state=='g':
            cv.InRangeS(self.hsv_frame, self.g0min, self.g0max, self.thresholded)
            #cv.InRangeS(self.dis_small, self.b0min, self.b0max, self.thres_small)


    def ThresCircle(self):        
        #if self.frame is not None :
        cv.InRangeS(self.hsv_frame, self.r0min, self.r0max, self.thresholded)
        cv.InRangeS(self.hsv_frame, self.r1min, self.r1max, self.thresholded2)
        cv.Or(self.thresholded, self.thresholded2, self.thresholded)                                           
 
    def FindWall2(self,opt):
        #threshold+rowsum+findRect
        mat = self.small
        if opt=='y':
            thres = np.uint8(self.hsv[1])
            w_thres = self.width_thres_y
        else:
            w_thres = self.width_thres_g
            thres = np.uint8(self.hsv[3])
        ww = self.small_size[0]            
        hh = self.small_size[1]
        h_thres = self.height_thres
        s_p = np.uint8([100, 100])
        e_p = np.uint8([100, 100])
        maxlen = np.zeros(2, np.uint8)       
        blueline=self.blueline/self.step
        weave.inline(self.codewall2, ['mat', 'thres', 'w_thres', 'h_thres', 'ww', 'hh', 's_p', 'e_p', 'maxlen','blueline'])
        if maxlen[1] >= self.height_thres:
            self.wall = (s_p[1], e_p[1])
        else:
            self.wall = []

################################################# 3 embedded C code #######################################
    def GenCode(self):            
        #input:['mat', 'thres', 'ww', 'hh', 'label', 'count', 'labeltable', 'lhmin', 'lhmax', 'lwmin', 'lwmax', 'maxnumcl', 'thres_size', 'circle', 'blueline']
        self.codecircle = '''
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

    memset(label,0,sizeof(ushort)*hh*ww);
    memset(count,0,sizeof(ushort)*maxnumcl[0]);
    memset(labeltable,0,sizeof(ushort)*maxnumcl[0]);
	memset(lhmin,0,sizeof(ushort)*maxnumcl[0]);
	memset(lhmax,0,sizeof(ushort)*maxnumcl[0]);
	memset(lwmin,0,sizeof(ushort)*maxnumcl[0]);
	memset(lwmax,0,sizeof(ushort)*maxnumcl[0]);

    int hindex=0,hindex2=0,windex=0,ntable=0,cc=0,hstep=3*ww;
    int b, c,i0; 

        
        for( int j = 0; j < ww; j++ ) 
        {        
        //for each width
        hindex=blueline[j]*hstep;
        hindex2=blueline[j]*ww;
        for( int i = blueline[j]; i < hh; i++ )     {    
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
                 
            {                
           //printf("%d,%d,%d,%d,%d,%d,%d,%d,%d \\n",i,j,(int)windex/3,mat[hindex+windex],mat[hindex+windex+1],mat[hindex+windex+2],mat2[hindex+windex],mat2[hindex+windex+1],mat2[hindex+windex+2]);
           //printf("%d,%d,%d,%d \\n",i,j,windex,mat[hindex+windex]);
                 //cc+=1;
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
            hindex+=hstep; 
            hindex2+=ww;
    }        
         windex+=3;  
    }    
    //printf("nonzero elements %d \\n",cc);   
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
    
    // find circles
    hindex2=0;
    c=0;
    hstep=0;
    for( int i = 1; i <= ntable; i++ ){
        if(count[i]>=thres_size ){
        if(count[i]>hstep){
        c=hindex2;
        hstep=count[i];
        }
        hindex=lhmax[i]-lhmin[i]+1;
        windex=lwmax[i]-lwmin[i]+1;
        //some shape constraint and in the middle range
        //if(hindex>5 && windex>5 && lwmin[i]+(int)windex/2>ww/4&& lwmin[i]+(int)windex/2<ww*3/4){
        if(hindex>2 && windex>2 && hindex<50 &&windex<50){
        circle[hindex2*3+1]=lhmin[i]+(int)hindex/2;
        circle[hindex2*3]=lwmin[i]+(int)windex/2;
        circle[hindex2*3+2]=hindex>windex?hindex:windex;
        hindex2++;
        }
        //printf("c:%d,%d,%d,%d\\n",thres_size,hindex2,hindex,windex);
        }        
    }
    //a little hacky to pass variables...
        if (hindex2==0){
            lhmin[0] = 0;}
        else if(circle[c*3]<0.3*ww){
            lhmin[0] = 1;}
        else if (circle[c*3]>0.7*ww){
            lhmin[0] = 3;}
        else{
            if (circle[c*3+1]>2*hh/3){
            lhmin[0] = 4;
            }else{
            lhmin[0] = 2;}
            }
    //end criteria of the circles
    circle[hindex2*3]=0;
        '''        
        #input:['mat', 'thres', 'w_thres', 'h_thres', 'ww', 'hh', 's_p', 'e_p', 'maxlen','step','blueline','w_count']
        self.codewall = '''
        int kill=0,rowsum=0,hindex=0,windex=0,hstep=3*ww;
        int range[4] ={0,(int)ww/3,(int)2*ww/3,ww};
        memset(w_count,0,sizeof(ushort)*3);
    
        for (int k=0; k<3; ++k){

        for (int j=range[k]; j<range[k+1]; ++j){/*each width*/
             hindex=hstep*blueline[j];                             
             rowsum=0;
        for (int i=blueline[j]; i<hh; ++i){/*each height*/
            if(mat[hindex+windex]>=thres[0] && mat[hindex+windex]<=thres[3] 
                 && mat[hindex+windex+1]>=thres[1] && mat[hindex+windex+1]<=thres[4]
                 && mat[hindex+windex+2]>=thres[2] && mat[hindex+windex+2]<=thres[5]){
                     rowsum+=1;
                 }
             hindex+=hstep;             
             }
             windex+=3;
             /*
             if (rowsum>0){
             printf("cc %d,%d,%d,%d,%d\\n",j,k,blueline[j],rowsum,windex);
             }
             */
             if (rowsum>=h_thres){                    
               w_count[k]+=1;
                }   
            }
        }
        //printf("ww:   %d,%d,%d,%f\\n",w_count[0],w_count[1],w_count[2],w_thres/3);
        if (w_count[1]>=w_thres/3){
           // in the middle
        if (w_count[0]>=w_thres/3&&w_count[2]>=w_thres/3){
                blueline[0]=4;
              }else{
                blueline[0]=2;
                }
            }
        else{         
            if(w_count[0]>w_thres/3){
                blueline[0]=1;
            }else if (w_count[2]>w_thres/3){
                blueline[0]=3;
            }else{
                blueline[0]=0;
            
            }        
        }

        '''
        #input:['mat', 'thres', 'w_thres', 'h_thres', 'ww', 'hh', 's_p', 'e_p', 'maxlen','step']
        self.codewall2 = '''
        int kill=0,rowsum=0,hindex=0,windex=0,hstep=3*ww;
        for (int i=0; i<hh; ++i){/*each height*/
             rowsum=0;
             windex=0;
             //printf("ww %d,%d,%d\\n",thres[0],thres[1],thres[2]);
             rowsum=0;
             for (int j=0; j<ww; ++j){/*each width*/
                 if(mat[hindex+windex]>=thres[0] && mat[hindex+windex]<=thres[3] 
                 && mat[hindex+windex+1]>=thres[1] && mat[hindex+windex+1]<=thres[4]
                 && mat[hindex+windex+2]>=thres[2] && mat[hindex+windex+2]<=thres[5]){
                     rowsum+=1;
                 }
             windex+=3;
             }
             hindex+=hstep;             
            //take the last segment as 0...
             if (rowsum>=w_thres && i<hh-1){                    
             //printf("%d,%d,%f,%d,%d,%d,%d\\n",i,rowsum,w_thres,s_p[0],e_p[0],maxlen[0],maxlen[1]);     
                if (s_p[0]==100){
                    s_p[0]=i; 
                    kill=0;
                }else if(kill==0){
                    e_p[0]=i;
                    maxlen[0]+=1;
                }
            }else{
                kill=1;
             //printf("well...%d \\n",maxlen[0]);     
                if (maxlen[0]!=0){
             //printf("ccc:  %d,%d\\n",maxlen[0],maxlen[1]);     
                    if( maxlen[0]>maxlen[1]){
                        maxlen[1]=maxlen[0];
                        s_p[1]=s_p[0];
                        e_p[1]=e_p[0];
                        maxlen[0]=0;
                    }else{
                        maxlen[0]=0;
                        s_p[0]=100;
                        e_p[0]=100;
                    }
                }else{
                        s_p[0]=100;
                        e_p[0]=100;		
		            }
                }   
            }

          // if wall found, is it in the center?
         if(maxlen[1] >= h_thres){
         int sl=0,sr=0,ss=s_p[1],ee=e_p[1];
        for (int i=ss; i<=ee; ++i){/*each height*/
             hindex=ww*i;
             for (int j=0; j<ww/4; ++j){/*each width*/
                 windex=j*3;
                 if(mat[hindex+windex]>=thres[0] && mat[hindex+windex]<=thres[3] 
                 && mat[hindex+windex+1]>=thres[1] && mat[hindex+windex+1]<=thres[4]
                 && mat[hindex+windex+2]>=thres[2] && mat[hindex+windex+2]<=thres[5]){
                     sl+=1;
                 }
             }
             for (int j=(int)3*ww/4; j<ww; ++j){/*each width*/
                 windex=j*3;
                 if(mat[hindex+windex]>=thres[0] && mat[hindex+windex]<=thres[3] 
                 && mat[hindex+windex+1]>=thres[1] && mat[hindex+windex+1]<=thres[4]
                 && mat[hindex+windex+2]>=thres[2] && mat[hindex+windex+2]<=thres[5]){
                     sr+=1;
                 }
            }
         }
         /*
*/
        if(sl>maxlen[1]*w_thres/4){
            if(sr>maxlen[1]*w_thres/4){
                e_p[0]=5;
            }else{
                e_p[0]=4;
            }
        }else{
            if(sr>maxlen[1]*w_thres/4){
                e_p[0]=6;
            }else{
                e_p[0]=5;
            }        
        }
}
            '''    
        #input :['mat', 'thres', 'b_thres', 'ww', 'hh', 'blueline']
        self.codeline = '''        
        int hindex=0,windex=0,hstep=3*ww,count,bb;
        memset(blueline,0,sizeof(ushort)*ww);
        for (int j=0; j<ww; ++j){/*each width*/
        count=0;
        hindex=0;
        bb=0;
        for (int i=0; i<hh; ++i){/*each height*/                     
                 if(mat[hindex+windex]>=thres[0] && mat[hindex+windex]<=thres[3] 
                 && mat[hindex+windex+1]>=thres[1] && mat[hindex+windex+1]<=thres[4]
                 && mat[hindex+windex+2]>=thres[2] && mat[hindex+windex+2]<=thres[5]){
                     count+=1;
                     if(count>=b_thres){
                     blueline[j]=i;
                     bb=1;
                     }
                 }else if(bb==1){
                 break;
                 }
             hindex+=hstep;        
             }
        windex+=3;             
         }             
            '''    
        #input:['mat', 'mat2','thres',  'ww', 'hh', 'diffcount','step']        #mat2 is smaller
        self.codestuck = '''        
        int hindex=0,windex=0,hstep=3*ww,tmp1,tmp2;        
        diffcount[0]   =0;
        for (int i=0; i<hh; ++i){/*each height*/                     
	    windex=0;    
        for (int j=0; j<ww; ++j){/*each width*/
        tmp2=hindex+windex;
        tmp1=hindex*step*step+windex*step;
        //printf("stuck: %d,%d,%d,%d,%d,%d,%d,%d\\n",tmp1,tmp2,mat[tmp1],mat[tmp1+1],mat[tmp1+2],mat2[tmp2],mat2[tmp2+1],mat2[tmp2+2]);
        if(  abs(mat[tmp1]-mat2[tmp2])>thres 
          && abs(mat[tmp1+1]-mat2[tmp2+1])>thres
        && abs(mat[tmp1+2]-mat2[tmp2+2])>thres
           ){

                     diffcount[0]+=1;
                    }
        windex+=3;
             }
         hindex+=hstep;        
         }         
        // printf("total diff:%d\\n",diffcount[0]);    
            '''
        #input:['mat', 'mat2', 'ww', 'hh','step' ]        downsample from mat to mat2
        self.codecopy = '''        
        int hindex=0,windex=0,hstep=3*ww,tmp1,tmp2;        
        //printf("%d,%d,%d,%d\\n",step,ww,hh,hstep);
        for (int i=0; i<hh; ++i){/*each height*/                     
	    windex=0;    
        for (int j=0; j<ww; ++j){/*each width*/
        tmp2=hindex+windex;
        tmp1=hindex*step*step+windex*step;
        //printf("copy: %d,%d,%d,%d,%d,%d,%d,%d\\n",tmp1,tmp2,mat[tmp1],mat[tmp1+1],mat[tmp1+2],mat2[tmp2],mat2[tmp2+1],mat2[tmp2+2]);
           mat2[tmp2]=mat[tmp1];
           mat2[tmp2+1]=mat[tmp1+1];
           mat2[tmp2+2]=mat[tmp1+2];
        windex+=3;
             }
         hindex+=hstep;        
         }         
            '''
            
