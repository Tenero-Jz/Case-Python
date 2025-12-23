import threading
import time
from pymycobot import *


ml = Mercury("/dev/left_arm")
mr = Mercury("/dev/right_arm")
mr.set_pro_gripper_speed(14, 100)
ml.set_pro_gripper_speed(14, 100)


def gripper_control(arm, value):
    if value == 0:
        arm.set_pro_gripper_angle(14, 80)
    else:
        arm.set_pro_gripper_angle(14, 2)


# 初始位置
def init_position(arm):
    if arm == 1:
        ml.send_angles([30.292, 62.737, -90.522, -96.081, -6.207, 20.274, 36.737], 50)
    else:
        mr.send_angles([-30.292, 62.737, 90.522, -96.081, -6.207, 20.274, -36.737], 50)


# 过度点1
def pass_position_1(arm):
    if arm == 1:
        ml.send_angles([44.204, 71.273, -94.396, -67.908, -0.511, -2.035, 36.729], 5)
    else:
        mr.send_angles([-44.204, 71.273, 94.396, -67.908, -0.511, 2.035, -36.729], 5)


# 过度点2
def pass_position_2(arm):
    if arm == 1:
        ml.send_angles([59.094, 69.942, -98.005, -81.808, 1.102, -18.71, 36.754], 5)
    else:
        mr.send_angles([-59.094, 69.942, 98.005, -81.808, -1.102, -18, -36.754], 5)


# 主程序
if __name__ == '__main__':
    threading.Thread(target=init_position, args=(1,)).start()
    threading.Thread(target=init_position, args=(2,)).start()
    time.sleep(5)
    threading.Thread(target=pass_position_1, args=(1,)).start()
    threading.Thread(target=pass_position_1, args=(2,)).start()
    time.sleep(2)
    threading.Thread(target=pass_position_2, args=(1,)).start()
    threading.Thread(target=pass_position_2, args=(2,)).start()
    time.sleep(5)
    threading.Thread(target=init_position, args=(1,)).start()
    threading.Thread(target=init_position, args=(2,)).start()
    time.sleep(2)
    time.sleep(2)

