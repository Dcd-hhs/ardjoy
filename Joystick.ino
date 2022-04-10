// https://github.com/Cleric-K/vJoySerialFeeder#include "ibus.h"

#define UPDATE_INTERVAL 10 // millisecond
#define BAUD_RATE 115200
#define ANALOG_REFERENCE DEFAULT
#define ANALOG_INPUTS_COUNT 5
byte analogPins[] = {A0, A1, A2, A6, A7};//, A6, A7}; #define DIGITAL_INPUTS_COUNT 0
byte digitalPins[] = {2, 3, 7, 8}; #define DIGITAL_BITMAPPED_INPUTS_COUNT 0
byte digitalBitmappedPins[] = {}; #define ROTARY_COUNT 2//byte rotaryValues[] = {valL, valR};#define NUM_CHANNELS ( (ANALOG_INPUTS_COUNT) + (DIGITAL_INPUTS_COUNT) + (15 + (DIGITAL_BITMAPPED_INPUTS_COUNT))/16 + ROTARY_COUNT)

// initialise the IBus classIBus ibus(NUM_CHANNELS);
IBus jbus(NUM_CHANNELS);
// Prepare for rotary encoder updates// The pins and their complements, interrupts on a nano ar on 2 and three// A-Channelint pinLA  = 3;int pinRA = 2;
// B-channelint pinLB = 8;int pinRB = 7;int pinLAstate = LOW;
int pinRAstate = LOW;
int pinLBstate = LOW;
int pinRBstate = LOW;
int valL = 0;int valR = 0;

void setup()
{
  analogReference(ANALOG_REFERENCE); // use the defined ADC reference voltage source  pinMode(pinLA, INPUT_PULLUP);
  pinMode(pinLB, INPUT_PULLUP);
  pinMode(pinRA, INPUT_PULLUP);
  pinMode(pinRB, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(pinLA), LRotate, CHANGE);
  attachInterrupt(digitalPinToInterrupt(pinRA), RRotate, CHANGE);
  Serial.begin(BAUD_RATE);           // setup serial  
}

void loop()
{	//	Serial.println("___"); // Serial.println(valL);
  int i, bm_ch = 0;
  unsigned long time = millis();

  ibus.begin(0x40); //start checksum, and begin comms
  // read analog pins - one per channel
  for(i=0; i < ANALOG_INPUTS_COUNT; i++)
    ibus.write(analogRead(analogPins[i]));

  // read digital pins - one per channel
  for(i=0; i < DIGITAL_INPUTS_COUNT; i++)
    ibus.write(digitalRead(digitalPins[i]) == HIGH ? 1023 : 0);

  // read digital bit-mapped pins - 16 pins go in one channel
  for(i=0; i < DIGITAL_BITMAPPED_INPUTS_COUNT; i++) {
  	int bit = i%16;
  	if(digitalRead(digitalBitmappedPins[i]) == HIGH)
  		bm_ch |= 1 << bit;

  	if(bit == 15 || i == DIGITAL_BITMAPPED_INPUTS_COUNT-1) {
  		// data for one channel ready
  		ibus.write(bm_ch);
  		bm_ch = 0;
  	}	
		
  }
    ibus.write(valL);
	ibus.write(valR);
  ibus.end(); // Write two byte checksum

  time = millis() - time; // time elapsed in reading the inputs
  if(time < UPDATE_INTERVAL)
    // sleep till it is time for the next update
    delay(UPDATE_INTERVAL  - time);
}
void LRotate(){	//Serial.println("Lrotate");
	pinLAstate = digitalRead(pinLA);
	pinLBstate = digitalRead(pinLB);
	if (pinLBstate == LOW) {
		if (pinLAstate == HIGH){
		valL +=8; //go up		if (valL>360)valL=0;
		}else{
		valL -=8;  //go down		if (valL <0)valL =360;
		}
	}else {//pinLBstate == HIGH)
		if (pinLAstate == LOW){
		valL +=8; //go up
		if (valL>360)valL=0;
		}else{
		valL -=8;  //go down
		if (valL <0)valL =360;
		}
	}
}void RRotate(){
	pinRAstate = digitalRead(pinRA);
	pinRBstate = digitalRead(pinRB);
	if (pinRBstate == LOW) {
		if (pinRAstate == HIGH){
		valR +=8; //go up
		if (valR>360)valR=0;
		}else{
		valR -=8;  //go down
		if (valR <0)valR =360;
		}
	}else {//pinLBstate == HIGH)
		if (pinRAstate == LOW){
		valR +=8; //go up
		if (valR>360)valR=0;
		}else{
		valR -=8;  //go down
		if (valR <0)valR =360;
		}
	}
}