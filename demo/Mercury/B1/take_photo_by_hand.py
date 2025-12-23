# !/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
需要安装 cvzone和mediapipe库，注意这两个库会更新numpy的版本
且左臂的6关节旋转方向要改成0：ml.set_model_direction(6,0)
左臂三指安装方式：手心朝上
右臂力控安装方式：屏幕朝斜下方（朝机器人这边）
"""
import threading
import time
from pymycobot import *
import cv2
from cvzone.HandTrackingModule import HandDetector

ml = Mercury("/dev/left_arm")
mr = Mercury("/dev/right_arm")
mr.set_pro_gripper_angle(14, 100)
ml.set_hand_gripper_enabled(1)
if ml.is_power_on() == 0:
    ml.power_on()
if mr.is_power_on() == 0:
    mr.power_on()


def play_countdown_video(video_path="countdown.mp4"):
    cap_video = cv2.VideoCapture(video_path)
    if not cap_video.isOpened():
        print(f"无法打开视频文件：{video_path}")
        return

    while True:
        ret, frame = cap_video.read()
        if not ret:
            break  # 播放结束
        cv2.imshow("Countdown", frame)
        # 按 ESC 可提前退出倒计时
        if cv2.waitKey(30) & 0xFF == 27:
            break

    cap_video.release()
    cv2.destroyWindow("Countdown")


# 双臂初始位置
def right_arm_init():
    mr.send_angles([-27.071, 54.741, 10.399, -65.479, -0.249, 132.921, -66.338], 15)
    time.sleep(2)
    mr.set_pro_gripper_speed(14, 98)


def left_arm_init():
    ml.send_angles([66.604, 69.43, -40.019, -73.276, 62.509, -45.911, -12.041], 30)


def gripper_control(value):
    mr.set_pro_gripper_speed(14, 100)
    if value == 0:
        mr.set_pro_gripper_angle(14, 95)
    else:
        mr.set_pro_gripper_angle(14, 0)


# 控制手臂方便按下快门按钮
def right_arm_move_in():
    mr.send_base_coord(2, 60, 10)


# 控制手臂方便松开快门按钮
def right_arm_move_out():
    mr.send_base_coord(2, -85, 10)


# 双臂拍照点
def right_take_photo_position():
    mr.send_angles([19.065, 55.539, 35.491, -45.147, -42.692, 108.29, -4.064], 18)


def left_take_photo_position():
    ml.send_angles([-33.429, 82.806, 16.398, -72.775, -32.385, -67.535, 0.299], 20)


# 右臂打招呼函数
def right_arm_greet():
    mr.send_angles([-30.053, 79.7, 96.809, -116.882, 51.498, 171.547, -8.348], 30)
    time.sleep(1)
    threading.Thread(target=gripper_control, args=(0,)).start()
    for _ in range(3):
        mr.send_angle(3, 120, 30)
        threading.Thread(target=gripper_control, args=(1,)).start()
        time.sleep(0.1)
        mr.send_angle(3, 60, 30)
        time.sleep(0.1)
        threading.Thread(target=gripper_control, args=(0,)).start()
    mr.send_angles([-34.543, 53.734, 64.3, -68.569, 1.254, 119.225, -64.045], 30)


# 创建手部检测器对象
detector = HandDetector(
    detectionCon=0.8,  # 检测置信度阈值（0~1，越高越严格）
    maxHands=2  # 最多检测的手部数量
)

gesture_active = False
number = 0
threading.Thread(target=right_arm_init, args=()).start()
threading.Thread(target=left_arm_init, args=()).start()
time.sleep(2)

while True:
    cap = cv2.VideoCapture(0)
    right_arm_greet()
    time.sleep(2)
    threading.Thread(target=right_arm_init, args=()).start()
    threading.Thread(target=left_arm_init, args=()).start()
    time.sleep(8)
    gesture_detected = False  # 是否本轮识别到手势

    while True:
        success, img = cap.read()
        if not success:
            break

        hands, img = detector.findHands(img)
        cv2.imshow("Hand Tracking", img)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            gesture_detected = False
            break

        if hands:
            for hand in hands:
                fingers = detector.fingersUp(hand)
                print(fingers)

                if fingers == [0, 1, 1, 0, 0]:
                    gesture_detected = True
                    break

        if gesture_detected:
            break

    cap.release()
    cv2.destroyAllWindows()

    if gesture_detected:
        print("开始拍照咯！")
        threading.Thread(target=right_arm_move_in, args=()).start()
        time.sleep(5)
        threading.Thread(target=right_take_photo_position, args=()).start()
        threading.Thread(target=left_take_photo_position, args=()).start()
        time.sleep(3)
        play_countdown_video("countdown.mp4")
        threading.Thread(target=gripper_control, args=(1,)).start()
        time.sleep(1)
        threading.Thread(target=gripper_control, args=(0,)).start()
        time.sleep(1)
        print("拍照成功！")
        play_countdown_video("take_photo.mp4")
        threading.Thread(target=right_arm_move_out, args=()).start()
        time.sleep(8)

    print("准备下一轮手势识别...\n")
    time.sleep(2)

    threading.Thread(target=right_arm_init, args=()).start()
    threading.Thread(target=left_arm_init, args=()).start()


