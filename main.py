
import pyb
import stm
import micropython
micropython.alloc_emergency_exception_buf(100)

# This script sets up a timer to do quadrature decoding
#
# It was tested using a switch similar to https://www.sparkfun.com/products/9117

t4_int_tick001 = 0
t4_int_tick002 = 0
t4_int_counter001 = 0

t4_int_counter01 = 0

pin_a = pyb.Pin(pyb.Pin.cpu.A0, pyb.Pin.AF_PP, pull=pyb.Pin.PULL_NONE, af=pyb.Pin.AF1_TIM2)
pin_b = pyb.Pin(pyb.Pin.cpu.A1, pyb.Pin.AF_PP, pull=pyb.Pin.PULL_NONE, af=pyb.Pin.AF1_TIM2)

enc_timer = pyb.Timer(2, prescaler=1, period=5000000)
enc_channel = enc_timer.channel(1, pyb.Timer.ENC_B)

def dump_regs(timer_base):
    smcr = stm.mem16[timer_base + stm.TIM_SMCR]
    sms = smcr & 0x0007
    ece = (smcr & 0x4000) >> 14
    print('SMS = {:03b} ECE = {:1b}'.format(sms, ece))

dump_regs(stm.TIM2)

out_idx = 0
out_seq = [0, 1, 3, 2]

pin_a2 = pyb.Pin('D2', pyb.Pin.OUT_PP)
pin_b2 = pyb.Pin('D3', pyb.Pin.OUT_PP)

t3 = pyb.Timer(3, freq=600, mode=pyb.Timer.CENTER)
ch1 = t3.channel(1, pyb.Timer.PWM, pin=pyb.Pin.cpu.C6, pulse_width_percent = 0)
ch2 = t3.channel(2, pyb.Timer.PWM, pin=pyb.Pin.cpu.C7, pulse_width_percent = 0)


def timer4_regular_interval_callback(timer):
    global t4_int_counter001
    global t4_int_tick001

    global t4_int_counter01
    global t4_int_tick002
    t4_int_tick001 = 1
    t4_int_counter01 = t4_int_counter01 + 1
    if(t4_int_counter01 > 100):
        t4_int_counter01 = 0
        t4_int_tick002 = 1


def anticlock(upcount):
    while(enc_timer.counter() < upcount):
        ch1.pulse_width_percent(12)

    ch1.pulse_width_percent(0)
    print('ENCODER:{:d}'.format(enc_timer.counter()))

def clockwise(downcount):
    while(enc_timer.counter() > downcount):
        ch2.pulse_width_percent(12)

    ch2.pulse_width_percent(0)
    print('ENCODER:{:d}'.format(enc_timer.counter()))

def set_out():
    print("Writing {:d}{:d}".format((out_seq[out_idx] & 0x01) != 0, (out_seq[out_idx] & 0x02) != 0))
    pin_a2.value((out_seq[out_idx] & 0x01) != 0)
    pin_b2.value((out_seq[out_idx] & 0x02) != 0)

def incr():
    global out_idx
    out_idx = (out_idx + 1) % 4
    set_out()

def decr():
    global out_idx
    out_idx = (out_idx - 1) % 4
    set_out()

if False:
    set_out()
    while True:
        for i in range(100):
            print("Counter =", enc_timer.counter(), " channel =", enc_channel.capture())
            incr()
            pyb.delay(400)
        for i in range(100):
            print("Counter =", enc_timer.counter(), " channel =", enc_channel.capture())
            decr()
            pyb.delay(400)
        break

timer4 = pyb.Timer(4, freq=4000)
timer4.callback(timer4_regular_interval_callback)

prev_encoder_count_value = 0
encoder_count_difference = 0

import pidencoderpwm


def SetPoint(setpoint):
    pid_pwm = pidencoderpwm.PidEncoderPwm()
    global t4_int_tick002
    brk = True
    pulse_width_value = 0
    pwm_o = 0
    pwm_om = 0
    pid_pwm.set_point = setpoint
    print("FB,ERR,PT,IT,DT,PWM")
    while(brk):
        if(t4_int_tick002 == 1):
            t4_int_tick002 = 0
            if((setpoint-5) > enc_timer.counter()):
                ch2.pulse_width(0)
                if(enc_timer.counter() > (setpoint - (setpoint / 4))):
                	pwm_o = int(pid_pwm.pwm_change(enc_timer.counter(), 0))
                else:
                	pwm_o = int(pid_pwm.pwm_change(enc_timer.counter(), 0))
                pwm_om = pwm_o
                #if(pwm_o < 2500):
                	#pwm_o = 2500
                #elif(pwm_o > 17000):
                	#pwm_o = 17000
                ch1.pulse_width(pwm_o)
                #print("ANTCLK:{:d} CNT:{:d}".format(pwm_om, enc_timer.counter()))
            elif((setpoint + 5) < enc_timer.counter()):
                ch1.pulse_width(0)
                if(enc_timer.counter() > (setpoint - (setpoint / 4))):
                	pwm_o = int(pid_pwm.pwm_change(enc_timer.counter(), 0))
                else:
                	pwm_o = int(pid_pwm.pwm_change(enc_timer.counter(), 0))
                pwm_om = pwm_o

                #if(pwm_o < 2500):
                	#pwm_o = 2500
                #elif(pwm_o > 17000):
                	#pwm_o = 17000
                ch2.pulse_width(pwm_o)
                #print("CLOCK :{:d} CNT:{:d}".format(pwm_om, enc_timer.counter()))
            else:
                ch1.pulse_width(0)
                ch2.pulse_width(0)
                brk = False


while True:
    if(t4_int_tick002 == 1):
        if(prev_encoder_count_value != enc_timer.counter()):
            print("Counter =", enc_timer.counter())
        t4_int_tick002 = 0
        prev_encoder_count_value = enc_timer.counter()

