import time
import threading
from pymycobot import Pro450Client, Mercury, Pro630, Mercury


# 初始化两台机械臂
mc1 = Pro450Client("127.0.0.1", 4500)  # 第一台 Pro450
mc2 = Pro630("/dev/ttyACM0")  # 第二台 Pro450，请替换端口

# 吸泵控制（针对第一台）
# suck = Mercury("/dev/ttyACM1", debug=False)


# 夹爪控制（针对第一台）
def open_gripper():
    mc1.set_digital_output(5, 0)
    time.sleep(0.5)
    mc1.set_digital_output(6, 1)


def close_gripper():
    mc1.set_digital_output(5, 1)
    time.sleep(0.5)
    mc1.set_digital_output(6, 0)


# # 吸泵控制
# def open_sucker():
#     suck.set_base_io_output(1, 1)
#
#
# def close_sucker():
#     suck.set_base_io_output(1, 0)


# 同步控制两台机械臂的角度
def send_angles_sync(angles, speed):
    # 构造第二台机械臂用的角度列表，第5个关节偏移-90°
    angles_mc2 = angles.copy()
    angles_mc2[4] = angles_mc2[4] - 90  # 第5关节补偿
    # 创建并启动两个线程
    # t1 = threading.Thread(target=mc1.send_angles, args=(angles, speed))
    t2 = threading.Thread(target=mc2.send_angles, args=(angles_mc2, speed))
    # t1.start()
    t2.start()
    # t1.join()
    t2.join()


while True:
    print("\n=====输入1：控制两台机械臂跳舞=====")
    print("=====输入2：控制第一台机械臂1、2关节运动=====")
    print("=====输入3：控制第一台机械臂矩形平移=====")
    print("=====输入4：开吸泵=====")
    print("=====输入5：关吸泵=====")
    print("=====输入6：开夹爪=====")
    print("=====输入7：关夹爪=====")
    number = input("请输入数字：")

    if number == "1":
        send_angles_sync([0, 0, 0, 0, 0, 0], 60)
        time.sleep(1)

        send_angles_sync([87.66, -1.02, 1.43, 3.49, -95.87, 0.0], 90)
        time.sleep(1)

        for i in range(5):
            send_angles_sync([87.66, 54.32, -97.66, 42.42, -97.03, 0.0], 90)
            time.sleep(0.7)
            send_angles_sync([87.65, -53.73, 102.78, -44.49, -97.29, 0.0], 90)
            time.sleep(0.7)
            send_angles_sync([87.66, 54.32, -97.66, 42.42, 10, 0.0], 90)
            time.sleep(0.7)
            send_angles_sync([87.65, -53.73, 102.78, -44.49, -170, 0.0], 90)
            time.sleep(0.7)

        send_angles_sync([0, 0, 0, 0, 0, 0], 60)
        time.sleep(1)

    elif number == "2":
        for i in range(3):
            mc1.send_angles([0, 0, 0, 0, 0, 0], 50)
            time.sleep(1)
            mc1.send_angles([90, -90, 0, 0, 0, 0], 40)
            time.sleep(1.5)
            mc1.send_angles([90, 90, 0, 0, 0, 0], 40)
            time.sleep(1.5)
        mc1.send_angles([0, 0, 0, 0, 0, 0], 50)
        time.sleep(1)

    elif number == "3":
        mc1.send_angles([0, 0, -90, 0, 0, 0], 40)
        time.sleep(1)
        for i in range(3):
            mc1.send_angles([-2.59, -35.38, -126.93, 73.08, 0.0, 0.0], 10)
            time.sleep(1)
            mc1.send_angles([-1.78, -64.24, -56.67, 30.0, 0.0, 0.0], 10)
            time.sleep(1)
            mc1.send_angles([31.9, -36.31, -56.16, 4.2, 0.32, 0.01], 10)
            time.sleep(1)
            mc1.send_angles([53.9, 23.13, -124.13, 10.53, 0.28, 0.01], 10)
            time.sleep(1)
        mc1.send_angles([0, 0, 0, 0, 0, 0], 50)
        time.sleep(1)

    elif number == "4":
        open_sucker()
    elif number == "5":
        close_sucker()
    elif number == "6":
        open_gripper()
    elif number == "7":
        close_gripper()
    else:
        print("无效输入，请输入 1 、2 、3 、 4 、 5 、 6 、 7")
