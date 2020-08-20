#!/usr/bin/env python
import PCF8591_3 as ADC
import RPi.GPIO as GPIO
from gpiozero import PWMOutputDevice
from time import time, sleep
import math
import sys

def indicatorON():
    GPIO.output(19, GPIO.HIGH)
    # indicator light ON
    

def indicatorOFF():
    GPIO.output(19, GPIO.LOW)
    # indicator light OFF
    
def electrode():
    frequency = 45 #hertz (can be changed based on therapy plan)
    pulsewidth = 400 - 60 #microseconds (constant 60 adjustment) (can be changed based on therapy plan)
    period = 1 / frequency
    pwm = PWMOutputDevice(21, initial_value = (pulsewidth / (period * 1e6)), frequency = frequency) # pulse width modulation
    sleep(12)
    pwm.off() # electrodes OFF
    sleep(6)
'''Electrode stimulation occurs in periods of 12 seconds on, 6 seconds off during therapy - this pattern can be changed based on therapy plan.'''
    
def setup():
    ADC.setup(0x48)
    DO = 17
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(DO, GPIO.IN)
    GPIO.setup(18, GPIO.OUT)
    GPIO.setup(19, GPIO.OUT)
    indicatorON()
    # initializes a couple pins, indicator light is turned on

def vibratorON():
    GPIO.output(18, GPIO.HIGH)
    print("Vibrator ON")
    # vibration motor ON

def vibratorOFF():
    GPIO.output(18, GPIO.LOW)
    print("Vibrator OFF")
    # vibration motor OFF

'''Vibration strength as well as current through the electrode can be moderated using resistors.'''

def loop_EON():
    t1 = time() # loop start time
    print("________________________________________________________")
    print("Electromuscular Stimulation stage. Start time:", round(t1,2),)
    print("________________________________________________________")
    while True:
            analogVal = ADC.read(0)
            Vr = 5 * float(analogVal) / 255
            Rt = 10000 * Vr / (5 - Vr)
            temp = 1/(((math.log(Rt / 10000)) / 3950) + (1 / (273.15 + 25)))
            temp = temp - 273.15 # temperature conversion
            print('Temperature: ', round(temp,2), 'C') # temperature display from thermistor sample code
            if temp >= 45:
                            check = 0
                            counter = 0
                            tmp = 0

                            while check in range(10):
                                    if temp > 45:
                                            counter += 1
                                            
                            if counter >= 8:
                                print("Dangerous temperatures detected, turning off.")
                                sys.exit()
                                '''Counter: if we see that a value is greater than or equal to 45 degrees, we run a check:
                                if 8 of the last 10 checks equal or exceed 45 degrees, program is exited.'''
                                    
            electrode() # electrodes ON
            t2 = time() # current time
            dt = t2 - t1 # elapsed time
            if dt > 120:
                print("Electrodes OFF @", round(t2, 2), "\n elapsed time:", round(dt,2))
                break
            # electrode therapy occurs over two minutes
    loop_EOFF_VON()
    # after the electrotherapy period is completed, we move to the vibration stage

def loop_EOFF_VON():
    t1 = time()
    print("________________________________________________________")
    print("--Mechanical vibration stage. Start time:", round(t1, 2), "--")
    
    while True:
            analogVal = ADC.read(0)
            Vr = 5 * float(analogVal) / 255
            Rt = 10000 * Vr / (5 - Vr)
            temp = 1/(((math.log(Rt / 10000)) / 3950) + (1 / (273.15 + 25)))
            temp = temp - 273.15
            print('Temperature: ', round(temp, 1), 'C')
            if temp >= 45:
                            check = 0
                            counter = 0

                            while check in range(10):
                                    if temp > 45:
                                            counter += 1
                                            
                            if counter >= 8:
                                print("Dangerous temperatures detected, turning off.")
                                sys.exit()

            vibratorON()
            t2 = time()
            dt = t2 - t1
            if dt > 60:
                vibratorOFF()
                print("Vibration OFF @", round(t2,2), "\n elapsed time:", round(dt,2))
                break
            # one minute of mechanical vibration therapy
            sleep(1)
    loop_OFF()
'''Logic and structure are the same as the EMS loop, moves to a rest stage that only maintains the thermistor's function.'''
    

def loop_OFF():
    t1 = time()
    print("________________________________________________________")
    print("------------Rest time begins:", round(t1,2), "------------")
    while True:
            analogVal = ADC.read(0)
            Vr = 5 * float(analogVal) / 255
            Rt = 10000 * Vr / (5 - Vr)
            temp = 1/(((math.log(Rt / 10000)) / 3950) + (1 / (273.15 + 25)))
            temp = temp - 273.15
            print('Temperature: ', round(temp,1), 'C')
            if temp >= 45:
                            check = 0
                            counter = 0

                            while check in range(10):
                                    if temp > 45:
                                            counter += 1
                                            
                            if counter >= 8:
                                print("Dangerous temperatures detected, turning off.")
                                sys.exit()
                                    
            t2 = time()
            dt = t2 - t1
            if dt > 3420:
                print("Rest time complete @", round(t2,2), "\n elapsed time:", round(dt,2))
                break
            sleep(1)
    loop_EON()
'''Once again, the same structure and function as the loops. After the rest period is complete, the program returns to the EMS stage - maintaining an infinite loop.'''
            
if __name__ == '__main__':
    try:
            print("________________________________________________________")
            print("------------------Welcome to STIMWEAR-------------------")
            print("________________________________________________________")
            setup()
            loop_EON()
            # sets up pins, therapy loop initialized
            
    except KeyboardInterrupt:
            vibratorOFF()
            indicatorOFF()
            print("Indicator OFF")
            print("________________________________________________________")
            print("-------------------Exiting STIMWEAR---------------------")
            print("________________________________________________________")
            # in case of keyboard interrupt, all modules are switched off
            pass	
