#!/usr/bin/python
# -*- coding: utf-8 -*-

# Documentation
# https://www.yoctopuce.com/EN/products/yocto-voc/doc/YVOCMK01.usermanual.html
# https://www.yoctopuce.com/EN/products/yocto-serial/doc/YSERIAL1.usermanual.html
# https://www.yoctopuce.com/EN/doc/reference/yoctolib-python-EN.html
# https://gpiozero.readthedocs.io/en/stable/
# https://nerdynat.com/programming/2019/run-python-on-your-raspberry-pi-as-background-service/
# https://www.raspberrypi.org/documentation/usage/gpio/
# https://docs.python.org/2.7/library/urllib2.html
# https://www.pythonforbeginners.com/python-on-the-web/how-to-use-urllib2-in-python
# https://zipcpu.com/dsp/2017/08/19/simple-filter.html


# Config -------------------------- 
voc_yellow_thld = 1500
voc_red_thld = 3000
dust_yellow_thld = 170
dust_red_thld = 300
pm_yellow_thld = 20
pm_red_thld = 40
pm_avg_coeff = 0.2
voc_led_beep_time = 1000
pm_led_beep_time = 200
# URL ---------------------------------------
virtualhub_url = 'http://127.0.0.1:4444/bySerial/'
pm25_path = '/api/genericSensor2/currentValue'
# -------------------------------------------


import os, sys
import urllib2

#from yocto_api import *
#from yocto_voc import *
from yoctopuce.yocto_api import *
from yoctopuce.yocto_voc import *
from yoctopuce.yocto_serialport import *
from gpiozero import LED

# add ../../Sources to the PYTHONPATH
#sys.path.append(os.path.join("..", "..", "Sources"))

errmsg = YRefParam()

# RPI GPIO number
green_led = LED(18)
yellow_led = LED(23)
red_led = LED(24)

# Setup the API to use the VirtualHub server (localhost)
#if YAPI.RegisterHub("usb", errmsg) != YAPI.SUCCESS:
if YAPI.RegisterHub("127.0.0.1", errmsg) != YAPI.SUCCESS:
    sys.exit("init error" + errmsg.value)

# retrieve any voc sensor and any PM (serialport) sensor
vocSensor = YVoc.FirstVoc()
serialPort = YSerialPort.FirstSerialPort()
if vocSensor is None:
    sys.exit('No VOC sensor connected')
if serialPort is None:
    sys.exit('No PM sensor connected')

sn_vocmod = vocSensor.get_module().get_serialNumber()
sn_serialmod = serialPort.get_module().get_serialNumber()

print("VOC sensor: " + sn_vocmod)
print("PM sensor: " + sn_serialmod)
#serialPort.set_serialMode("9600,8N1")  #gp2y1010au0f only
#serialPort.set_protocol("Line")    #gp2y1010au0f only
#serialPort.reset()

voc_val = 0
dust_val = 0
pm_val = 0
pm_avg_val = 0

pm25_url = virtualhub_url + sn_serialmod + pm25_path

try:
    while vocSensor.isOnline() or serialPort.isOnline():
        if vocSensor.isOnline():
            voc_val = vocSensor.get_currentValue()
            print("VOC :  " + "%2.1f" % voc_val + " ppm")
        if serialPort.isOnline():
            try:
                #dust_val = float(serialPort.readLine())
                #print("DUST :  " + "%2.1f" % dust_val + " pm/cm3")
                response = urllib2.urlopen(pm25_url)
                pm_val = float(response.read())
                pm_avg_val = pm_avg_val + pm_avg_coeff*(pm_val - pm_avg_val) # IIR averaging filter
                print("PM25 :  " + "%2.1f" % pm_val + " ug/m3")
                print("PM25 avg:  " + "%2.1f" % pm_avg_val + " ug/m3")
            except ValueError: 
                pass
        #if voc_val > voc_red_thld or dust_val > dust_red_thld:
        #elif voc_val > voc_yellow_thld or dust_val > dust_yellow_thld:
        
        # led pattern: long beep = voc, short beep = pm
        if voc_val > voc_red_thld:
            red_led.on()
            YAPI.Sleep(voc_led_beep_time)
        elif voc_val > voc_yellow_thld:
            yellow_led.on()
            YAPI.Sleep(voc_led_beep_time)
        else:
            green_led.on()
            YAPI.Sleep(voc_led_beep_time)
        green_led.off()
        yellow_led.off()
        red_led.off()
        YAPI.Sleep(voc_led_beep_time)
        if pm_avg_val > pm_red_thld:
            red_led.on()
            YAPI.Sleep(pm_led_beep_time)
        elif pm_avg_val > pm_yellow_thld:
            yellow_led.on()
            YAPI.Sleep(pm_led_beep_time)
        else:
            green_led.on()
            YAPI.Sleep(pm_led_beep_time)
        green_led.off()
        yellow_led.off()
        red_led.off()
        YAPI.Sleep(pm_led_beep_time)

except KeyboardInterrupt:
    print("Press Ctrl-C to terminate loop")

green_led.off()
yellow_led.off()
red_led.off()

YAPI.FreeAPI()
