# !/usr/bin/env python
# -*- coding: UTF-8 -*-
import time
from pymycobot import *

ml = Mercury("/dev/left_arm")


def wait():
    time.sleep(0.2)
    while ml.is_moving():
        time.sleep(0.03)


AGING_TIME = 48 * 60 * 60  # 48小时
start_time = time.time()

print("开始单关节老化测试，共需运行 48 小时...")
try:
    while True:
        elapsed_time = time.time() - start_time
        if elapsed_time >= AGING_TIME:
            print("老化测试完成，程序已停止。")
            break

        # 每种速度都完整执行一轮角度切换
        for speed in [10, 50, 100]:
            print(f"当前速度: {speed}")
            for angle in [0, -160, 160]:
                ml.send_angle(7, angle, speed)
                wait()

        # 打印运行时间
        hours = elapsed_time / 3600
        print(f"已运行 {hours:.2f} 小时 / 48 小时")

except KeyboardInterrupt:
    print("手动终止老化测试。")

finally:
    ml.send_angle(7, 0, 50)
    wait()
    print("机械臂已复位。")
