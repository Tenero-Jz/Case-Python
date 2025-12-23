import os
import threading
import time
from pymycobot import MyAGVPro, Exoskeleton, Mercury
from pymycobot.utils import get_port_list

# 设置权限
os.system("sudo chmod 777 /dev/ttyACM*")

# 实例化设备
agv_pro = MyAGVPro("/dev/ttyACM0", baudrate=1000000, debug=False)
exo_controller = Exoskeleton(port="/dev/ttyACM2")
left_arm = Mercury("/dev/left_arm")
right_arm = Mercury("/dev/right_arm")

# 设置双臂为速度融合模式
for arm in [left_arm, right_arm]:
    arm.set_movement_type(3)
    arm.set_vr_mode(1)
    arm.set_pro_gripper_speed(14, 50)

# 全局状态变量及互斥锁
last_move_cmd = None
last_rotation_cmd = None
move_lock = threading.Lock()


def control_gripper(arm, angle):
    if arm == 1:
        left_arm.set_pro_gripper_angle(14, angle)
    elif arm == 2:
        right_arm.set_pro_gripper_angle(14, angle)
    else:
        raise ValueError("Invalid arm identifier")


def handle_gripper_buttons(arm, red_btn, blue_btn):
    if red_btn == 0:
        threading.Thread(target=control_gripper, args=(arm, 100)).start()
    elif blue_btn == 0:
        threading.Thread(target=control_gripper, args=(arm, 0)).start()


def move(x, y):
    global last_move_cmd
    with move_lock:
        if y < 50 and last_move_cmd != 'forward':
            agv_pro.move_forward(0.2)
            last_move_cmd = 'forward'
        elif y > 200 and last_move_cmd != 'backward':
            agv_pro.move_backward(0.2)
            last_move_cmd = 'backward'
        elif x > 200 and last_move_cmd != 'left':
            agv_pro.move_left_lateral(0.2)
            last_move_cmd = 'left'
        elif x < 50 and last_move_cmd != 'right':
            agv_pro.move_right_lateral(0.2)
            last_move_cmd = 'right'
        elif 50 < y < 200 and 50 < x < 200 and last_move_cmd != 'stop':
            agv_pro.stop()
            last_move_cmd = 'stop'


def stop():
    global last_move_cmd
    with move_lock:
        if last_move_cmd != 'stop':
            agv_pro.stop()
            last_move_cmd = 'stop'


def rotation(x):
    global last_rotation_cmd
    with move_lock:
        if x > 200 and last_rotation_cmd != 'left':
            agv_pro.turn_right(0.35)
            last_rotation_cmd = 'left'
        elif x < 50 and last_rotation_cmd != 'right':
            agv_pro.turn_left(0.35)
            last_rotation_cmd = 'right'
        elif 50 < x < 200 and last_rotation_cmd != 'stop':
            agv_pro.stop()
            last_rotation_cmd = 'stop'


def control_arm(arm):
    controller = left_arm if arm == 1 else right_arm

    while True:
        try:
            data = exo_controller.get_arm_data(arm)
            x, y = data[11], data[12]

            if arm == 1:
                move(x, y)
            elif arm == 2:
                rotation(x)

            angles = [
                data[0], -data[1], -data[3], data[4],
                135 + data[5], data[6] - 30
            ]

            red_btn = data[9]
            blue_btn = data[10]
            atom_btn = data[7]

            handle_gripper_buttons(arm, red_btn, blue_btn)

            # 红蓝按钮同时按下（举升或下降）
            if red_btn == 0 and blue_btn == 0:
                time.sleep(0.01)
                continue

            # atom 按钮按下时控制头部运动
            if atom_btn == 0:
                continue

            controller.send_angles(angles, 10, _async=True)
            time.sleep(0.01)

        except Exception as e:
            print(f"Error in control_arm({arm}): {e}")
            time.sleep(0.1)


def main():
    # 启动控制线程
    threading.Thread(target=control_arm, args=(1,)).start()  # 左臂
    threading.Thread(target=control_arm, args=(2,)).start()  # 右臂

    while True:
        time.sleep(1)


if __name__ == "__main__":
    main()
