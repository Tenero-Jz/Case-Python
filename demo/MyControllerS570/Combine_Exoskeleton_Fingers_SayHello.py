import threading
import time
import os
from pymycobot import Mercury, ChassisControl, Exoskeleton

# 提升串口权限
os.system("sudo chmod 777 /dev/ttyACM*")

# 初始化设备
obj = Exoskeleton(port="/dev/ttyACM4")
move = ChassisControl(port="/dev/wheeltec_controller")
ml = Mercury("/dev/left_arm")
mr = Mercury("/dev/right_arm")
lock = threading.Lock()
# 设置模式
ml.set_movement_type(3)
mr.set_movement_type(3)
ml.set_vr_mode(1)
mr.set_vr_mode(1)

for i in range(1, 7):
    ml.set_hand_gripper_speed(i, 80)
    time.sleep(0.1)
    mr.set_hand_gripper_speed(i, 80)
    time.sleep(0.1)

# 控制状态变量
control_mode = {"mode": "gripper"}  # 可为 "gripper" 或 "move"
current_mode = {"mode": "none"}  # 'none', 'code1', 'code2'
gripper_size = {1: 5, 2: 5}  # 1 左臂，2 右臂
mode_lock = threading.Lock()
red_press_count = {1: 0, 2: 0}

FINGER_ACTIONS = {
    "reset": 0,
    "index_thumb": 1,
    "middle_thumb": 2,
    "index_middle": 3,
    "three_finger": 4,
}


def set_screen_text(number):
    obj.set_atom_matrix(number)


def control_fingers(mc, pose):
    mc.set_hand_gripper_pinch_action_speed_consort(pose, 5)
    time.sleep(0.1)


def control_finger(mc, size):
    mc.set_hand_gripper_pinch_action_speed_consort(4, size)
    time.sleep(0.1)


def adjust_gripper_size(arm_id, y):
    with lock:
        current_size = gripper_size[arm_id]
        if y < 50:
            if current_size < 20:
                gripper_size[arm_id] = min(current_size + 5, 20)
                print(f"增大夹爪[{arm_id}]：{gripper_size[arm_id]}")
            else:
                print(f"夹爪[{arm_id}] 已达到最大开合")
        elif y > 230:
            if current_size > 1:
                gripper_size[arm_id] = max(current_size - 5, 1)
                print(f"减小夹爪[{arm_id}]：{gripper_size[arm_id]}")
            else:
                print(f"夹爪[{arm_id}] 已达到最小开合")
        else:
            print(f"夹爪[{arm_id}]：y={y} 未触发增减条件")


def jointlimit(angles):
    max_angles = [165, 120, 175, 0, 175, 180, 175]
    min_angles = [-165, -50, -175, -175, -175, 60, -175]
    for i in range(7):
        angles[i] = max(min(angles[i], max_angles[i]), min_angles[i])


def move_chassis(x, y):
    if y < 40:
        move.go_straight(0.3)
    elif y > 238:
        move.go_back(-0.3)
    elif x > 240:
        move.turn_left(0.3)
    elif x < 40:
        move.turn_right(-0.3)
    else:
        move.stop()


