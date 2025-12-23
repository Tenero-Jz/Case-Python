import os
import threading
import time
import serial
from pymycobot import *
from pymycobot.utils import get_port_list

# obj = Exoskeleton(port="COM14")
mc = MyArmC("com4", 1000000)
while True:
    print(mc.get_joints_angle())
    time.sleep(0.1)

# while True:
#     print(obj.get_arm_data(1))
#     print(obj.get_arm_data(2))

