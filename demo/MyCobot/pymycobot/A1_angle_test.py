"""
A1_angle_test.py
This module controls the robotic arm movements.

Author: Wang Weijian
Date: 2025-06-10
"""
from pymycobot import *
import time
import random
import threading

mc = Mercury('COM33')
speed = 100

angles_1 = [73.632, 84.605, -8.222, -22.29, 0.87, 89.998, 0.0]
angles_2 = [71, -50, -50, -22.29, 90.87, 89.998, 0.0]
angles_3 = [160, -50, -157, -71.29, -90.87, 89.998, 0.0]
angles_4 = [102, 93, -101, -43.29, 100.87, 89.998, 0.0]
angles_home = [0, 0, 0, 0, 0, 90, 0]

angles_list = [angles_1, angles_2, angles_3, angles_4]

if not mc.is_power_on():
    mc.power_on()

# 用线程触发随机 stop
def random_stop():
    print("\n>>> stop() 触发！\n")
    try:
        mc.stop()
    except Exception as e:
        print("stop 异常：", e)

# 主运动循环
for i in range(100):
    for angles in angles_list:
        # 随机决定是否中断
        if random.random() < 0.5:  # 50% 概率触发 stop
            threading.Thread(target=random_stop).start()

        # print(f"运动到: {angles}")
        mc.send_angles(angles, speed)
        # time.sleep(2)  # 给一点时间让动作开始执行

# 回到初始位
mc.send_angles(angles_home, speed)
