import threading
from pymycobot import Mercury, ChassisControl, Exoskeleton
import time
import os

os.system("sudo chmod 777 /dev/ttyACM*")

# 初始化设备
obj = Exoskeleton(port="/dev/ttyACM6")
move = ChassisControl(port="/dev/wheeltec_controller")
ml = Mercury("/dev/left_arm")
mr = Mercury("/dev/right_arm")

# 设置模式
ml.set_movement_type(3)
mr.set_movement_type(3)
ml.set_vr_mode(1)
mr.set_vr_mode(1)

for i in range(1, 7):
    ml.set_hand_gripper_speed(i, 80)
    time.sleep(0.5)
    mr.set_hand_gripper_speed(i, 80)
    time.sleep(0.5)

FINGER_ACTIONS = {
    "reset": 0,
    "index_thumb": 1,
    "middle_thumb": 2,
    "index_middle": 3,
    "three_finger": 4,
}

control_mode = {"mode": "gripper"}  # 可为 "gripper" 或 "move"
lock = threading.Lock()

# 全局底盘速度变量
chassis_speed = {"value": 0.3}

# 红色按钮按下次数，左右臂分开计数
red_press_count = {1: 0, 2: 0}

# 定义全局状态变量
last_move_cmd = None
last_rotation_cmd = None
move_lock = threading.Lock()


def set_screen_text(number):
    obj.set_atom_matrix(number)


def control_fingers(mc, pose):
    global size
    if pose in [0, 1, 2, 3]:
        size = 5
    elif pose == 4:
        size = 20
    mc.set_hand_gripper_pinch_action_speed_consort(pose, size)


def jointlimit(angles):
    max_angles = [165, 120, 175, 0, 175, 180, 175]
    min_angles = [-165, -50, -175, -175, -175, 60, -175]
    for i in range(7):
        angles[i] = max(min(angles[i], max_angles[i]), min_angles[i])


def move_chassis(x, y):
    global last_move_cmd

    with move_lock:
        direction = "stop"

        if y < 40 and 90 < x < 120:
            direction = 'forward'
        elif y > 238 and 100 < x < 150:
            direction = 'backward'
        elif x > 240 and 120 < y < 140:
            direction = 'left'
        elif x < 40 and 120 < y < 150:
            direction = 'right'

        if direction != last_move_cmd:
            last_move_cmd = direction
            if direction == 'forward':
                move.go_straight(0.25)
            elif direction == 'backward':
                move.go_back(-0.25)
            elif direction == 'left':
                move.turn_left(0.25)
            elif direction == 'right':
                move.turn_right(-0.25)
            else:
                move.stop()


def control_arm(arm_id):
    while True:
        try:
            if arm_id == 1:
                arm_data = obj.get_arm_data(1)
                mc = ml
                number = 1
                mercury_list = [
                    arm_data[0], -arm_data[1]+10, arm_data[2],
                    -arm_data[3], arm_data[4], 135 + arm_data[5], arm_data[6] - 20
                ]
            elif arm_id == 2:
                arm_data = obj.get_arm_data(2)
                mc = mr
                number = 2
                mercury_list = [
                    arm_data[0], -arm_data[1]+10, arm_data[2],
                    -arm_data[3], arm_data[4], 135 + arm_data[5], arm_data[6] + 20
                ]
            else:
                raise ValueError("Unknown arm id")

            jointlimit(mercury_list)

            atom_pressed = arm_data[7] == 0
            x, y = arm_data[11], arm_data[12]
            red_btn = arm_data[9]
            blue_btn = arm_data[10]

            # 模式切换
            with lock:
                if arm_id == 1 and atom_pressed:
                    control_mode["mode"] = "gripper"
                    print("模式切换：夹爪控制")
                    time.sleep(0.2)
                elif arm_id == 2 and atom_pressed:
                    control_mode["mode"] = "move"
                    print("模式切换：移动控制")
                    time.sleep(0.2)

            mode = control_mode["mode"]

            if mode == "gripper":
                if red_btn == 0:
                    with lock:
                        pose = red_press_count[arm_id]
                        red_press_count[arm_id] += 1
                        if red_press_count[arm_id] > 3:
                            red_press_count[arm_id] = 0
                    threading.Thread(target=control_fingers, args=(mc, pose)).start()
                    threading.Thread(target=set_screen_text, args=(number,)).start()
                    time.sleep(0.2)  # 防抖，稍延长以防止快速多次触发

                elif blue_btn == 0:
                    # 蓝色按钮仍可用于三指抓取
                    threading.Thread(target=control_fingers, args=(mc, 4)).start()
                    threading.Thread(target=set_screen_text, args=(number,)).start()
                    time.sleep(0.2)  # 防抖

                elif blue_btn == 0 and red_btn == 0:
                    time.sleep(0.2)
                    continue

            elif mode == "move":
                move_chassis(x, y)
                if blue_btn == 0 and red_btn == 0:
                    time.sleep(0.2)
                    continue

            mc.send_angles(mercury_list, 10, _async=True)
            time.sleep(0.01)

        except Exception as e:
            print(f"Error in control_arm({arm_id}):", e)
            time.sleep(0.1)


# 启动线程
threading.Thread(target=control_arm, args=(1,), daemon=True).start()
threading.Thread(target=control_arm, args=(2,), daemon=True).start()

# 保持主线程活跃
while True:
    time.sleep(1)
