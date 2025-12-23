import threading
import time

import serial
from pymycobot import *
from exoskeleton_api import Exoskeleton
from mercury_ros_api import MapNavigation
from pymycobot.mycobot import MyCobot
from pymycobot.utils import get_port_list

#plist = get_port_list()
#print(plist)
mr = MyCobot("/dev/ttyACM3", 115200)

obj = Exoskeleton(port="/dev/ttyACM4")
# ml = Mercury("/dev/left_arm")
# ser_r = serial.Serial(port="/dev/ttyACM4", baudrate=1000000)
# mr = MyCobot("/dev/ttyACM0")

map_navigation = MapNavigation()
mr.power_on()


def Pump_testing_open():
    import RPi.GPIO as GPIO
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(2, GPIO.OUT)
    GPIO.setup(3, GPIO.OUT)

    # open
    GPIO.output(3, GPIO.LOW)
    GPIO.output(2, GPIO.HIGH)


def Pump_testing_close():
    import RPi.GPIO as GPIO
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(2, GPIO.OUT)
    GPIO.setup(3, GPIO.OUT)
    # close
    GPIO.output(3, GPIO.HIGH)
    GPIO.output(2, GPIO.LOW)
    time.sleep(0.05)
    GPIO.output(2, GPIO.HIGH)


def move(x, y):
    if y < 50:
        map_navigation.pub_vel(0.25, 0, 0)
    elif y > 200:
        map_navigation.pub_vel(-0.25, 0, 0)
    elif x < 50:
        map_navigation.pub_vel(0, 0, -0.5)
    elif x > 200:
        map_navigation.pub_vel(0, 0, 0.5)
    else:
        map_navigation.pub_vel(0, 0, 0)
        #map_navigation.stop()


# 0 左臂，1 右臂
def control_arm(arm):
    while True:
        if arm == 0:
            arm_data = obj.get_data(0)
            x, y = arm_data[9], arm_data[10]
            print("l: ", arm_data)
            # mc = ml
            mc = mr
        elif arm == 1:
            arm_data = obj.get_data(1)
            x, y = arm_data[9], arm_data[10]
            print("r: ", arm_data)
            mc = mr
            threading.Thread(target=move, args=(x, y,)).start()
        else:
            raise ValueError("error arm")
        mercury_list = [
            -arm_data[1]-40, arm_data[0] - 90, -arm_data[3], arm_data[5],
            arm_data[4], arm_data[6]
        ]
        #mercury_list = [
        #    0, 0, 0, 0, 0,
        #    arm_data[6]
        #]
        if arm_data[7] == 0:
            Pump_testing_open()
        elif arm_data[8] == 0:
            Pump_testing_close()
        mc.send_angles(mercury_list, 100)


# 左臂
# threading.Thread(target=control_arm, args=(0,)).start()
# 右臂
threading.Thread(target=control_arm, args=(1, )).start()
