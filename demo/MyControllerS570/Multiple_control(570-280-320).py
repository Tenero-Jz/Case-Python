import threading
import time

from pymycobot import Mercury, MyArmM, MyCobot
from exoskeleton_api import Exoskeleton

obj = Exoskeleton(port="COM27")
mr = MyArmM("COM5", 1000000)  # 右臂--MyArmM750
my320 = MyCobot("COM29", 115200)
my280 = MyCobot("COM28", 115200)

my320.set_gripper_mode(0)
my320.set_fresh_mode(1)
# def gripper_320(mc, value):
#     mc.set_gripper_value(14, value)


def gripper_280(mc, value):
    mc.set_gripper_value(value, 50)


# 0 左臂，1 右臂
def control_arm(arm):
    angle = 0
    while True:
        if arm == 0:
            arm_data = obj.get_arm_data(1)
            # print("l: ", arm_data)
            # mc = my280  # 左臂--MyCobot280

            mercury_list_280 = [  # 280映射关系
                arm_data[1] + 70, -arm_data[0] - 90, -arm_data[3], arm_data[5],
                arm_data[4], arm_data[6]
            ]
            mercury_list_320 = [  # 320映射关系
                arm_data[1] + 60, -arm_data[0] - 95, -arm_data[3], arm_data[5],
                arm_data[4] + 65, arm_data[6] + 20
            ]

            if arm_data[9] == 0:
                try:
                    value = 0
                    threading.Thread(target=gripper_280, args=(my280, value,)).start()
                    threading.Thread(target=gripper_280, args=(my320, value,)).start()

                except Exception as e:
                    print(f"Warning: Failed to set angle -100. Error: {e}")

            elif arm_data[10] == 0:
                try:
                    value = 100
                    threading.Thread(target=gripper_280, args=(my280, value,)).start()
                    threading.Thread(target=gripper_280, args=(my320, value,)).start()
                except Exception as e:
                    print(f"Warning: Failed to set angle 0. Error: {e}")
            try:
                my280.send_angles(mercury_list_280, 100)
                time.sleep(0.01)
                my320.send_angles(mercury_list_320, 100)
                time.sleep(0.02)
            except:
                pass

        elif arm == 1:
            arm_data = obj.get_arm_data(2)
            print("r: ", arm_data)
            mc = mr
            mercury_list = [
                -arm_data[1] - 75, -arm_data[0], arm_data[3], arm_data[4],
                -arm_data[5] + 50, arm_data[6], angle
            ]
            if arm_data[9] == 0:
                try:
                    angle = -115
                except Exception as e:
                    print(f"Warning: Failed to set angle -100. Error: {e}")

            elif arm_data[10] == 0:
                try:
                    angle = 0
                except Exception as e:
                    print(f"Warning: Failed to set angle 0. Error: {e}")

            try:
                mc.set_joints_angle(mercury_list, 20)
                time.sleep(0.01)
            except:
                pass


# 左臂
threading.Thread(target=control_arm, args=(0,)).start()
# 右臂
threading.Thread(target=control_arm, args=(1,)).start()
