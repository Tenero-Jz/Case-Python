import threading
from pymycobot import Mercury
import time
from exoskeleton_api import Exoskeleton, ExoskeletonSocket
import os

os.system("sudo chmod 777 /dev/ttyACM*")

obj = Exoskeleton(port="/dev/ttyACM4")

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

ml.set_hand_gripper_angle(14, 4, 90)
ml.set_hand_gripper_angle(14, 5, 20)
ml.set_hand_gripper_angle(14, 6, 30)
ml.set_hand_gripper_angle(14, 1, 50)
ml.set_hand_gripper_angle(14, 3, 90)
# ml.set_hand_gripper_angle(14, 2, 50)


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


def gripper_control_open_2(mc):
    mc.set_hand_gripper_angle(14, 2, 0)


# def gripper_control_open_3():
#     mr.set_hand_gripper_angle(14, 3, 0)


# def gripper_control_close_1():
#     mr.set_hand_gripper_angle(14, 1, 35)


def gripper_control_close_2(mc):
    mc.set_hand_gripper_angle(14, 2, 90)


# def gripper_control_close_3():
#     mr.set_hand_gripper_angle(14, 3, 43)


# 1 左臂，2 右臂
def control_arm(arm):
    global l_control_mode, l_last_mode, r_control_mode, r_last_mode
    st = 0
    while True:
        try:
            if arm == 1:
                arm_data = obj.get_arm_data(1)
                print("l: ", arm_data)
                mc = ml
            elif arm == 2:
                arm_data = obj.get_arm_data(2)
                # print("r: ", arm_data)
                mc = mr
            else:
                raise ValueError("error arm")
            # mercury_list = [
            #     arm_data[0], -arm_data[1], arm_data[2], -arm_data[3], arm_data[4], 135 + arm_data[5], arm_data[6] - 90
            # ]
            # mercury_list = [
            #     arm_data[0]-10, -arm_data[1], arm_data[2], -arm_data[3], 100, 38, 0
            # ]
            # jointlimit(mercury_list)
            time_err = 1000 * (time.time() - st)
            st = time.time()
            # print(2)
            # TI = 3
            if arm == 1:
                mercury_list = [
                    arm_data[0] - 10, -arm_data[1], arm_data[2], -arm_data[3], 105, 38, 0
                ]
                jointlimit(mercury_list)
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
                if arm_data[9] == 0:
                    # ml.set_hand_gripper_angle(14, 2, 70)
                    threading.Thread(target=gripper_control_close_2, args=(mc,)).start()

                elif arm_data[10] == 0:
                    # ml.set_hand_gripper_angle(14, 2, 0)
                    threading.Thread(target=gripper_control_open_2, args=(mc,)).start()
                if arm_data[9] == 0 and arm_data[10] == 0:
                    time.sleep(0.01)
                    continue

            else:  # 右臂
                mercury_list = [
                    arm_data[0], -arm_data[1], -0.524, -41.862, -90.686, 101.273, 25.257
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

            mc.send_angles(mercury_list, TI, _async=True)
            time.sleep(0.01)

        except Exception as e:
            print(e)
            pass


# 左臂
threading.Thread(target=control_arm, args=(1,)).start()
# 右臂
threading.Thread(target=control_arm, args=(2,)).start()
