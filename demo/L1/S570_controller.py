import os
import threading
import time
import serial
from pymycobot import *
from pymycobot.utils import get_port_list
from dmmotordrive import DMMotorDrive as DMMotorDrive1
from dmmotordrive import DMMotorDrive as DMMotorDrive2
import dmmotordrive


os.system("sudo chmod 777 /dev/ttyACM*")
agv_pro = MyAGVProSocket("192.168.4.1", 9000)
obj = Exoskeleton(port="/dev/ttyACM2")
ml = DMMotorDrive1("/dev/ttyACM1")
mr = DMMotorDrive2("/dev/ttyACM4")
body = dmmotordrive.SD100("/dev/ttyACM0")


# 设置初始身体高度
body.set_pos(1, 10, 100, 200, 200)
# 定义全局状态变量
last_move_cmd = None
last_rotation_cmd = None
move_lock = threading.Lock()
# 全局变量：身体高度
body_height = 10
body_height_lock = threading.Lock()
# 初始化红按钮点击计数器（奇偶判断用）
left_red_btn_count = 0
right_red_btn_count = 0
btn_lock = threading.Lock()


# 控制力控夹爪开闭
def control_gripper(arm, mode):
    if arm == 1:
        ml.gripper_control(mode)
    elif arm == 2:
        mr.gripper_control(mode)
    else:
        raise ValueError("error arm")


# 控制底盘移动
def move(x, y):
    global last_move_cmd
    with move_lock:
        if y < 50:
            if last_move_cmd != 'forward':
                agv_pro.move_forward(0.2)
                last_move_cmd = 'forward'
        elif y > 200:
            if last_move_cmd != 'backward':
                agv_pro.move_backward(0.2)
                last_move_cmd = 'backward'
        elif x > 200:
            if last_move_cmd != 'left':
                agv_pro.move_left_lateral(0.2)
                last_move_cmd = 'left'
        elif x < 50:
            if last_move_cmd != 'right':
                agv_pro.move_right_lateral(0.2)
                last_move_cmd = 'right'
        elif 50 < y < 200 and 50 < x < 200:
            if last_move_cmd != 'stop':
                agv_pro.stop()
                last_move_cmd = 'stop'


# 停止移动
def stop():
    global last_move_cmd
    with move_lock:
        if last_move_cmd != 'stop':
            agv_pro.stop()
            last_move_cmd = 'stop'


# 控制底盘旋转
def rotation(x):
    global last_rotation_cmd
    with move_lock:
        if x > 200:
            if last_rotation_cmd != 'left':
                agv_pro.turn_right(0.35)
                last_rotation_cmd = 'left'
        elif x < 50:
            if last_rotation_cmd != 'right':
                agv_pro.turn_left(0.35)
                last_rotation_cmd = 'right'
        elif 50 < x < 200:
            if last_rotation_cmd != 'stop':
                agv_pro.stop()
                last_rotation_cmd = 'stop'


def control_body(i):
    body.set_pos(1, i, 100, 200, 200)


def adjust_body_height(arm):
    global body_height
    step = -1 if arm == 1 else 1  # 左臂升（减），右臂降（加）
    while True:
        with body_height_lock:
            new_height = body_height + step
            new_height = max(0, min(150, new_height))
            if new_height != body_height:
                body_height = new_height
                control_body(body_height)


# 摇头
def head_move_1(arm):
    if arm == 1:
        mr.send_angle(7, 30, 30)
    elif arm == 2:
        mr.send_angle(7, -30, 30)


# 点头
def head_move_2(arm):
    if arm == 1:
        mr.send_angle(8, 10, 30)
    elif arm == 2:
        mr.send_angle(8, -10, 30)


# 回初始位
def head_move_3(arm):
    if arm == 1:
        mr.send_angle(7, 0, 50)
    elif arm == 2:
        mr.send_angle(8, 0, 50)


def control_arm(arm):
    global last_rotation_cmd, left_red_btn_count, right_red_btn_count
    while True:
        if arm == 1:
            arm_data = obj.get_arm_data(1)
            x, y = arm_data[11], arm_data[12]
            mc = ml
            threading.Thread(target=move, args=(x, y,)).start()
            mercury_list = [
                arm_data[0], -arm_data[1], arm_data[3], arm_data[4],
                -arm_data[5], arm_data[6]
            ]
            mc.send_angles(mercury_list, 30)
            time.sleep(0.01)

        elif arm == 2:
            arm_data = obj.get_arm_data(2)
            x = arm_data[11]
            mc = mr
            threading.Thread(target=rotation, args=(x,)).start()
            mercury_list = [
                arm_data[0], arm_data[1], -arm_data[3], -arm_data[4],
                -arm_data[5], -arm_data[6]
            ]
            mc.send_angles(mercury_list, 30)
            time.sleep(0.01)
        else:
            raise ValueError("error arm")

        red_btn = arm_data[9]
        blue_btn = arm_data[10]
        atom_btn = arm_data[7]

        # 红色按钮控制夹爪奇偶开关
        # if red_btn == 0:
        #     with btn_lock:
        #         if arm == 1:
        #             left_red_btn_count += 1
        #             mode = left_red_btn_count % 2
        #             threading.Thread(target=control_gripper, args=(1, mode)).start()
        #         else:
        #             right_red_btn_count += 1
        #             mode = right_red_btn_count % 2
        #             threading.Thread(target=control_gripper, args=(2, mode)).start()
        #
        #         # 防抖延时，直到按钮松开
        #         while obj.get_arm_data(arm)[9] == 0:
        #             time.sleep(0.05)

        # 蓝按下控制身体升降
        if atom_btn == 0:
            if arm == 1:
                threading.Thread(target=control_body, args=(0,)).start()
            else:
                threading.Thread(target=control_body, args=(70,)).start()

        # 头部运动
        if arm == 1:
            if blue_btn == 0:
                threading.Thread(target=head_move_1, args=(arm,)).start()
            if red_btn == 0:
                threading.Thread(target=head_move_2, args=(arm,)).start()
            if blue_btn == 0 and red_btn == 0:
                threading.Thread(target=head_move_3, args=(arm,)).start()


def main():
    threading.Thread(target=control_arm, args=(1,)).start()  # 左臂
    threading.Thread(target=control_arm, args=(2,)).start()  # 右臂
    while True:
        time.sleep(1)


if __name__ == "__main__":
    main()
