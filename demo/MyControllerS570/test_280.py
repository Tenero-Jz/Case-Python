import threading
import time

from exoskeleton_api import Exoskeleton
from pymycobot import *

mr = MyCobot280("COM3", 115200)
obj = Exoskeleton(port="COM7")

mr.set_fresh_mode(1)
# mr.get_gripper_value()

# 开启吸泵
def pump_on():
    mr.set_basic_output(5, 0)
    time.sleep(0.05)


# 停止吸泵
def pump_off():
    mr.set_basic_output(5, 1)
    time.sleep(0.05)
    mr.set_basic_output(2, 0)
    time.sleep(1)
    mr.set_basic_output(2, 1)
    time.sleep(0.05)


def gripper_control(mode, mc):
    if mode == 0:
        mc.set_gripper_value(1, 100, 1)  # 设置夹爪以60的速度闭合5度
    elif mode == 1:
        mc.set_gripper_value(50, 100, 1)  # 设置夹爪以60的速度张开100度
    else:
        raise ValueError("Invalid mode identifier")


def arm_control(arm):
    while True:
        if arm == 1:
            arm_data = obj.get_arm_data(1)  # 读取左臂的数据
            # print("l: ", arm_data)
        elif arm == 2:
            arm_data = obj.get_arm_data(2)  # 读取右臂的数据
            mc = mr
            # print("r: ", arm_data)
        else:
            raise ValueError("Invalid arm identifier")

        if arm_data[9] == 0:
            threading.Thread(target=gripper_control, args=(0, mc,)).start()
        elif arm_data[10] == 0:
            threading.Thread(target=gripper_control, args=(1, mc,)).start()

        # 根据人体工学匹配外骨骼控制机械臂的初始位置
        mercury_list = [
            -arm_data[1] - 40, arm_data[0] - 35, -arm_data[3], arm_data[5] + 45, arm_data[4] + 90, -arm_data[6] + 30
        ]
        mc.send_angles(mercury_list, 90)  # 发送角度给机械臂
        time.sleep(0.01)  # 添加延时，以便达到流程运行的效果


# 启动线程
threading.Thread(target=arm_control, args=(2,)).start()

