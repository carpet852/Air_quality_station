/*
 Interface to Sharp GP2Y1010AU0F Particle Sensor
 Modified from Program by Christopher Nafis 
 Written April 2012

 Changes (Sept 2016):
 LCD Display
 ISR code for ADC

 SCA 2020-08-02
 adapted for Arduino Micro
 removed LCD code
 added Serial1 output

 http://www.howmuchsnow.com/arduino/airquality/
 https://web.archive.org/web/20161115025001/http://connectranet.co.uk/wp/2016/09/21/using-the-sharp-dust-sensor-with-arduino-getting-the-timing-right/
 
 */
#include <stdlib.h>

const byte adcMux = 0x07; // A0=ADC7, ADMUX register, cf ATmega32U4 datasheet
// Variables that can be changed by an ISR must be declared as volatile
volatile int adcReading;
volatile boolean adcDone;
boolean adcStarted;

int dustPin=0;  // A0 ADC input
int ledPower=9; // D9 PWM 16bit
int dataInterval=500;  // update interval in multiple of 10ms cycle time
int delayTime=280;  // data sampling delay in us
int delayTime2=40;  // pulse off delay in us
float offTime=9580;   // pulse off time in us (int is 16bit only)
int i=0;
int c=0;
int adcMin=1023;
int adcMax=0;
float adcSum=0;
char s[32];
float voltage = 0.0;
float vMin = 0.0;
float vMax = 0.0;
float dustdensity = 0.0;
float ppmperccm = 0.0;

void setup(){
   Serial.begin(9600);  // Serial is the USB CDC serial connection
   Serial1.begin(9600); // Serial1 are uart pins 0(RX),1(TX) on the Micro
   pinMode(ledPower,OUTPUT);
   delay(1000);
   i=0;
   c=0;
   adcSum=0;
   // set the ADC reference input AREF=AVCC (high two bits of ADMUX)
   // select the channel (low 4 bits). this also sets ADLAR (left-adjust result) to 0 (the default).
   ADMUX = bit (REFS0) | (adcMux);
}

// ADC conversion complete Interrupt Service Routine
ISR (ADC_vect){
   byte low, high;
   // read the result registers and store value in adcReading
   // Must read ADCL first
   low = ADCL;
   high = ADCH;
   adcReading = (high << 8) | low;
   adcDone = true; 
} 
// end of ADC_vect
 
void loop(){
   do { 
     i=i+1;
     digitalWrite(ledPower,LOW); // power on the LED
     delayMicroseconds(delayTime); // wait 280us
     // Check the conversion hasn't been started already
     if (!adcStarted)
     {
     adcStarted = true;
     // start the conversion
     ADCSRA |= bit (ADSC) | bit (ADIE);
     } 
     delayMicroseconds(delayTime2); // wait another 40us or so to give 320us pulse width
     digitalWrite(ledPower,HIGH); // turn the LED off
     // give the ADC time to complete then process the reading
     delayMicroseconds(100); 
     if (adcDone) 
     // adcDone is set to True by the ISR, called when the conversion is complete.
     {
       adcStarted = false;
       if (adcMin > adcReading) adcMin = adcReading;
       if (adcMax < adcReading) adcMax = adcReading;
       adcSum = adcSum + adcReading;
       c = c+1; // count of readings
       adcDone = false;
     }  
     delayMicroseconds(offTime); // wait for the remainder of the 10ms cycle time
   } while (i <dataInterval);
   voltage = adcSum / c * 5.0 / 1024;
   vMin = adcMin * 5.0 / 1024;
   vMax = adcMax * 5.0 / 1024;
   ppmperccm = (voltage-0.0256)*120*3.5314667; // particle per cubic-cm, calibration done with Dylos Air quality monitor
   if (ppmperccm < 0)
      ppmperccm = 0;
   String dataString = "vAvg:";
   dataString += dtostrf(voltage, 9, 4, s);
   dataString += ", vMin:";
   dataString += dtostrf(vMin, 9, 4, s);
   dataString += ", vMax:";
   dataString += dtostrf(vMax, 9, 4, s);
   dataString += ", pm per cm^3:";
   dataString += dtostrf(ppmperccm, 8, 2, s);
   Serial.println(dataString);
   //Serial.println(ppmperccm, 2);  // print as ASCII text with 2 decimals
   Serial1.println(ppmperccm, 2); // print as ASCII text with 2 decimals
   i=0;
   c=0;
   adcMin=1023;
   adcMax=0;
   adcSum=0;
}
