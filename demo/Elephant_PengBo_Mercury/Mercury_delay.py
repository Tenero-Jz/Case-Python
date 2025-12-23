# !/usr/bin/env python
# -*- coding: UTF-8 -*-
from pymycobot import Mercury
from mercury_arms_socket import MercuryArmsSocket
import time
import statistics

ml = MercuryArmsSocket(arm="left_arm", ip="192.168.2.50")
mr = MercuryArmsSocket(arm="right_arm", ip="192.168.2.50")


def test_send_delay(arm, joint=1, speed=100, repeat=20):
    delays = []
    target_angles = [100, 0]

    for i in range(repeat):
        angle = target_angles[i % 2]
        t1 = time.time()
        arm.send_angle(joint, angle, speed, _async=True)
        t2 = time.time()
        delay = t2 - t1
        print(f"[send_delay] 第{i + 1}次 (角度={angle}): {delay:.4f} 秒")
        # delays.append(delay)
        time.sleep(1)
    # print(f"\n[send_delay] 平均延迟: {statistics.mean(delays):.4f} 秒\n")


def test_read_delay(arm, repeat=20):
    delays = []
    last_time = time.time()

    for i in range(repeat):
        arm.get_angles()
        now = time.time()
        delay = now - last_time
        print(f"[read_delay] 第{i + 1}次: {delay:.4f} 秒")
        # delays.append(delay)
        last_time = now
        # time.sleep(0.5)

    # print(f"\n[read_delay] 平均间隔: {statistics.mean(delays):.4f} 秒\n")


if __name__ == "__main__":
    print(">>> 测试右臂发送延迟 (1关节来回0° <-> 50°)")
    test_send_delay(mr)

    print(">>> 测试右臂读取延迟")
    test_read_delay(mr)

    # print(">>> 测试左臂发送延迟 (1关节来回0° <-> 50°)")
    # test_send_delay(ml)
    #
    # print(">>> 测试左臂读取延迟")
    # test_read_delay(ml)
