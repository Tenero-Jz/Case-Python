import threading
import time
import os
from pymycobot import Mercury, Exoskeleton
# from exoskeleton_api import exoskeleton

os.system("sudo chmod 777 /dev/ttyACM*")
obj = Exoskeleton(port="/dev/ttyACM4")
ml = Mercury("/dev/left_arm")
mr = Mercury("/dev/right_arm")

# 设置双臂为速度融合模式
ml.set_movement_type(3)
mr.set_movement_type(3)
# 设置夹爪运行模式
ml.set_gripper_mode(0)
mr.set_gripper_mode(0)


# 0 左臂，1 右臂
def control_arm(arm):
    while True:
        if arm == 0:
            arm_data = obj.get_arm_data(1)
            print("l: ", arm_data)
            mc = ml
        elif arm == 1:
            arm_data = obj.get_arm_data(2)
            print("r: ", arm_data)
            mc = mr
        else:
            raise ValueError("error arm")
        mercury_list = [
            arm_data[0], -arm_data[1], arm_data[2], -arm_data[3], arm_data[4],
            135 + arm_data[5], arm_data[6]
        ]
        # if arm_data[7] == 0:
        #     mc.set_gripper_state(1, 100)
        # elif arm_data[8] == 0:
        #     mc.set_gripper_state(0, 100)

        mc.send_angles(mercury_list, 10)
        time.sleep(0.01)


# 左臂
threading.Thread(target=control_arm, args=(1, )).start()
# 右臂
threading.Thread(target=control_arm, args=(2, )).start()