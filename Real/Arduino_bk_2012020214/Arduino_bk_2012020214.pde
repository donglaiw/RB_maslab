#include <Servo.h>
#include <CompactQik2s9v1.h>
#include <NewSoftSerial.h>

#define rxPin 19
#define txPin 18
#define rstPin 5
#define servoChar 'S'
#define analogChar 'A'
#define motorChar 'M'
#define digitalChar 'D'
#define commandLen 6
/*
//IR:
Short Range: 4: front; 5:left;  6:right;
(sharp)Long Range: 7:front
*/
#define F_IR 4
#define L_IR 5
#define R_IR 6
#define S_IR 7
#define L_BP 24
#define R_BP 30
#define F_BP 26


#define Left_IR 3

Servo servo;
NewSoftSerial mySerial = NewSoftSerial(rxPin, txPin);
CompactQik2s9v1 motor = CompactQik2s9v1(&mySerial, rstPin);

int IR[4][2]= {{0,0},{0,0},{0,0},{0,0}}; //0:old val, 1: new val
int prestate=-1,state=-1;
int fb=0,fb_c=0,fb_thres=5;//front bolck
int fb_begin=0, fb_c_begin=0;
int lb=0, lb_c=0,lb_thres=5;//left block
int rd=0,rd_c=0,rd_thres=5;//rightwall disappear
int md=0,md_c=0;//middle of nowhere
int diff_thres=50; //simple filter out ir outlier

char Gstate=' ';
int ccc=0;


void setup() {
    Serial.begin(9600);           // set up Serial library at 9600 bps
    delay(1000); //Wait for it to initialize
    Serial.flush();

    mySerial.begin(9600);
    motor.begin();
    motor.stopBothMotors();
    
     }


void loop() {
  switch(Gstate) {
        case 'N':
            //Navigation,persistent state
            Navigation();
            break;
        case 'C':
            //Backward
            setMotor(-120,-120);
            delay(300);
            Gstate=' ';
            break;
        case 'L':
            //Try to align the wall lost from left 
            goTurn90(-1);
            setMotor(100,120);
            delay(1300);
            setMotor(0,0);
            Gstate=' ';
            Serial.println("d");            
            break;
        case 'S':
            //Stop it
            setMotor(0,0);
            Gstate=' ';
            break;
        case 'T':
            //Turn a small angle left

            LeftBlock();

            if(lb==1)
           //if (val_IR_l>350)
            {
              TurnBackward();
            }
            else
            {
            //Tune a smaller angle left
            goTurn(-1);
            }
            Gstate=' ';
            Serial.println("d");            

          break;
        case 't':
			//Turn a small angle right
            goTurn(1);
            Gstate=' ';            
         Serial.println("d");            
            break;
        case 'U':
			//Tune a smaller angle left
            goTurn2(-1);
                        Gstate=' ';  
                                 Serial.println("d");            
            break;
        case 'u':
			//Tune a smaller angle right
            goTurn2(1);
                        Gstate=' ';  
                                 Serial.println("d");            
            break;
        case 'G':
            setMotor(120,120);//Go straight a little bit
            delay(300);
            Gstate=' ';  
            break;
        case 'A':
			//Align Wall for throw ball
            AlignWall();
             Serial.println("d");            
              delay(10);
              Gstate=' ';  
            break;
        case 'B':
	//Throw Ball
            DumpBall();
            Serial.println("d");            
            delay(10);
            Gstate=' ';  
            break;
        case 'W':
        //Get Switch
            getSwitch();
            break;
        case 'K':
		//Get Out of Stuck
          getOutStuck();
         Serial.println("d");            
         delay(10);
            Gstate=' ';  
            break;
        case 'O':
          analogWrite(9,0);
          break;    
        case 'o':
          analogWrite(9,255);
          break;
           }

    if(Serial.available()){
     Gstate= (char)Serial.read();
    }
}

int AlignWall(){
  int val_l=analogRead(F_IR);
  int val_r=analogRead(S_IR);
  while ((val_l<300) && (val_r<300)){
    setMotor(120,120);
    val_l=analogRead(F_IR);
    val_r=analogRead(S_IR);
  }
  setMotor(0,0);
  delay(100);
  int aligned=0;
  
  while (aligned==0){
    val_l=analogRead(F_IR);
    val_r=analogRead(S_IR);

  if (abs((val_l-val_r))>20){
    if ((val_l-val_r)>0){
      setMotor(-100,100);
    }else {
      setMotor(100,-100);
    }
    }else{
    setMotor(0,0);
    aligned=1;
  }
  }
  delay(100);
  setMotor(120,120);
  delay(1000);
  setMotor(0,0);
  
  return aligned;
}


void Navigation()
{
     FrontBlock();
     FrontBlock_begin();
     RightDisappear();
     LeftBlock();

     if(rd==2)//In the middle of nowhere
     {
       //Serial.print(rd);
       if(lb==1)
       {
         //Serial.print(lb);
         TurnBackward();
       }
       else if(fb==1 || fb_begin==1)
       {
         //Turn Left
         goTurn60(-1);
       }
       else
       {
       //GoStraight()
         setMotor(120,120);
      // setMotor(0,0);
       }

     }
     else if(rd==1)//Right Wall Disappear
     {
         goUturn();
     }
     else if(fb==1)
     {
         goTurn60(-1);
     }
     else
     {
         FollowRightWall();
     }


}





