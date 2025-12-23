# -*- coding: utf-8 -*-
import threading
import time
import serial
from pymycobot import Exoskeleton
from mercury_arms_socket import MercuryArmsSocket


ml = MercuryArmsSocket(arm="left_arm", ip="192.168.1.216")
mr = MercuryArmsSocket(arm="right_arm", ip="192.168.1.216")
obj = Exoskeleton("COM3")

# 设置双臂为速度融合模式
ml.set_movement_type(3)
mr.set_movement_type(3)
ml.set_vr_mode(1)
mr.set_vr_mode(1)
ml.set_pro_gripper_speed(14, 80)
mr.set_pro_gripper_speed(14, 80)


def jointlimit(angles):
    max = [165, 120, 175, 0, 175, 180, 175]
    min = [-165, -50, -175, -175, -175, 60, -175]
    for i in range(7):
        if angles[i] > max[i]:
            angles[i] = max[i]
        if angles[i] < min[i]:
            angles[i] = min[i]


# 控制力控夹爪开闭
def control_gripper(mc, value):
    mc.set_pro_gripper_angle(14, value)


# 0 左臂，1 右臂
def control_arm(arm):
    while True:
        if arm == 1:
            arm_data = obj.get_arm_data(1)
            print("l: ", arm_data)
            mc = ml
        elif arm == 2:
            arm_data = obj.get_arm_data(2)
            print("r: ", arm_data)
            mc = mr
        else:
            raise ValueError("error arm")

        mercury_list = [
            arm_data[0], -arm_data[1], arm_data[2], -arm_data[3], arm_data[4],
            135 + arm_data[5], arm_data[6] - 30
        ]
        jointlimit(mercury_list)

        if arm_data[9] == 0:
            threading.Thread(target=control_gripper, args=(mc, 0,)).start()
        elif arm_data[10] == 0:
            threading.Thread(target=control_gripper, args=(mc, 99,)).start()

        if arm_data[9] == 0 and arm_data[10] == 0:
            time.sleep(0.01)
            continue

        mc.send_angles(mercury_list, 6, _async=True)
        time.sleep(0.01)


# 左臂
threading.Thread(target=control_arm, args=(1,)).start()
# 右臂
threading.Thread(target=control_arm, args=(2,)).start()
