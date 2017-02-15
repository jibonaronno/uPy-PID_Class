# uPy-PID_Class
PID Class written in MicroPython for Pyboard. 

This class is a simple implementation of PID operations. Important issue is to call the cyclic function at a regular interval. 
This interval duration may vary depending on application. I tested this PID class over a DC Motor equiped with a Rotary Encoder. 
TIMER2 is used for Rotary Encoder Interface. The TIMER2 instance enc_timer is used to access the Encoder Count by 
enc_timer.counter() function. Also we can set a value to the counter by enc_timer.counter(0) function. Where enc_timer is a 
live object instance.
