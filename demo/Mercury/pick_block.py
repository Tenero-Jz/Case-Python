from pymycobot import Mercury
import time

# 初始化左右机械臂
ml = Mercury("/dev/left_arm")
mr = Mercury("/dev/right_arm")

# 设置夹爪速度
ml.set_pro_gripper_speed(14, 100)
mr.set_pro_gripper_speed(14, 100)


# 夹爪控制
def open_gripper(mc):
    mc.set_pro_gripper_angle(14, 100)
    time.sleep(0.5)


def close_gripper(mc):
    mc.set_pro_gripper_angle(14, 10)
    time.sleep(0.5)


# 初始位置
def reset_position():
    open_gripper(ml)
    open_gripper(mr)
    ml.send_angles([13.32, 39.307, -16.858, -89.188, 93.457, 75.075, -88.493], 50)
    mr.send_angles([-8.036, 40.951, 27.408, -85.21, -96.904, 64.702, 93.538], 50)
    time.sleep(1.5)


# 左手抓取并传递给右手
def left_to_right():
    print("左手抓取中...")
    ml.send_base_coord(3, 20, 30)
    time.sleep(3)
    close_gripper(ml)
    time.sleep(0.5)
    print("左手移动到传递位置...")
    ml.send_angles([17.216, 28.991, -11.699, -75.551, 4.308, 110.273, -138.157], 50)
    time.sleep(1.5)
    print("右手移动到传递位置...")
    mr.send_angles([-32.704, 18.819, 41.817, -99.857, -24.138, 126.34, 63.469], 30)
    time.sleep(1.5)
    mr.send_base_coord(2, -60, 20)
    ml.send_coord(3, 90, 20)
    time.sleep(3)
    close_gripper(mr)
    time.sleep(0.5)
    open_gripper(ml)
    time.sleep(0.5)
    print("右手放下...")
    mr.send_angles([-8.036, 40.951, 27.408, -85.21, -96.904, 64.702, 93.538], 50)
    mr.send_base_coord(3, 55, 20)
    time.sleep(1.5)
    open_gripper(mr)
    time.sleep(3)


# 右手抓取并传递给左手
def right_to_left():
    print("右手抓取中...")
    close_gripper(mr)
    time.sleep(0.5)
    print("右手移动到传递位置...")
    mr.send_angles([-32.704, 18.819, 41.817, -99.857, -24.138, 126.34, 63.469], 30)
    time.sleep(2.5)
    mr.send_base_coord(2, -60, 20)
    ml.send_coord(3, 90, 20)
    time.sleep(3)
    close_gripper(ml)
    time.sleep(0.5)
    open_gripper(mr)
    time.sleep(0.5)
    print("左手放下...")
    ml.send_angles([17.216, 28.991, -11.699, -75.551, 4.308, 110.273, -138.157], 50)
    time.sleep(1.5)
    ml.send_angles([13.32, 39.307, -16.858, -89.188, 93.457, 75.075, -88.493], 50)
    time.sleep(3)
    ml.send_base_coord(3, 10, 30)
    time.sleep(3)
    open_gripper(ml)
    time.sleep(3)


# 初始化位置
reset_position()

# 循环抓取流程
while True:
    left_to_right()
    time.sleep(3)
    right_to_left()
    time.sleep(3)