def code1(arm_id):
    global MAX_GRIPPER_SIZE, MIN_GRIPPER_SIZE
    while True:
        with mode_lock:
            if current_mode["mode"] != "code1":
                break
        try:
            if arm_id == 1:
                arm_data = obj.get_arm_data(1)
                mc = ml
                number = 1
                mercury_list = [
                    arm_data[0], -arm_data[1] + 10, arm_data[2],
                    -arm_data[3], arm_data[4], 135 + arm_data[5], arm_data[6] - 20
                ]
            elif arm_id == 2:
                arm_data = obj.get_arm_data(2)
                mc = mr
                number = 2
                mercury_list = [
                    arm_data[0], -arm_data[1] + 10, arm_data[2],
                    -arm_data[3], arm_data[4], 135 + arm_data[5], arm_data[6] + 20
                ]
            else:
                raise ValueError("Unknown arm id")
            jointlimit(mercury_list)
            x, y = arm_data[11], arm_data[12]
            red_btn = arm_data[9]
            blue_btn = arm_data[10]
            atom_pressed = arm_data[7] == 0

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
                MAX_GRIPPER_SIZE = 20
                MIN_GRIPPER_SIZE = 0
                if red_btn == 0:
                    with lock:
                        pose = red_press_count[arm_id]
                        red_press_count[arm_id] += 1
                        if red_press_count[arm_id] > 3:
                            red_press_count[arm_id] = 0
                    threading.Thread(target=control_fingers, args=(mc, pose)).start()
                    time.sleep(0.1)
                    # threading.Thread(target=set_screen_text, args=(number,)).start()
                    # time.sleep(0.01)  # 防抖，稍延长以防止快速多次触发

                elif blue_btn == 0:
                    threading.Thread(target=adjust_gripper_size, args=(arm_id, y)).start()
                    time.sleep(0.1)
                    # 发送当前夹爪角度
                    threading.Thread(target=control_finger, args=(mc, gripper_size[arm_id])).start()
                    time.sleep(0.1)

                elif blue_btn == 0 and red_btn == 0:
                    time.sleep(0.02)
                    continue

            elif mode == "move":
                threading.Thread(target=move_chassis, args=(x, y,)).start()
                if blue_btn == 0 and red_btn == 0:
                    time.sleep(0.2)
                    continue

            mc.send_angles(mercury_list, 10, _async=True)
            time.sleep(0.01)

        except Exception as e:
            print(f"Error in control_arm({arm_id}):", e)
            time.sleep(0.1)


def code2():
    try:
        # 初始化手爪角度
        for i in range(1, 5):
            mr.set_hand_gripper_angle(i, 0)
            time.sleep(0.1)
        mr.set_hand_gripper_angle(6, 30)
        time.sleep(0.1)
        mr.set_hand_gripper_angle(5, 40)
        time.sleep(0.1)

        ml.set_hand_gripper_angle(1, 0)
        time.sleep(0.1)
        ml.set_hand_gripper_angle(4, 0)
        time.sleep(0.1)
        ml.set_hand_gripper_angle(2, 100)
        time.sleep(0.1)
        ml.set_hand_gripper_angle(3, 100)
        time.sleep(0.1)
        ml.set_hand_gripper_angle(5, 60)
        time.sleep(0.1)
        ml.set_hand_gripper_angle(6, 90)
        time.sleep(0.1)

        left_pose = [7.468, 25.816, -13.513, -65.267, 12.673, 141.074, -8.023]
        for joint, angle in enumerate(left_pose, start=1):
            ml.send_angle(joint, angle, 20)
            time.sleep(0.1)

        init_pose = [-10.297, 58.307, 83.722, -103.229, -80, 171.277, -82.914]
        joint_order = [7, 6, 5, 1, 2, 3, 4]
        for joint in joint_order:
            mr.send_angle(joint, init_pose[joint - 1], 20)
            time.sleep(0.1)

        while True:
            with mode_lock:
                if current_mode["mode"] != "code2":
                    break
            mr.send_angle(3, 50, 25)
            time.sleep(0.3)
            mr.send_angle(3, 100, 25)
            time.sleep(0.3)
    except Exception as e:
        print("[错误] code2:", e)


def button_monitor():
    while True:
        try:
            left = ml.is_btn_clicked()
            right = mr.is_btn_clicked()
            # print("right", right, ",left", left)
            with mode_lock:
                if left == 1:
                    print("[切换] -> code1")
                    current_mode["mode"] = "none"  # 通知其他线程停止
                    time.sleep(0.2)  # 等待旧线程响应退出
                    current_mode["mode"] = "code1"
                    threading.Thread(target=code1, args=(1,), daemon=True).start()
                    threading.Thread(target=code1, args=(2,), daemon=True).start()

                elif right == 1:
                    print("[切换] -> code2")
                    current_mode["mode"] = "none"  # 通知其他线程停止
                    time.sleep(0.2)  # 等待旧线程响应退出
                    current_mode["mode"] = "code2"
                    threading.Thread(target=code2, daemon=True).start()

            time.sleep(0.1)
        except Exception as e:
            print("[错误] button_monitor:", e)
            time.sleep(0.5)


# 启动按钮监听
button_monitor()
