#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "math.h"

using namespace std;

//DIGITAL PINS USABLE FOR INTERRUPTS
//Mega, Mega2560, MegaADK:           2, 3, 18, 19, 20, 21
//Micro, Leonardo, other 32u4-based: 0, 1, 2, 3, 7

// Pin assignments
const int LASER_640 = 2;
const int LASER_561 = 17;
const int LASER_488 = 5;
const int LASER_405 = 12;
const int DETECTOR = 3;

//const int LASER_640_INTERRUPT = 18;
//const int LASER_561_INTERRUPT = 19;
//const int LASER_488_INTERRUPT = 20;
//const int LASER_405_INTERRUPT = 21;

int LASERS[] = {LASER_640, LASER_561, LASER_488, LASER_405};
long int exposure_405;
long int exposure_488;
long int exposure_561;
long int exposure_640;

// Serial communication variables
int N = 0;
String input = "";
String numbers[12];
String temp = "";

void setup() {
  Serial.begin(115200); // use the same baud-rate as the python side
  // put your setup code here, to run once:
  pinMode(LASER_640, OUTPUT);
  pinMode(LASER_561, OUTPUT);
  pinMode(LASER_488, OUTPUT);
  pinMode(LASER_405, OUTPUT);
  pinMode(DETECTOR, OUTPUT);

  digitalWrite(LASER_640, LOW);
  digitalWrite(LASER_561, LOW);
  digitalWrite(LASER_488, LOW);
  digitalWrite(LASER_405, LOW);
  digitalWrite(DETECTOR, LOW);

}


//*****************************************************************************************************
unsigned long stringToInt(String num) {
  int len;
  unsigned long dec = 0;
  len = num.length();
  for (int i = 0; i < len; i++) {
    dec = dec * 10 + ( num[i] - '0' );
  }
  return dec;
}


void TakeImage(){
  long int exposures[] = {exposure_640, exposure_561, exposure_488, exposure_405};
  for (int index = 0; index <4; index++){
    if (exposures[index]!= 0){
      digitalWrite(LASERS[index], HIGH);
      digitalWrite(DETECTOR, HIGH);
      delay(exposures[index]);
      digitalWrite(LASERS[index], LOW);
      digitalWrite(DETECTOR, LOW);
      delay(1000);
    }
  }
}

//*****************************************************************************************************

// reading serial from the PC
void loop() {
  while (Serial.available()) {
    delay(2);
    if (Serial.available() > 0) {
      char c = Serial.read();
      input += c;
    }
  }
  if (input.length() > 0 && input[0] == 'E') {
    N = 0;
    // print incoming serial comm
    // Serial.print("Received ");
    // Serial.println(input);

    // go through each character
    for (int ii = 2; ii <= input.length(); ++ii) {
      // if the char is a digit, append it to an array
      if (isdigit(input[ii]) ) {
        temp += input[ii];
      }

      //this 0 is not an integer, is null string
      else if (input[ii] == ' ' || input[ii] == 0) {
        numbers[N] = temp;
        temp = "";
        if (input[ii] == ' ') N++;
      }
    }
    N++;

    exposure_405 = stringToInt(numbers[3]);
    exposure_488 = stringToInt(numbers[2]);
    exposure_561 = stringToInt(numbers[1]);
    exposure_640 = stringToInt(numbers[0]);
    for (int jj = 0; jj < N; jj++)
      numbers[jj] = "";

    Serial.print("Recieved: ");
    Serial.println(input);

    if (input[1] == 'S'){
      Serial.println('s');
      TakeImage();}
    if (input[1] == 'L'){
      while (!Serial.available()){
        TakeImage();
      }
      }
    }


  input = "";
  Serial.flush();
}
