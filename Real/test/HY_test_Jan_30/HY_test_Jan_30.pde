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


Servo servo;
NewSoftSerial mySerial = NewSoftSerial(rxPin, txPin);
CompactQik2s9v1 motor = CompactQik2s9v1(&mySerial, rstPin);

int IR[4][2]= {{0,0},{0,0},{0,0},{0,0}}; //0:old val, 1: new val
int prestate=-1,state=-1;
int fb=0,fb_c=0,fb_thres=10;
int rd=0,rd_c=0,rd_thres=5;
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
  //setMotor(100,100);
  
  if (ccc==0){
  AlignWall();
  ccc=1;
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
void serialEvent() {
    // get the new byte:
/*
    Gstate= (char)Serial.read();
     Serial.println("ppp");    
     Serial.println(Gstate);

     Serial.println("ahaha");
*/  
  }

void Navigation(){
     FrontBlock();
     RightDisappear();
	if (fb==1){
        if(rd==1){
      //go into the new era
    goUturn();
      }else{
	goTurn60(-1);
	}
    }else{
        if(rd==1){
       //go into the new era
		goUturn();
	}else{
   	FollowRightWall();
        }
   }
}
void goUturn(){
//forward left
setMotor(100,120);
delay(400);
//turn 90 right
goTurn90(1);
setMotor(120,100);
delay(500);
RightDisappear();
if (rd==1){
//still missing...
goTurn90(1);
setMotor(120,100);
RightDisappear();
FrontBlock();
while(rd==1 && fb==0){
RightDisappear();
FrontBlock();
}
}

}
//Rule 3
void RightDisappear() {
    int val=getIr(R_IR);
    if(val<100) {
        rd_c+=1;
        if(rd_c>rd_thres) {
            rd_c=0;
            rd=1;
            }
        }
    else {
        rd=0;
        rd_c=0;
        }
    }
//Rule 2
void FrontBlock() {
    int val2=getIr(F_IR);
    int val3=getIr(S_IR);
    if(val2 > 500||(val3>500)) {
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

//Rule 1
void FollowRightWall() {
    int val=getIr(R_IR);
    //right wall disappear
        //400-500 is ideal
        if(val >550) {
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

void DumpBall() {
    //don't want it on all time...
    servo.attach(7);
    servo.write(160);
    delay(2000);
    servo.write(60);
    delay(10);
    servo.detach();
    }

/*
void AlignWall() {
    int stuck=0;
    setMotor(120,120);
    int val_l=1;
    int val_r=1;
    while(stuck==0) {
        val_l=digitalRead(26);
        val_r=digitalRead(30);

        if (val_l==0) {
            stuck=1;
            Serial.print("left");
            Serial.println(val_l);
            }
        else if (val_r==0) {

            Serial.print("right");
            Serial.println(val_r);
            stuck=1;
            }

        }

    setMotor(0,0);
    if (val_l==0) {
        setMotor(-120,-120);
        delay(200);
        setMotor(-50,120);
        delay(800);
        setMotor(0,0);
        }
    else {
        setMotor(-120,-120);
        delay(200);
        setMotor(120,-50);
        delay(800);
        setMotor(0,0);
        }
      setMotor(120,120);

      delay(2000);

    }

*/
void getOutStuck(){
  setMotor(-100,-100);
  delay(400);
  goTurn90(1);
  
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
    delay(800);
    setMotor(0,0);
    }

void goTurn60(int dir) {
    setMotor(100*dir,-100*dir);
    delay(300);
    }

//1: turn right
void goTurn(int dir) {
    setMotor(100*dir,-100*dir);
    delay(300);
    setMotor(0,0);
    }

void goTurn2(int dir) {
    setMotor(100*dir,-100*dir);
    delay(100);
    setMotor(0,0);
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

