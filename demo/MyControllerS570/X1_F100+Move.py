import threading
import time

import serial
from pymycobot import *
from exoskeleton_api import Exoskeleton
from mercury_ros_api import MapNavigation
from pymycobot.mycobot import MyCobot
from pymycobot.utils import get_port_list


obj = Exoskeleton(port="/dev/ttyACM4")
ml = Mercury("/dev/left_arm")
mr = Mercury("/dev/right_arm")

# 设置双臂为速度融合模式
ml.set_movement_type(3)
mr.set_movement_type(3)

map_navigation = MapNavigation()


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
        # map_navigation.stop()


# 0 左臂，1 右臂
def control_arm(arm):
    while True:
        if arm == 1:
            arm_data = obj.get_arm_data(1)
            print("l: ", arm_data)
            mc = ml
        elif arm == 2:
            arm_data = obj.get_arm_data(2)
            x, y = arm_data[9], arm_data[10]
            print("r: ", arm_data)
            mc = mr
            threading.Thread(target=move, args=(x, y,)).start()
        else:
            raise ValueError("error arm")

        mercury_list = [
            -arm_data[1] - 40, arm_data[0] - 90, -arm_data[3], arm_data[5],
            arm_data[4], arm_data[6]
        ]

        mc.send_angles(mercury_list, 100)


# 左臂
# threading.Thread(target=control_arm, args=(0,)).start()
# 右臂
threading.Thread(target=control_arm, args=(1,)).start()
