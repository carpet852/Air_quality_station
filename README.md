# Air Quality Station

## Objective
This is a DIY project to build a basic Air Quality station with 2 kind of sensors:  
- meteo: temperature/humidity/pressure  
- air pollution: PM2.5/PM10 detector + VOC sensor

Volatile Organic Compounds (VOC) and Particule Matter (PM) are 2 important categories of air pollutants.  
Several commercial products I looked at were on a subscription-based model, with the data on the cloud.  
I wanted a self-contained system running on a Raspberry Pi.  
The data is visualized on a webserver running on the RPi.  
This system has been running continuously for years at my home.  

## Sensors
1. Dust sensor: built with a Sharp GP2Y1010AU0F analog dust sensor and an arduino board.
   It is not a very accurate sensor so I discarded it.
2. PM sensor: after some research, I chose a Sensirion SPS30 laser PM sensor that is pretty accurate.
   This sensor has a UART interface so I used a Yocto-Serial board to connect to the RPi.
3. VOC sensor: I used a Yocto-VOC-V3 board 
4. Meteo: I used a Yocto Meteo board with temperature/humidity/pressure sensors.

## Mechanics
CAD design done in Fusion360, 3D files exported for 3D-printing.
1. GP2Y1010AU0F sensor box: built to integrate the Sharp sensor and an Arduino Micro board, connected to the RPi with a USB cable.
2. SPS30 sensor box: built to integrate the Sensirion laser sensor and the Yocto-Serial, connected to the RPi with a USB cable.
3. LED box: built to integrate 3 leds (green/yellow/red) that give a convenient inidcation of the pollution level. 

## Firmware
RPi model: RPi2 modelB with Raspbian9.
Webserver: Lighttpd
Web app: YoctoCloud PHP scripts from Yoctopuce. A better web app has been released by Yoctopuce since then.
https://github.com/yoctopuce/YoctoCloud
Python: need to install the YoctoLib python library
The Python script that controls the LEDs is running as a service.
Yoctopuce provides a Virtulahub interface to display the sensors status. Virtualhub is also used to configure the sensors.



