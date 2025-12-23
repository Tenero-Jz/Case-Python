# -*- coding: utf-8 -*-
import threading
import time
import serial
from pymycobot import *
from mercury_arms_socket import MercuryArmsSocket


ml = MercuryArmsSocket(arm="left_arm", ip="192.168.2.50")
mr = MercuryArmsSocket(arm="right_arm", ip="192.168.2.50")
move = ChassisControl(port="/dev/wheeltec_controller")
obj = Exoskeleton("COM3")

# 设置双臂为速度融合模式
ml.set_movement_type(3)
mr.set_movement_type(3)
ml.set_vr_mode(1)
mr.set_vr_mode(1)
ml.set_pro_gripper_speed(14, 80)
mr.set_pro_gripper_speed(14, 80)

if ml.is_power_on() == 0:
    ml.power_on()
if mr.is_power_on() == 0:
    mr.power_on()

# 定义全局状态变量
last_move_cmd = None
last_rotation_cmd = None
move_lock = threading.Lock()
moving = False
moving_thread = None


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


def keep_moving(direction):
    global moving
    while moving:
        if direction == 'forward':
            move.go_straight(0.18)
        elif direction == 'backward':
            move.go_back(-0.15)
        elif direction == 'left':
            move.turn_left(0.3)
        elif direction == 'right':
            move.turn_right(-0.3)
        time.sleep(0.05)  # 控制发送频率


def control_move(x, y):
    global last_move_cmd, moving, moving_thread
    with move_lock:
        if y < 50:
            if last_move_cmd != 'forward':
                moving = False
                if moving_thread: moving_thread.join()
                moving = True
                moving_thread = threading.Thread(target=keep_moving, args=('forward',))
                moving_thread.start()
                last_move_cmd = 'forward'

        elif y > 200:
            if last_move_cmd != 'backward':
                moving = False
                if moving_thread: moving_thread.join()
                moving = True
                moving_thread = threading.Thread(target=keep_moving, args=('backward',))
                moving_thread.start()
                last_move_cmd = 'backward'

        elif x > 200:
            if last_move_cmd != 'left':
                moving = False
                if moving_thread: moving_thread.join()
                moving = True
                moving_thread = threading.Thread(target=keep_moving, args=('left',))
                moving_thread.start()
                last_move_cmd = 'left'

        elif x < 50:
            if last_move_cmd != 'right':
                moving = False
                if moving_thread: moving_thread.join()
                moving = True
                moving_thread = threading.Thread(target=keep_moving, args=('right',))
                moving_thread.start()
                last_move_cmd = 'right'

        elif 50 < y < 200 and 50 < x < 200:
            if last_move_cmd != 'stop':
                moving = False
                move.stop()
                last_move_cmd = 'stop'


def stop():
    global last_move_cmd
    with move_lock:
        if last_move_cmd != 'stop':
            move.stop()
            last_move_cmd = 'stop'


# 0 左臂，1 右臂
def control_arm(arm):
    while True:
        if arm == 1:
            arm_data = obj.get_arm_data(1)
            x, y = arm_data[11], arm_data[12]
            # print("l: ", arm_data)
            mc = ml
            # threading.Thread(target=control_move, args=(x, y,)).start()
            mercury_list = [
                arm_data[0], -arm_data[1] + 10, arm_data[2],
                -arm_data[3], arm_data[4], 135 + arm_data[5], arm_data[6] + 20
            ]
            jointlimit(mercury_list)
        elif arm == 2:
            arm_data = obj.get_arm_data(2)
            # print("r: ", arm_data)
            mc = mr
            mercury_list = [
                arm_data[0], -arm_data[1] + 10, arm_data[2],
                -arm_data[3], arm_data[4], 135 + arm_data[5], arm_data[6] - 20
            ]
            jointlimit(mercury_list)
        else:
            raise ValueError("error arm")

        atom_btn = arm_data[7]

        if arm_data[9] == 0:
            threading.Thread(target=control_gripper, args=(mc, 0,)).start()
        elif arm_data[10] == 0:
            threading.Thread(target=control_gripper, args=(mc, 99,)).start()

        if arm_data[9] == 0 and arm_data[10] == 0:
            time.sleep(0.01)
            continue

        if atom_btn == 0:
            exit()

        mc.send_angles(mercury_list, 6, _async=True)
        time.sleep(0.01)


# 左臂
threading.Thread(target=control_arm, args=(1,)).start()
# 右臂
threading.Thread(target=control_arm, args=(2,)).start()
