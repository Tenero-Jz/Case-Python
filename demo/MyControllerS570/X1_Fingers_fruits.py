import threading
from pymycobot import Mercury
import time
from exoskeleton_api import Exoskeleton, ExoskeletonSocket
import os

os.system("sudo chmod 777 /dev/ttyACM*")

obj = Exoskeleton(port="/dev/ttyACM2")

ml = Mercury("/dev/left_arm")
mr = Mercury("/dev/right_arm")
# mr.send_angle(1,20,20)
l_control_mode = 1
r_control_mode = 1

l_last_mode = 0
r_last_mode = 0

# 设置双臂为速度融合模式
ml.set_movement_type(3)
mr.set_movement_type(3)
# 设置VR模式
ml.set_vr_mode(1)
mr.set_vr_mode(1)

mr.set_hand_gripper_angle(1, 90)
mr.set_hand_gripper_angle(2, 90)
mr.set_hand_gripper_angle(3, 90)
mr.set_hand_gripper_angle(4, 80)
mr.set_hand_gripper_angle(5, 60)
mr.set_hand_gripper_angle(6, 56)

ml.set_hand_gripper_angle(3, 90)
ml.set_hand_gripper_angle(4, 60)
ml.set_hand_gripper_angle(5, 94)
ml.set_hand_gripper_angle(6, 66)


def jointlimit(angles):
    max = [165, 120, 175, 0, 175, 180, 175]
    min = [-165, -50, -175, -175, -175, 60, -175]
    for i in range(7):
        if angles[i] > max[i]:
            angles[i] = max[i]
        if angles[i] < min[i]:
            angles[i] = min[i]


# def gripper_control_open_1():
#     mr.set_hand_gripper_angle(14, 1, 0)

num = 3


def l_move_3(mc):  # [-23.64, 56.085, 4.618, -36.925, 68.139, 141.765, 12.36]  [-15.707, 39.084, 4.831, -54.917, 84.619, 135.638, -9.543]
    mc.send_angle(3, 4.831, 50)


def l_move_4(mc):
    mc.send_angle(4, -36.925, 50)


def l_move_5(mc):
    mc.send_angle(5, 68.1395, 50)


def l_move_6(mc):
    mc.send_angle(6, 141.765, 50)


def l_move_7(mc):
    mc.send_angle(7, 12.36, 50)


def l_gripper_control_close_1(mc):
    mc.set_hand_gripper_angle(1, 40)


def l_gripper_control_close_2(mc):
    mc.set_hand_gripper_angle(2, 55)


def l_gripper_control_open_1(mc):
    mc.set_hand_gripper_angle(1, 0)


def l_gripper_control_open_2(mc):
    mc.set_hand_gripper_angle(2, 0)


# 1 左臂，2 右臂
def control_arm(arm):
    global l_control_mode, l_last_mode, r_control_mode, r_last_mode
    st = 0
    while True:
        try:
            if arm == 1:
                arm_data = obj.get_arm_data(1)
                # print("l: ", arm_data)
                mc = ml
            elif arm == 2:
                arm_data = obj.get_arm_data(2)
                print("r: ", arm_data)
                mc = mr
            else:
                raise ValueError("error arm")
            time_err = 1000 * (time.time() - st)
            st = time.time()
            a = 177.5
            if arm == 1:
                mercury_list = [  # 只控制一二关节[-30.809, 46.801, 36.25, -36.917, 67.891, 86.44, -85.724]
                    arm_data[0] - 20, -arm_data[1], 36.25, -36.917, 67.891, 86.44, -85.724
                ]

                jointlimit(mercury_list)
                TH = 20
                if arm_data[9] == 0:
                    threading.Thread(target=l_gripper_control_close_1, args=(mc,)).start()
                    time.sleep(0.01)
                    threading.Thread(target=l_gripper_control_close_2, args=(mc,)).start()
                    # continue

                elif arm_data[10] == 0:
                    threading.Thread(target=l_gripper_control_open_1, args=(mc,)).start()
                    time.sleep(0.01)
                    threading.Thread(target=l_gripper_control_open_2, args=(mc,)).start()

                if arm_data[9] == 0 and arm_data[10] == 0:
                    # ml.send_angle(7, 20, 100)
                    continue

                if arm_data[7] == 0 and l_last_mode == 0:
                    l_last_mode = 1
                    l_control_mode += 1
                    if l_control_mode > 3:
                        l_control_mode = 1

                    if l_control_mode == 1:
                        obj.set_color(arm, 0, 255, 0)
                    elif l_control_mode == 2:
                        obj.set_color(arm, 0, 0, 255)
                    else:
                        obj.set_color(arm, 255, 0, 0)

                if arm_data[7] == 1:
                    l_last_mode = 0

                if l_control_mode == 1:
                    TI = 10

                elif l_control_mode == 2:
                    TI = 5
                else:
                    TI = 3

            else:  # 右臂 只控制1、2、4关节[20.441, 59.376, 14.112, -53.285, -96.702, 58.361, 140.565]
                mercury_list = [
                    arm_data[0] + 20, -arm_data[1], 14.112, -arm_data[3] - 30,  -96.702, 58.361, 140.565
                ]
                jointlimit(mercury_list)

                if arm_data[7] == 0 and r_last_mode == 0:
                    r_last_mode = 1
                    r_control_mode += 1
                    if r_control_mode > 3:
                        r_control_mode = 1
                    if r_control_mode == 1:
                        obj.set_color(arm, 0, 255, 0)
                    elif r_control_mode == 2:
                        obj.set_color(arm, 0, 0, 255)
                    else:
                        obj.set_color(arm, 255, 0, 0)

                if arm_data[7] == 1:
                    r_last_mode = 0
                if r_control_mode == 1:
                    TI = 10
                elif r_control_mode == 2:
                    TI = 5
                else:
                    TI = 3
                if arm_data[9] == 0:  # 设置左手姿态-可抓取水果[-15.707, 39.084, 4.831, -54.917, 84.619, 135.638, -9.543]
                    threading.Thread(target=l_move_3, args=(ml,)).start()
                    threading.Thread(target=l_move_4, args=(ml,)).start()
                    threading.Thread(target=l_move_5, args=(ml,)).start()
                    threading.Thread(target=l_move_6, args=(ml,)).start()
                    threading.Thread(target=l_move_7, args=(ml,)).start()

            mc.send_angles(mercury_list, TI, _async=True)
            time.sleep(0.01)
            # print(mercury_list)

            # mc.send_angles(mercury_list, 6)
        except Exception as e:
            print(e)
            pass


# 左臂
threading.Thread(target=control_arm, args=(1,)).start()
# 右臂
threading.Thread(target=control_arm, args=(2,)).start()
