import threading
from pymycobot.mybuddy import MyBuddy
from exoskeleton_api import exoskeleton

obj = exoskeleton(port="/dev/ttyACM3")

mb = MyBuddy("/dev/ttyACM0", debug=False)
mb.power_on()
# 设置双臂为速度融合模式
mb.set_movement_type(0, 2)


# 1 左臂，2 右臂
def control_arm(arm):
    while True:
        if arm == 1:
            arm_data = obj.get_data(0)
            print("l: ", arm_data)
            mercury_list = [arm_data[0] - 90, -arm_data[1], arm_data[3], -arm_data[5], arm_data[4], arm_data[6]]

        elif arm == 2:
            arm_data = obj.get_data(1)
            print("r: ", arm_data)
            mercury_list = [arm_data[0] + 90, arm_data[1], -arm_data[3], arm_data[5], arm_data[4], arm_data[6]]

        else:
            raise ValueError("error arm")
        mb.send_angles(arm, mercury_list, 100)


# 左臂
threading.Thread(target=control_arm, args=(1,)).start()
# 右臂
threading.Thread(target=control_arm, args=(2, )).start()