void goUturn()
{
    while(rd==1)
    {
        setMotor(100,100);
        RightDisappear();
    }
    goTurn90(1);
    setMotor(100,80);
    delay(350);
    RightDisappear();
    
    if(rd!=0)
    {
        goTurn90(1);
    }
  
  //forward left
  //setMotor(80,100);
  //delay(100);
  
  
  //setMotor(100,40);
  //delay(500);
  
 // setMotor(0,0);
 // delay(2000);
  
  
  //turn 90 right
  //goTurn90(1); 
  
 // setMotor(120,80);
  //delay(100);
  //setMotor(120,80);
  //delay(200);
  //RightDisappear();
/*
  if (rd==1)
  {
    //still missing...
    goTurn90(1);
    setMotor(120,100);
    RightDisappear();
    FrontBlock();
   while(rd==1 && fb==0)
   {
      RightDisappear();
      FrontBlock();
   }
 }
*/
}
//Rule 3
//rd=0--->Right Wall Appear
//rd=1--->Right Wall Disappear
//rd=2--->In the middle of nowhere
void RightDisappear() 
{
    int val_front=analogRead(R_IR);
    int val_rear=analogRead(L_IR);
    
    if(val_front<150) 
    {
        rd_c+=1;
        
        if(val_rear<150)
        {
            md_c+=1;
        }


        
        if(rd_c>rd_thres+1) 
        {
            if(md_c>=rd_thres)
            {
                rd_c=0;
                md_c=0;
                rd=2;
            }
            else
            {
                md_c=0;
                rd_c=0;
                rd=1;
            }
        }
    }
    else 
    {
        rd=0;
        rd_c=0;
        md_c=0;
    }
}
//Rule 2
void FrontBlock() {
    int val2=analogRead(F_IR);
    int val3=analogRead(S_IR);
    //if(val2 > 500||(val3>500)) {
      if(val2>425){
        fb_c+=1;
        if(fb_c>fb_thres) {
            fb_c=0;
            fb=1;
            }
        }
    else {
        fb=0;
        fb_c=0;
        }
    }


void FrontBlock_begin() 
{
    int val2=analogRead(F_IR);
    int val3=analogRead(S_IR);
    //if(val2 > 500||(val3>500)) {
      if(val2>425 || val3>500)
      {
        fb_c_begin+=1;
        if(fb_c_begin>fb_thres) 
        {
            fb_c_begin=0;
            fb_begin=1;
        }
      }
    else {
        fb_begin=0;
        fb_c_begin=0;
        }
    }


//Rule 1
void FollowRightWall() {
    int val=analogRead(R_IR);
    int val3=analogRead(S_IR);
    
    if(val3>425)
    {
        state=-1;
    }
    
    //right wall disappear
        //400-500 is ideal
    else if(val >500) {
            // if we are way too close, turn away fast
            state=0;
            }
        else if(val >450) {
            // if we are too close, drift away
            state=1;
            }
        else if(val < 250) {
            // too far away, turn towards wall and go straight
            state=2;
            }
        else if(val<350) {
            // default, drift towards wall
            state=3;
            }

    if (state!=prestate) {
        prestate=state;
        switch (state) {
            case -1:
                setMotor(0,120);
                break;
            case 0:
                setMotor(80,120);
                break;
            case 1:
                setMotor(100,120);
                break;
            case 2:
                setMotor(120,100);
                break;
            case 3:
                setMotor(120,80);
                break;
            }
        }
    }



void TurnBackward()
{
  goTurn90(1);
  goTurn90(1);
  goTurn60(-1);
  //setMotor(0,0);
  //delay(10000);
}


void LeftBlock()
{
  int val=analogRead(Left_IR);
  if(val>300)
  {
      Serial.print("val  ");
      Serial.print(val);
            Serial.print("      ");
      lb_c+=1;
            Serial.println(lb_c);
      if(lb_c>lb_thres)
      {
          lb_c=0;
          lb=1;
      }
  }
  else
  {
      lb=0;
      lb_c=0;
  }

}
void DumpBall() {
    //don't want it on all time...
    servo.attach(7);
    servo.write(160);
    delay(2000);
    servo.write(60);
    delay(200);
    servo.detach();
    }

void getOutStuck(){
  setMotor(-120,-120);
  delay(600);
    int val_rf=analogRead(R_IR);
    int val_lf=analogRead(Left_IR);
    if(val_rf>val_lf){
goTurn90(-1);
}else{
goTurn90(1);

}

  
}

void setMotor(int sp0,int sp1) {
    if (sp0>0) {
        motor.motor0Forward(sp0);
        }
    else {
        motor.motor0Reverse(-sp0);
        }
    if (sp1>0) {
        motor.motor1Forward(sp1);
        }
    else {
        motor.motor1Reverse(-sp1);
        }
    }

void goTurn90(int dir) {
    setMotor(100*dir,-100*dir);
    delay(650);
    setMotor(0,0);
    }

void goTurn60(int dir) {
    setMotor(100*dir,-80*dir);
    delay(300);
    }

//1: turn right
void goTurn(int dir) {
    setMotor(120*dir,-120*dir);
    delay(200);
    setMotor(0,0);
    delay(300);    
}

void goTurn2(int dir) {
    setMotor(100*dir,-100*dir);
    delay(90);
    setMotor(100,100);
    delay(600);
    }

void goStraight(int speed) {
    if(speed<=127) {
        motor.motor0Forward(speed);
        motor.motor1Forward(speed);
        }
    else {
        }
    motor.motor0Reverse(speed-128);
    motor.motor1Reverse(speed-128);
    }




//---------------
void getAnalog() {
    int port = 1;//getData(2);
    int analogData = analogRead(port);
    Serial.println(analogData);
    delay(10);
    }
//---------------
void getDigital() {
    int port = 1;//getData(2);
    int digitalData = digitalRead(port);
    Serial.println(digitalData);
    delay(10);
    }

void getSwitch() {
    int digitalData = digitalRead(22);
    Serial.println(digitalData);
    delay(100);
    }

