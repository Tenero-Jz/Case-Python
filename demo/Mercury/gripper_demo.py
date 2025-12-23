import time

from pymycobot import *

ml = Mercury("/dev/left_arm")

ml.set_pro_gripper_speed(14, 100)

while True:
    time1 = time.time()
    ml.set_pro_gripper_abs_angle(14, 100)
    while True:
        if ml.get_pro_gripper_angle(14) == 100:
            time2 = time.time()
            print("张开夹爪延迟：", time2 - time1)
            break
    time.sleep(1)

    time3 = time.time()
    ml.set_pro_gripper_abs_angle(14, 0)
    while True:
        if ml.get_pro_gripper_angle(14) == 0:
            time4 = time.time()
            print("闭合夹爪延迟：", time4 - time3)
            break
    time.sleep(1)

