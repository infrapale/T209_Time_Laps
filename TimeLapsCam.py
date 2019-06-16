"""
T209 TimeLapsCam
Time Laps Camera

"""
from picamera import PiCamera
#from gpiozero import MotionSensor
from gpiozero import Button
import board
import busio
from digitalio import DigitalInOut
import time
from time import gmtime, strftime
import adafruit_ssd1306
from datetime import datetime
from time import sleep
import os
import subprocess
import sys
import threading
from threading import Timer
from subprocess import call

print('3D AI Camera..')

io_pin = {'JOY_UP':17,'JOY_DOWN':22,'JOY_LEFT':27,'JOY_RIGHT':23,'JOY_PRESS':4,
          'BTN_A':5,'BTN_B':6}

i2c = busio.I2C(board.SCL, board.SDA)
reset_pin = DigitalInOut(board.D5)
display = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c, addr=0x3c, reset=reset_pin)

# Set up all our devices
camera = PiCamera()
camera.vflip = True
camera.hflip = True

btn_A = Button(io_pin['BTN_A'])        
btn_B = Button(io_pin['BTN_B'])
joy_up = Button(io_pin['JOY_UP'])
joy_down = Button(io_pin['JOY_DOWN'])
joy_press = Button(io_pin['JOY_PRESS'])
joy_left = Button(io_pin['JOY_LEFT'])
joy_right = Button(io_pin['JOY_RIGHT'])

halytys = False
aika =0
video_laskuri = 0
running = True


pic_root ='/home/pi/3d_pic/'

time_cntr = 30
run_photo = False
menu_indx = 0
menu_hindx = 0
ival = 2
ival_cntr = 0
prev_minute =0
run_thread = True

def run_1min():
    global time_cntr
    global ival_cntr
    sec_tick = True
    if run_thread:
       t = Timer(60.0,run_1min)
       t.start()
       
    #print(time.time())
    if time_cntr > 0:
        time_cntr -= 1
    if ival_cntr > 0:
        ival_cntr -= 1
    else:
        ival_cntr = ival
        if run_photo:
            take_photo()
    
    print('@ run_1min')            
    menu_handler()
    
def run_shutdown():
    display.fill(0)
    display.text('Shutdown now',0,0,2)
    display.show()
    call("sudo nohup shutdown -h now", shell=True)
 
def nop():
    pass
def menu_up():
    global menu_indx
    if menu_indx < 2:
        menu_indx += 1
    menu_handler()

def menu_down():
    global menu_indx
    if menu_indx > 0:
        menu_indx -= 1
    menu_handler()    

def menu_right():
    global menu_indx
    menu_matrix[menu_indx][3]()   
    menu_handler()

def menu_left():
    global menu_indx
    menu_matrix[menu_indx][2]()   
    menu_handler()

def menu_press():
    global menu_indx
    menu_matrix[menu_indx][1]()
    menu_handler()

def clear_time():
    global time_cntr
    time_cntr = 0
    
def send_photo(file_name):
    os.system('scp '+file_name+ ' pi@192.168.0.10:pic_3d/')
    pass

def take_photo():
    camera.resolution = (2592,1944)
    camera.start_preview(fullscreen=False,window=(100,20,640,480))
    sleep(2)
    ts = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    file_name ='pic'+ts+'.jpg'
    print (pic_root+file_name)
    camera.capture(pic_root+file_name)
    camera.stop_preview()
    send_photo(pic_root+file_name)
def start_photo():
    global run_photo
    run_photo = True
def stop_photo():
    global run_photo
    run_photo = False
def more_time():
    global time_cntr
    time_cntr += 15
def less_time():
    global time_cntr
    time_cntr -= 15
    if time_cntr < 0:
        time_cntr =0

def inc_ival():
    global ival
    ival += 1

def dec_ival():
    global ival
    if ival > 1:
        ival -= 1

     
menu_matrix =[['Start / Stop',take_photo, stop_photo, start_photo],
              ['Set Duration',clear_time,less_time, more_time],
              ['Set Interval',nop,dec_ival,inc_ival]]

btn_A.when_pressed = take_photo
btn_B.when_pressed = run_shutdown
joy_up.when_pressed = menu_up
joy_down.when_pressed = menu_down
joy_right.when_pressed = menu_right
joy_left.when_pressed = menu_left
joy_press.when_pressed = menu_press


def menu_handler():
    display.fill(0)
    display.text(menu_matrix[menu_indx][0],0,0,2)
    print(menu_matrix[menu_indx][0])
    if menu_indx == 0:
        pass
    elif menu_indx == 1:
        
        display.text('Duration = {0} min'.format(time_cntr),0,20,1)
    elif menu_indx == 2:
        display.text('Interval = {0} min'.format(ival),0,20,1)
    display.text('Remaining Time= {0}/{1}'.format(ival_cntr,time_cntr),0,30,1)
    if run_photo:
        display.text('Running',0,50,1)
    else:
        display.text('Stopped',0,50,1)

    display.show()  

def main():
    ival_cntr = 0
    #t = Timer(1.0,run_1sec)
    run_1min()
    try:
        while True:
            pass            
           
    except KeyboardInterrupt:
       print('Keyboard Interrupt')
       run_thread = False
       t.cancel()
       pass
    except:
       print('Other exception')
       return(1)
       pass
    
if __name__ == "__main__":
    main()
