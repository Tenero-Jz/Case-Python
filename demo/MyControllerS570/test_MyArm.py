import threading
import time

from pymycobot import Mercury, MyArmM
from exoskeleton_api import Exoskeleton

obj = Exoskeleton(port="COM37")
# ml = MyArmM("COM7", 1000000)
mr = MyArmM("COM36", 1000000)


def jointlimit(angles):
    max = [160, 80, 80, 140, 80, 140, 0]
    min = [-160, -70, -70, -150, -90, -150, -115]
    for i in range(7):
        if angles[i] > max[i]:
            angles[i] = max[i]
        if angles[i] < min[i]:
            angles[i] = min[i]


def l_open():
    mr.set_joint_angle(7, -100, 100)


def l_close():
    mr.set_joint_angle(7, 0, 100)


def r_open():
    mr.set_joint_angle(7, -100, 100)


def r_close():
    mr.set_joint_angle(7, 0, 100)


# 0 左臂，1 右臂
def control_arm(arm):
    angle = 0
    while True:
        if arm == 0:
            arm_data = obj.get_arm_data(1)
            print("l: ", arm_data)
            mc = ml

            mercury_list = [
                arm_data[1]+60, arm_data[0], 54.21, arm_data[4],
                -arm_data[5]-40, arm_data[6], angle
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

        elif arm == 1:
            arm_data = obj.get_arm_data(2)
            print("r: ", arm_data)
            mc = mr

            mercury_list = [
                -arm_data[1] - 65, arm_data[0]-20, arm_data[3], arm_data[4], -arm_data[5]+20, arm_data[6], angle
            ]
            jointlimit(mercury_list)
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
# threading.Thread(target=control_arm, args=(0,)).start()
# 右臂
threading.Thread(target=control_arm, args=(1,)).start()
