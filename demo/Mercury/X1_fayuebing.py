from pymycobot import Mercury
import time

# 初始化左右机械臂
ml = Mercury("/dev/left_arm")
mr = Mercury("/dev/right_arm")


# say_hello
def say_hello():
    for i in range(3):
        mr.send_angles([-29.312, 44.958, 129.328, -91.586, 9.249, 177.464, 51.979], 30)
        time.sleep(0.1)
        mr.send_angles([-32.391, 45.511, 80.957, -111.357, 9.166, 177.385, 51.978], 30)
        time.sleep(0.1)


# 初始姿态
def init_pose():
    ml.send_angles([99.241, 79.194, -112.122, -121.461, 0.185, 185.001, 122.42], 50)
    time.sleep(2)
    mr.send_angles([-23.652, 14.688, 0.805, -89.993, 12.994, 139.737, -81.747], 20)


def control_gripper(mode):
    mr.set_pro_gripper_torque(14, 100)
    if mode == 1:
        mr.set_pro_gripper_angle(14, 50)
    else:
        mr.set_pro_gripper_angle(14, 0)


# 第一个月饼位置
def one_pie_1():
    mr.send_base_coord(2, 0, 50)
    time.sleep(3)


def one_pie_2():
    mr.send_angles([-17.772, 49.623, 0.648, -67.629, 14.811, 157.626, -81.708], 10)
    time.sleep(1)
    mr.send_angles([-11.309, 59.437, 1.036, -43.977, 14.82, 157.63, -81.708], 10)
    time.sleep(1)
    mr.send_angles([4.362, 40.374, 1.039, -43.977, 14.815, 157.63, -81.708], 10)
    time.sleep(1)


# 第二个月饼位置
def two_pie_1():
    mr.send_angles([-24.929, 45.245, 1.294, -84.607, -19.192, 167.083, -81.684], 10)
    time.sleep(3)


def two_pie_2():
    mr.send_angles([-17.727, 41.93, 1.329, -82.288, -19.207, 167.082, -81.684], 10)
    time.sleep(1)
    mr.send_angles([-8.488, 53.209, 1.551, -60.686, -19.211, 167.115, -81.673], 10)
    time.sleep(1)
    mr.send_angles([4.362, 40.374, 1.039, -43.977, 14.815, 157.63, -81.708], 10)
    time.sleep(1)


# 第三个月饼位置
def three_pie_1():
    mr.send_angles([-30.339, 47.31, 1.458, -89.97, -8.081, 164.485, -73.113], 10)
    time.sleep(3)


def three_pie_2():
    mr.send_angles([-21.052, 39.903, 1.815, -82.055, -22.701, 147.889, -58.865], 10)
    time.sleep(1)
    mr.send_angles([-13.627, 44.488, 1.821, -72.256, -18.211, 160.064, -58.804], 10)
    mr.send_angles([4.362, 40.374, 1.039, -43.977, 14.815, 157.63, -81.708], 10)
    time.sleep(1)


# 主函数
if __name__ == '__main__':
    # 夹第一个月饼
    say_hello()
    # time.sleep(1)
    # init_pose()
    # time.sleep(2)
    # control_gripper(1)
    # time.sleep(1)
    # one_pie_1()
    # control_gripper(2)
    # time.sleep(1)
    # one_pie_2()
    # time.sleep(1)
    # control_gripper(1)
    # time.sleep(1)
    # # 夹第二个月饼
    # say_hello()
    # time.sleep(1)
    # init_pose()
    # time.sleep(2)
    # two_pie_1()
    # control_gripper(2)
    # time.sleep(1)
    # two_pie_2()
    # control_gripper(1)
    # time.sleep(1)
    # # 夹第三个月饼
    # say_hello()
    # time.sleep(1)
    # init_pose()
    # time.sleep(2)
    # three_pie_1()
    # control_gripper(2)
    # time.sleep(1)
    # three_pie_2()
    # control_gripper(1)
    # time.sleep(1)

