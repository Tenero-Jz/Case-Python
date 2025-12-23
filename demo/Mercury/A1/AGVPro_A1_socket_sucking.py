# !/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
需要安装 cvzone和mediapipe库，注意这两个库会更新numpy的版本
该案例现将手臂摆放置指定位置
"""
import os
import threading
import time
from pymycobot import *
import cv2
from cvzone.HandTrackingModule import HandDetector


cap = cv2.VideoCapture(1)
ml = MercurySocket("192.168.6.247", 9000)


# 控制吸泵
def control_suck(mode):
    if mode == 1:
        ml.set_base_io_output(1, 1)
    else:
        ml.set_base_io_output(1, 0)


# 初始位置
def init_position():
    ml.send_angles([90, 0, -90, 0, 0, 90, 0], 50)
    time.sleep(1)


# 打招呼
def say_hello():
    for _ in range(3):
        ml.send_angle(2, -22, 30)
        # time.sleep(0.1)
        ml.send_angle(2, 22, 30)
        # time.sleep(0.1)
    # time.sleep(0.5)


# 吸取位置
def suck_position():
    ml.send_angles([-90, 0, 0, -90, 0, 90, 0], 50)
    time.sleep(1)
    ml.send_coord(3, 5, 40)
    time.sleep(1)


# 传递位置
def pass_position():
    ml.send_angles([-90, 0, 0, -90, 0, 90, 0], 50)
    time.sleep(0.6)
    ml.send_angles([0, 29.347, 1.362, -22.896, 4.838, 89.987, 0.0], 50)
    time.sleep(0.6)


# 创建手部检测器对象
detector = HandDetector(
    detectionCon=0.8,
    maxHands=2
)

while True:
    init_position()

    say_hello()

    init_position()

    number = 0
    gesture_detected = False
    while not gesture_detected:
        success, img = cap.read()
        if not success:
            break

        hands, img = detector.findHands(img)

        if hands:
            for hand in hands:
                fingers = detector.fingersUp(hand)
                print(fingers)
                if fingers == [1, 1, 1, 1, 1]:
                    number += 1
                    if number >= 20:
                        suck_position()
                        control_suck(1)
                        time.sleep(1)
                        pass_position()
                        time.sleep(1.5)
                        control_suck(0)
                        init_position()

                        gesture_detected = True
                        break

        # 显示画面
        cv2.imshow("Hand Tracking", img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            gesture_detected = True
            break

cap.release()
cv2.destroyAllWindows()
