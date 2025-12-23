import time
import threading
from pymycobot import *
import cv2
import numpy as np
import sys


class Logger(object):
    def __init__(self, filename="Aging.log"):
        self.terminal = sys.stdout
        self.log = open(filename, "a", encoding="utf-8")

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)

    def flush(self):
        self.terminal.flush()
        self.log.flush()


sys.stdout = Logger("Aging.log")
print("系统启动，所有输出将同时写入 Aging.log\n")


def arm_motion_loop(robot, angles_list):
    while True:
        for ang in angles_list:
            robot.send_angles(ang, 50)
            time.sleep(2.8)


my = Mercury("/dev/ttyUSB0", 1000000)

angles = [
    [0, 0, 0, 0, 0, 0, 0],
    [30, 0, 40, 0, 0, 0, 0],
    [35, -1, 48, 90, -3, 92, -70],
    [5, -38, 4, 78, -6, 71, -70],
    [5, -1, 4, 90, -3, 9, 0],
]

arm_thread = threading.Thread(target=arm_motion_loop, args=(my, angles), daemon=True)
arm_thread.start()


def open_camera():
    gst = (
        "v4l2src device=/dev/video4 ! "
        "image/jpeg,width=640,height=480,framerate=30/1 ! "
        "jpegdec ! videoconvert ! video/x-raw,format=BGR ! appsink"
    )

    cap = cv2.VideoCapture(gst, cv2.CAP_GSTREAMER)
    return cap


cap = open_camera()

lower_green = np.array([35, 60, 60])
upper_green = np.array([85, 255, 255])

green_count = 0
detected = False
retry_count = 0

print("系统已启动：摄像头实时检测 + 机械臂后台自动运动")

while True:

    ret, frame = cap.read()

    if not ret:
        print("警告：摄像头帧读取失败，正在重连...")
        cap.release()
        time.sleep(1)
        cap = open_camera()
        retry_count += 1

        if retry_count >= 5:
            print("摄像头重连次数过多，继续尝试中...")
            retry_count = 0
        continue
    else:
        retry_count = 0  # 成功读取帧后清零

    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, lower_green, upper_green)

    mask = cv2.erode(mask, None, iterations=2)
    mask = cv2.dilate(mask, None, iterations=2)

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    found_green = False

    for cnt in contours:
        if cv2.contourArea(cnt) < 500:
            continue

        found_green = True

        x, y, w, h = cv2.boundingRect(cnt)
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv2.putText(frame, "Green Block", (x, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

    if found_green and not detected:
        green_count += 1
        detected = True
        current_time = time.strftime("%Y年%m月%d日_%H:%M:%S", time.localtime())
        print(f"{current_time}，第 {green_count} 次检测到绿色木块")

    if not found_green:
        detected = False

    cv2.imshow("Frame", frame)
    cv2.imshow("Mask", mask)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
