import time
import threading
from pymycobot import MyArmMControl

# 初始化三台机械臂
robot1 = MyArmMControl("COM36", 1000000)
robot2 = MyArmMControl("COM39", 1000000)
robot3 = MyArmMControl("COM32", 1000000)


# 定义每台机械臂的动作逻辑
def run_motion(robot):
    robot.write_coords([319.7, -52.4, 200, -175.66, -0.81, 174.5], 30)
    time.sleep(2)
    robot.write_coords([419.7, -52.4, 200, -175.66, -0.81, 174.5], 30)
    time.sleep(2)

    robot.write_coord(2, -270, 100)
    time.sleep(4)
    robot.set_gripper_value(100, 50)
    time.sleep(1)
    robot.write_coord(3, 10, 100)
    time.sleep(6)
    robot.set_gripper_value(30, 50)
    time.sleep(1)

    robot.write_coords([419.7, -52.4, 200, -175.66, -0.81, 174.5], 30)
    time.sleep(3)

    # robot.write_coord(2, 170, 100)
    # time.sleep(6)
    # robot.write_coord(3, 10, 100)
    # time.sleep(6)
    # robot.set_gripper_value(100, 50)
    # time.sleep(1)
    #
    # robot.set_gripper_value(30, 50)
    # time.sleep(1)

    # robot.write_coords([319.7, -52.4, 200, -175.66, -0.81, 174.5], 30)
    # time.sleep(3)

    robot.write_coord(1, 550, 100)
    time.sleep(6)
    # robot.write_coords([355.9, -50.1, 10, -176.32, -2.28, 174.47], 30)
    # time.sleep(3)
    robot.set_gripper_value(100, 50)
    time.sleep(1)
    # robot.write_coord(3, 200, 100)
    # time.sleep(6)
    robot.write_coords([319.7, -52.4, 200, -175.66, -0.81, 174.5], 30)
    time.sleep(3)


# 创建线程
t1 = threading.Thread(target=run_motion, args=(robot1,))
t2 = threading.Thread(target=run_motion, args=(robot2,))
t3 = threading.Thread(target=run_motion, args=(robot3,))

# 启动线程
t1.start()
time.sleep(0.01)
t2.start()
time.sleep(0.01)
t3.start()
time.sleep(0.01)

# 等待线程结束
t1.join()
t2.join()
t3.join()

# print("所有机械臂动作完成")
