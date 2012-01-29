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

Servo servo;
NewSoftSerial mySerial = NewSoftSerial(rxPin, txPin);
CompactQik2s9v1 motor = CompactQik2s9v1(&mySerial, rstPin);

int IR[4][2]={{0,0},{0,0},{0,0},{0,0}}; //0:old val, 1: new val
/*
//Bumper 
26:front;24:left;30:right
*/

int prestate=-1,state=-1;
int fb=0,fb_c=0,fb_thres=5;
int diff_thres=50; //simple filter out ir outlier
void setup() {
    Serial.begin(9600);           // set up Serial library at 9600 bps
    delay(1000); //Wait for it to initialize
    Serial.flush();

    mySerial.begin(9600);
    motor.begin();
    motor.stopBothMotors();
    
    //goTurn90();    
    //goStraight(100);
}


void loop() {
  
/* 
 int val=getIr(F_IR);
 Serial.print("short:");
 Serial.println(val);
*/
 int val=getIr(S_IR);
 Serial.print("long:");
 Serial.println(val);
 
/**/

  //1. Check Front Block
      FrontBlock();
  //2. follow straight wall on the right with right IR
      if(fb==1){
        goTurn90(-1);
        delay(100);
      }else{        
        FollowRightWall();
      }      
      
 /*     */
  
      //    FollowRightWall();
    }

void FindWall(){
  int a=1;
}

void FrontBlock(){
    int val=getIr(F_IR);    
    if(val > 400){
      fb_c+=1;
      if(fb_c>fb_thres){        
       fb_c=0;
       fb=1;
      }      
      }else{
      fb=0;
      fb_c=0;
      }
 //Serial.println(val+" "+fb);      
}
void FollowRightWall(){
     int val=getIr(R_IR);
     int val2=getIr(S_IR);
     if(val2>550){
     //right front corner near
          state=-1;  
     }else{
       
    //400-500 is ideal
        if(val >600){
    // if we are way too close, turn away fast
          state=0;  
        }else if(val >500){
    // if we are too close, drift away
            state=1;  
        }else if(val < 200){
    // too far away, turn towards wall and go straight
            state=2;
        }else if(val<400){
    // default, drift towards wall
            state=3;
        }
     }
     
    if (state!=prestate){
        prestate=state;        
        switch (state){
        case -1:
        setMotor(0,120);
        break;
        case 0:
        setMotor(30,120);
        break;
        case 1:
        setMotor(100,120);
        break;
        case 2:
        setMotor(120,80);
        break;
        case 3:
        setMotor(120,100);
        break;
        }
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

void goTurn90(int dir){
    setMotor(100*dir,-100*dir);
    delay(800);
    setMotor(0,0);
}

//1: turn right
void goTurn(int dir){
    setMotor(100*dir,-100*dir);
    delay(300);
    setMotor(0,0);
}

void goStraight(int speed) {
    if(speed<=127){
    motor.motor0Forward(speed);
    motor.motor1Forward(speed);
    }else{
    }
    motor.motor0Reverse(speed-128);
    motor.motor1Reverse(speed-128);
    }



int getIr(int port) {
  int tmp=analogRead(port);
  //IR<200 may be degenerate
  //for IR>200, we want the change to be smooth
//  if (IR[port-4][1]<200 ||abs(tmp-IR[port-4][1])<diff_thres)
//    {
      IR[port-4][0]=IR[port-4][1];
      IR[port-4][1]=tmp;
//    }
   return IR[port-4][1];
    }

//----------
void moveServo() {
    int port = getData(2);
    int angle = getData(3);
    servo.attach(port);
    servo.write(angle);
    Serial.println("000000");
    delay(10);
    //servo.detach();
    }
//----------------
void moveMotor() {
    int num = getData(1);
    int val = getData(3);
    //0-127  :forward
    //128-255 :backward
    if (val<=127) {
        if (num==0) {
            motor.motor0Forward(val);
            }
        else if (num==1) {
            motor.motor1Forward(val);
            }
        }
    else {
        if (num==0) {
            motor.motor0Reverse(val-128);
            }
        else if (num==1) {
            motor.motor1Reverse(val-128);
            }
        }

    delay(100);
    }
//---------------
void getAnalog() {
    int port = getData(2);
    int analogData = analogRead(port);
    Serial.println(analogData);
    delay(10);
    }
//---------------
void getDigital() {
    int port = getData(2);
    int digitalData = digitalRead(port);
    Serial.println(digitalData);
    delay(10);
    }
//----------------
int getData(int len)
//Collects data of the appropriate length and turns it into an integer
    {
    char buffer[len+1];
    int received = 0, returnInt;

    for (int i = 0; i<len; i++) {
        buffer[received++] = Serial.read();
        buffer[received] = '\0';
        if (received >= (sizeof(buffer)-1)) {
            returnInt = atoi(buffer);
            received = 0;
            }
        }

    return returnInt;
    }
