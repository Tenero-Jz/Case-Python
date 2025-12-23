import threading
from pymycobot import Mercury
import time
from MyControllerS570.exoskeleton_api import Exoskeleton
import os

os.system("sudo chmod 777 /dev/ttyACM*")

obj = Exoskeleton(port="/dev/ttyACM2")

ml = Mercury("/dev/left_arm")
mr = Mercury("/dev/right_arm")
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

# mr.set_hand_gripper_angle(1, 100)
# mr.set_hand_gripper_angle(2, 70)
# mr.set_hand_gripper_angle(3, 80)
# mr.set_hand_gripper_angle(4, 80)
# mr.set_hand_gripper_angle(5, 60)
# mr.set_hand_gripper_angle(6, 30)
#
# ml.set_hand_gripper_angle(3, 90)
# ml.set_hand_gripper_angle(4, 67)
# ml.set_hand_gripper_angle(5, 60)
# ml.set_hand_gripper_angle(6, 10)


def l_move_1(mc):
    mc.set_hand_gripper_angle(1, 100)


def l_move_2(mc):
    mc.set_hand_gripper_angle(2, 100)


def l_move_3(mc):
    mc.set_hand_gripper_angle(3, 100)


def l_move_4(mc):
    mc.set_hand_gripper_angle(4, 80)


def l_move_5(mc):
    mc.set_hand_gripper_angle(5, 60)


def l_move_6(mc):
    mc.set_hand_gripper_angle(5, 30)


def jointlimit(angles):
    max = [165, 120, 175, 0, 175, 180, 175]
    min = [-165, -50, -175, -175, -175, 60, -175]
    for i in range(7):
        if angles[i] > max[i]:
            angles[i] = max[i]
        if angles[i] < min[i]:
            angles[i] = min[i]


num = 3


def l_gripper_control_close_1(mc):
    mc.set_hand_gripper_angle(1, 44)


def l_gripper_control_close_2(mc):
    mc.set_hand_gripper_angle(2, 58)


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
                # 只控制一关节,切辣椒、大蒜[-20.568, 43.446, 9.001, -69.812, 76.539, 141.191, -4.893]
                # 动1、2关节，削黄瓜皮[-17.223, 51.17, 14.123, -112.11, 141.353, 70.494, -52.326]
                # 动1、2、4、7关节，拿取倒调料[-2.034, 31.618, -1.557, -44.997, 4.417, 148.108, 1.017]
                # 动1、2、4关节，翻炒[-26.494, 23.141, -1.54, -88.207, 61.485, 150.749, 84.492]
                mercury_list = [
                    arm_data[0] - 20, -arm_data[1], 36.25, -36.917, 67.891, 86.44, -85.724
                ]
                jointlimit(mercury_list)

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
                    time.sleep(0.01)
                    continue

                if arm_data[7] == 0 and l_last_mode == 0:
                    print(6)
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

            else:
                # 右臂切+拿黄瓜+拿锅 只控1、2、4、7关节[2.49, 43.268, 13.473, -87.514, -90.478, 80.763, 141.153]
                # 拿黄瓜，只控1、2关节[-29.688, 8.736, 38.03, -134.498, -131.594, 101.62, 70.69]
                mercury_list = [
                    arm_data[0] + 20, -arm_data[1], 14.112, -arm_data[3] - 30,  -96.702, 58.361, 140.565
                ]
                jointlimit(mercury_list)

                if arm_data[7] == 0 and r_last_mode == 0:
                    print(6)
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
                if arm_data[9] == 0:  # 三指捏合
                    threading.Thread(target=l_move_4, args=(mr,)).start()
                    threading.Thread(target=l_move_5, args=(mr,)).start()
                    threading.Thread(target=l_move_6, args=(mr,)).start()
                    threading.Thread(target=l_move_1, args=(mr,)).start()
                    threading.Thread(target=l_move_2, args=(mr,)).start()
                    threading.Thread(target=l_move_3, args=(mr,)).start()

            mc.send_angles(mercury_list, TI, _async=True)
            time.sleep(0.01)

        except Exception as e:
            print(e)
            pass


# 左臂
threading.Thread(target=control_arm, args=(1,)).start()
# 右臂
threading.Thread(target=control_arm, args=(2,)).start()
