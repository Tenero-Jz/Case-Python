# 实现柠檬识别摘取--采用颜色识别
import sys

import cv2
import numpy as np
import pyrealsense2 as rs
from pymycobot import ElephantRobot
import time
import math

# 相机内参 (请根据你的GEMINI2相机标定数据填写)
CAMERA_INTRINSICS = {
    'fx': 615.0,  # 焦距x
    'fy': 615.0,  # 焦距y
    'cx': 320.0,  # 主点x
    'cy': 240.0  # 主点y
}

# 相机与机械臂的外参（请实际标定）
CAMERA_TO_ARM_TRANSFORM = np.array([
    [1, 0, 0, 0],  # X方向平移（单位：米）
    [0, 1, 0, -0.1],  # Y方向平移
    [0, 0, 1, 0.3],  # Z方向平移
    [0, 0, 0, 1]
])

# 初始化机械臂
mc = ElephantRobot("192.168.10.158", 5001)

res = mc.start_client()
time.sleep(1)
if res is not True:
    sys.exit(1)

mc.set_speed(90)


def init_camera():
    pipeline = rs.pipeline()
    config = rs.config()
    config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
    config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
    profile = pipeline.start(config)
    return pipeline, profile


def get_largest_yellow_blob(frame):
    # 转 HSV
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    # 黄色范围
    lower_yellow = np.array([20, 100, 100])
    upper_yellow = np.array([40, 255, 255])
    mask = cv2.inRange(hsv, lower_yellow, upper_yellow)
    # 形态学操作
    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if contours:
        largest = max(contours, key=cv2.contourArea)
        M = cv2.moments(largest)
        if M["m00"] > 0:
            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"])
            return cx, cy, mask
    return None, None, mask


def pixel_to_camera_coords(x, y, depth, intrinsics):
    Z = depth / 1000.0  # mm -> m
    X = (x - intrinsics['cx']) * Z / intrinsics['fx']
    Y = (y - intrinsics['cy']) * Z / intrinsics['fy']
    return np.array([X, Y, Z, 1])


def transform_to_robot_coords(cam_coords):
    return CAMERA_TO_ARM_TRANSFORM @ cam_coords


def move_to_pick(mc, x, y, z):
    # 将米转换为mm并发送指令
    x, y, z = x * 1000, y * 1000, z * 1000
    print(f"移动到坐标：X={x:.1f}, Y={y:.1f}, Z={z:.1f}")
    mc.write_coords([x, y, z, 0, 0, 0], 50, 1)
    time.sleep(3)


def pick_and_place():
    pipeline, profile = init_camera()
    align = rs.align(rs.stream.color)

    try:
        while True:
            frames = pipeline.wait_for_frames()
            aligned_frames = align.process(frames)
            depth_frame = aligned_frames.get_depth_frame()
            color_frame = aligned_frames.get_color_frame()
            if not depth_frame or not color_frame:
                continue

            color_image = np.asanyarray(color_frame.get_data())
            depth_image = np.asanyarray(depth_frame.get_data())

            cx, cy, mask = get_largest_yellow_blob(color_image)
            if cx is not None:
                # 获取深度
                depth = depth_image[cy, cx]
                if depth == 0:
                    print("深度值无效，跳过")
                    continue

                camera_coords = pixel_to_camera_coords(cx, cy, depth, CAMERA_INTRINSICS)
                robot_coords = transform_to_robot_coords(camera_coords)
                print("机器人坐标:", robot_coords[:3])

                # 移动到目标上方
                move_to_pick(mc, *robot_coords[:3])
                time.sleep(1)
                # 启动夹爪
                mc.set_gripper_state(1, 80)
                time.sleep(1)
                # 抬起
                move_to_pick(mc, robot_coords[0], robot_coords[1], robot_coords[2] + 0.1)
                break

            # 显示画面
            cv2.imshow("Color", color_image)
            cv2.imshow("Mask", mask)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    finally:
        pipeline.stop()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    pick_and_place()




