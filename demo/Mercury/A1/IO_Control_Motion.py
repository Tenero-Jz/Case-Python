# !/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
开机上电 + 实时IO控制机械臂运动
IO口高电平(0) -> 执行动作序列
IO口低电平(1) -> 立即停止运动
"""
import os
import threading
import time
from pymycobot import *

os.system("sudo chmod 777 /dev/ttyAMA1")

mc = Mercury("/dev/ttyAMA1")

# 上电初始化
if mc.is_power_on() == 0:
    mc.power_on()
    time.sleep(1)


def wait():
    """等待机械臂停止"""
    time.sleep(0.2)
    while mc.is_moving():
        time.sleep(0.05)


io_state = 0  # 全局变量，记录IO口的状态


def monitor_io():
    global io_state
    while True:
        try:
            val = mc.get_base_io_input(1)
            if val is not None:
                io_state = val
            time.sleep(0.05)  # 采样频率20Hz，避免通讯过快
        except Exception as e:
            print("IO读取异常:", e)
            time.sleep(0.5)


def motion_loop():
    global io_state
    while True:
        # 只有检测到高电平时才执行动作
        if io_state == 0:
            print("检测到IO=0，开始执行动作序列")

            try:
                # 左边
                mc.send_angles([51.687, 3.6, -30.606, -66.088, -59.237, 150.306, -0.018], 80)
                wait()
                if io_state == 1: print("检测到IO=1，停止运行"); mc.stop(); continue

                mc.send_coord(1, 285, 10)
                wait()
                if io_state == 1: print("检测到IO=1，停止运行"); mc.stop(); continue

                mc.send_coord(3, 300, 10)
                wait()
                if io_state == 1: print("检测到IO=1，停止运行"); mc.stop(); continue

                # 中间
                mc.send_angles([4.887, -25.508, -6.172, -77.698, -3.404, 143.547, 1.908], 80)
                wait()
                if io_state == 1: print("检测到IO=1，停止运行"); mc.stop(); continue

                mc.send_coord(1, 170, 10)
                wait()
                if io_state == 1: print("检测到IO=1，停止运行"); mc.stop(); continue

                mc.send_coord(3, 441, 10)
                wait()
                if io_state == 1: print("检测到IO=1，停止运行"); mc.stop(); continue

                # 右边
                mc.send_angles([-10.756, -22.765, -25.713, -79.3, 49.106, 134.631, 9.128], 80)
                wait()
                if io_state == 1: print("检测到IO=1，停止运行"); mc.stop(); continue

                mc.send_coord(1, 130, 10)
                wait()
                if io_state == 1: print("检测到IO=1，停止运行"); mc.stop(); continue

                mc.send_coord(3, 390, 10)
                wait()

            except Exception as e:
                print("执行动作出错:", e)

        else:
            # 检测到低电平，停止所有动作
            print("检测到IO=1，停止运行")
            mc.stop()
            time.sleep(0.1)


if __name__ == "__main__":
    threading.Thread(target=monitor_io, daemon=True).start()
    motion_loop()
