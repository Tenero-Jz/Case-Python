# -*- coding: utf-8 -*-
import threading
import time
import serial
from pymycobot import *


obj = ExoskeletonSocket("192.168.4.1", 80)
move = ChassisControl(port="/dev/wheeltec_controller")
ml = Mercury("/dev/left_arm")
mr = Mercury("/dev/right_arm")

# 设置双臂为速度融合模式
ml.set_movement_type(3)
mr.set_movement_type(3)
ml.set_vr_mode(1)
mr.set_vr_mode(1)
ml.set_pro_gripper_speed(14, 80)
mr.set_pro_gripper_speed(14, 80)
# 定义全局状态变量
last_move_cmd = None
last_rotation_cmd = None
move_lock = threading.Lock()


# 控制底盘移动
def control_move(x, y):
    global last_move_cmd
    with move_lock:
        if y < 50:
            if last_move_cmd != 'forward':
                move.go_straight(0.2)
                last_move_cmd = 'forward'
        elif y > 200:
            if last_move_cmd != 'backward':
                move.go_back(-0.2)
                last_move_cmd = 'backward'
        elif x > 200:
            if last_move_cmd != 'left':
                move.turn_left(0.3)
                last_move_cmd = 'left'
        elif x < 50:
            if last_move_cmd != 'right':
                move.turn_right(-0.3)
                last_move_cmd = 'right'
        elif 50 < y < 200 and 50 < x < 200:
            if last_move_cmd != 'stop':
                move.stop()
                last_move_cmd = 'stop'


# 停止移动
def stop():
    global last_move_cmd
    with move_lock:
        if last_move_cmd != 'stop':
            move.stop()
            last_move_cmd = 'stop'


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
            arm_data[0], -arm_data[1] + 10, arm_data[2],
            -arm_data[3], arm_data[4], 135 + arm_data[5], arm_data[6] - 20
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
