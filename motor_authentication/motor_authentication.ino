// Adafruit Motor shield library
// copyright Adafruit Industries LLC, 2009
// this code is public domain, enjoy!

#include <AFMotor.h>


// DC motor on M1
AF_DCMotor motor(1);
String data;
// DC hobby servo// Stepper motor on M3+M4 48 steps per revolution

void setup() {
  Serial.begin(115200);
  // set up Serial library at 9600 bps
  
}


// Test the DC motor, stepper and servo ALL AT ONCE!
int x;
int state;
void loop() {
  if(state==1){
      motor.run(FORWARD);
      motor.setSpeed(200);  
      delay(3);
    }else{
      motor.run(FORWARD);
      motor.setSpeed(0);  
      delay(3);
    }
  while (Serial.available()){
    x = Serial.readString().toInt();
    Serial.print(x);
    state=x;
  }
}
