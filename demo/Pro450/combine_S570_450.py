import os
import threading
import time
import serial
from Pro450.pymycobot import Exoskeleton, Pro450Client
from pymycobot.utils import get_port_list

Pro450 = Pro450Client("192.168.0.232", 4500)

obj = Exoskeleton("COM7")
Pro450.set_fresh_mode(1)


# 控制夹爪函数
def open_gripper():
    Pro450.set_pro_gripper_open()
    Pro450.set_pro_gripper_open()


def close_gripper():
    Pro450.set_pro_gripper_close()
    Pro450.set_pro_gripper_close()


def control_arm(arm):
    while True:
        if arm == 2:
            arm_data = obj.get_arm_data(2)
            x, y = arm_data[11], arm_data[12]
            red_btn = arm_data[9]
            blue_btn = arm_data[10]
            mercury_list = [
                -arm_data[1] - 40, arm_data[0], -arm_data[3] - 20, arm_data[5] + 40,
                arm_data[4] + 70, arm_data[6] - 50
            ]

            Pro450.send_angles(mercury_list, 100)

            if red_btn == 0:
                threading.Thread(target=open_gripper, args=()).start()

            elif blue_btn == 0:
                threading.Thread(target=close_gripper, args=()).start()


def main():
    # threading.Thread(target=control_arm, args=(1,)).start()  # 左臂
    threading.Thread(target=control_arm, args=(2,)).start()  # 右臂
    while True:
        time.sleep(1)


if __name__ == "__main__":
    main()
