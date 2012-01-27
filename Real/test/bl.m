
img=imread('/home/donglai/Desktop/MASlab2012/test/img/1.jpg','JPEG');
mat=imread('/home/donglai/Desktop/MASlab2012/test/1ha.jpg','JPEG')';

[rr,cc]=ind2sub(size(mat),find(mat==1))
img2=rgb2hsv(img);
img2(:,:,1)=img2(:,:,1)*180;
img2(:,:,2)=img2(:,:,2)*255;
img2(:,:,3)=img2(:,:,3)*255;
img2
img2(437,153:154,:)



find (img2(437,:,1)==9)
img2(437,605:608,:)


find (img(437,:,3)==158)


img(437,[38,425,440],:)

thres=[0,100,100,10,250,255,150,100,100,179,250,255]./repmat([180,255,255],1,4)


clear

mat=imread('/home/donglai/Desktop/maslab/test/1ha.jpg','JPEG')';
mat(mat>0)=1;
%mat=mat(40:90,160:230);


%{
mat=ones(10);
mat(logical(eye(size(mat))))=0;
mat(10,10)=1;
%}

[aa,bb]=bwlabel(mat,4);
[cc,dd]=histc(aa(:),1:bb);
[ww,hh]=size(mat);
label=zeros(ww,hh);
count=zeros(1,1000);
lcount=zeros(1,1000);
tlabel=zeros(1,1000);
thres=20   

    hindex=0,ntable=0;
  ttt=0;
    for i = 0:hh-1
        for  j = 0: ww-1
            if (mat(hindex+j+1)==1)                 
                if ( j == 0 ) 
                    B = 0; 
                else                
                    B = label(hindex+j);
                    %[i,j,B]
            while  B~=0 &&tlabel(B)~=B
                    B=tlabel(B);
            end
                end

                if ( i == 0 ) 
                    C = 0; 
                else 
                    C = label(hindex+j-ww+1);
            while C~=0 && tlabel(C)~=C
                    C=tlabel(C);
            end
                end                                                         
                
				if ( B~=0 && C~=0 )                    
                    label(hindex+j+1) = B;
                    count(B) = count(B)+1;         
                    if B~=C
                    tlabel(C) = B;                
                    end
                    if C==34 && B==37
                     [C,B,tlabel(C),tlabel(B)]
                     end
                elseif ( B~=0 )             
                    label(hindex+j+1) = B;
                    count(B) = count(B)+1;
                elseif ( C~=0 )             
                    label(hindex+j+1) = C;
                    count(C) = count(C)+1;
                else 
                    ntable=ntable+1;
                    tlabel( ntable ) = ntable;
                    label(hindex+j+1)  =  ntable;
                    count(ntable)    = 1;                    
                end                 
                %{               %}
             end            
        end        
        hindex=hindex+ww; 
     end
    
%{
    for i = 1:ntable
        if (count(i)>0 && tlabel(i)~=i)       
            i0=i ;
            while  tlabel(i0)~=i0
                    i0=tlabel(i0);
                    count(i)=count(i)+count(i0);
                    count(i0)=0;
                    label(label(:)==i0)=i;
            end
            label(label(:)==i)=i0;
            count(i0)=count(i0)+count(i);
            count(i)=0;
         end
         if sum(count)~=1692
         [sum(count),i]
         break
         end
     end
                
  %}          
        
                                                                                                             
    %{%}
