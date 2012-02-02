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



Servo servo;
NewSoftSerial mySerial = NewSoftSerial(rxPin, txPin);
CompactQik2s9v1 motor = CompactQik2s9v1(&mySerial, rstPin);

void setup() {
    Serial.begin(9600);           // set up Serial library at 9600 bps
    delay(1000); //Wait for it to initialize
    Serial.flush();

    mySerial.begin(9600);
    motor.begin();
    motor.stopBothMotors();


    //gogogo
    //goStraight(100);
    //1. naive super straight?
    goStraight2(100);
    }

void loop() {

    /*
      //2. follow straight wall on the right with right IR
      //200-300 is ideal

       int val = getIr(26);
       println("IR:"+val);
        if(val >500){
            // if we are way too close, turn away fast
            setMotor(50,120);
        }else if(val >400){
            // if we are too close, drift away
            setMotor(60,80);
        }else if(val < 100){
            // too far away, turn towards wall more
            setMotor(120,50);
        }else if(val<200){
            // default, drift towards wall
            setMotor(80,60);
        }
	delay(100)
     */
    }

void setMotor(int sp0,int sp1) {
    if (sp0>0) {
        motor.motor0Forward(sp0);
        }
    else {
        motor.motor0Reverse(sp0);
        }
    if (sp1>0) {
        motor.motor1Forward(sp1);
        }
    else {
        motor.motor1Reverse(sp1);
        }
    }
void goStraight2(int speed) {
    motor.motor1Forward(speed);
    motor.motor0Forward(speed);
    }
void goStraight(int speed) {
    motor.motor0Forward(speed/2);
    delay(100);
    motor.motor1Forward(speed);
    delay(200);
    motor.motor0Forward(speed);
    }

int getIr(int port) {
    return analogRead(port);
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
