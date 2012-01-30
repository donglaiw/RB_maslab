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
int fb=0,fb_c=0,fb_thres=5;
int diff_thres=50; //simple filter out ir outlier

char Gstate=0;


void setup() {
    Serial.begin(9600);           // set up Serial library at 9600 bps
    delay(1000); //Wait for it to initialize
    Serial.flush();

    mySerial.begin(9600);
    motor.begin();
    motor.stopBothMotors();

    servo.attach(7);
    }

void serialEvent() {
    // get the new byte:
    Gstate= (char)Serial.read();
    }



void loop() {
    switch(Gstate) {
        case 'N':
            //Navigation
            FollowRightWall();
            break;
        case 'T':
            //Turn a small angle left
            goTurn(-1);
            break;
        case 't':
			//Turn a small angle right
            goTurn(1);
            break;
        case 'U':
			//Tune a smaller angle left
            goTurn2(-1);
            break;
        case 'u':
			//Tune a smaller angle right
            goTurn2(1);
            break;
        case 'G':
			//Go straight until stuck
            break;
        case 'A':
			//Align Wall for throw ball
            AlignWall();
            break;
        case 'B':
			//Throw Ball
            DumpBall();
            break;
        case 'W':
			//Get Switch
            break;
        case 'K':
			//Get Out of Stuck
            break;
        }
    /*
     int val=getIr(F_IR);
     Serial.print("short:");
     Serial.println(val);
    */


    /*
    int val=getIr(R_IR);
    Serial.print("long:");
    Serial.println(val);
    */

//int bp=digitalRead(26);
//Serial.println(bp);
    /**/

    //1. Check Front Block
//      FrontBlock();
    //2. follow straight wall on the right with right IR
//      if(fb==1){
//        goTurn90(-1);
//       delay(100);
//     }else{
//FollowRightWall();


    /*
    //test throw ball
    if( uu==0){
      AlignWall();
      setMotor(120,120);
      delay(2000);
      DumpBall();
    }

    */
    }
void DumpBall() {
    servo.write(160);
    delay(2000);
    servo.write(60);
    delay(10);
    }
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

    }

void FindWall() {
    int a=1;
    }

void FrontBlock() {
    int val=getIr(F_IR);
    if(val > 400) {
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
//Serial.println(val+" "+fb);
    }
void FollowRightWall() {
    int val=getIr(R_IR);
    int val2=getIr(F_IR);
    int val3=getIr(S_IR);

    //right wall disappear
    if (val<100) {
        state=-2;
        }
    else if((val2>300)||(val3>350)) {
        //left front corner near
        state=-1;
        }
    else {
        //400-500 is ideal
        if(val >600) {
            // if we are way too close, turn away fast
            state=0;
            }
        else if(val >500) {
            // if we are too close, drift away
            state=1;
            }
        else if(val < 300) {
            // too far away, turn towards wall and go straight
            state=2;
            }
        else if(val<400) {
            // default, drift towards wall
            state=3;
            }
        }

    if (state!=prestate) {
        prestate=state;
        switch (state) {
            case -2:
                //setMotor(120,120);
                //delay(500);
                setMotor(120,30);
                //delay(500);
                break;
            case -1:
                setMotor(-120,120);
                break;
            case 0:
                setMotor(60,120);
                break;
            case 1:
                setMotor(100,120);
                break;
            case 2:
                setMotor(120,60);
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

void goTurn90(int dir) {
    setMotor(100*dir,-100*dir);
    delay(800);
    setMotor(0,0);
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
