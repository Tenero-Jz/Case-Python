import os
import threading
import time
import socket
import serial
from pymycobot import *
from pymycobot.utils import get_port_list
import dmmotordrive

# ---------------- 初始化 ---------------- #
os.system("sudo chmod 777 /dev/ttyACM*")
obj = Exoskeleton(port="/dev/ttyACM2")
ml = dmmotordrive.DMMotorDrive("/dev/ttyACM1")
mr = dmmotordrive.DMMotorDrive("/dev/ttyACM2")
body = dmmotordrive.SD100("/dev/ttyACM3")
body.set_pos(1, 10)

# ---------------- Socket连接到AGV板（JN2） ---------------- #
agv_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
agv_client.connect(("192.168.10.2", 9999))  # 改成 JN板2 的 IP


def send_to_agv(command: str):
    try:
        agv_client.send(command.encode())
    except Exception as e:
        print(f"[ERROR] 发送AGV指令失败: {e}")


# ---------------- 力控夹爪 ---------------- #
# def control_gripper(arm, angle):
#     if arm == 1:
#         ml.set_pro_gripper_angle(14, angle)
#     elif arm == 2:
#         mr.set_pro_gripper_angle(14, angle)


# ---------------- 全局变量 ---------------- #
last_move_cmd = None
last_rotation_cmd = None
move_lock = threading.Lock()
body_height = 10
body_height_lock = threading.Lock()


# ---------------- 控制AGV移动 ---------------- #
def move(x, y):
    global last_move_cmd
    with move_lock:
        if y < 50 and last_move_cmd != 'forward':
            send_to_agv("forward")
            last_move_cmd = 'forward'
        elif y > 200 and last_move_cmd != 'backward':
            send_to_agv("backward")
            last_move_cmd = 'backward'
        elif x > 200 and last_move_cmd != 'left':
            send_to_agv("left")
            last_move_cmd = 'left'
        elif x < 50 and last_move_cmd != 'right':
            send_to_agv("right")
            last_move_cmd = 'right'
        elif 50 < x < 200 and 50 < y < 200 and last_move_cmd != 'stop':
            send_to_agv("stop")
            last_move_cmd = 'stop'


def rotation(x):
    global last_rotation_cmd
    with move_lock:
        if x > 200 and last_rotation_cmd != 'left':
            send_to_agv("turn_right")
            last_rotation_cmd = 'left'
        elif x < 50 and last_rotation_cmd != 'right':
            send_to_agv("turn_left")
            last_rotation_cmd = 'right'
        elif 50 < x < 200 and last_rotation_cmd != 'stop':
            send_to_agv("stop")
            last_rotation_cmd = 'stop'


# ---------------- 控制身体升降 ---------------- #
def control_body(i):
    body.set_pos(1, i)


def adjust_body_height(arm):
    global body_height
    step = -1 if arm == 1 else 1
    while True:
        with body_height_lock:
            new_height = max(0, min(150, body_height + step))
            if new_height != body_height:
                body_height = new_height
                control_body(body_height)


# ---------------- 控制头部运动 ---------------- #
def head_move(arm):
    if arm == 1:
        mr.send_angle(7, 50, 50)
        time.sleep(1)
        mr.send_angle(7, 0, 50)
    elif arm == 2:
        mr.send_angle(7, -50, 50)
        time.sleep(1)
        mr.send_angle(7, 0, 50)


# ---------------- 控制手臂 ---------------- #
def control_arm(arm):
    speeds = [50] * 6
    while True:
        arm_data = obj.get_arm_data(arm)
        x, y = arm_data[11], arm_data[12]
        mc = ml if arm == 1 else mr

        if arm == 1:
            threading.Thread(target=move, args=(x, y)).start()
        elif arm == 2:
            threading.Thread(target=rotation, args=(x,)).start()

        mercury_list = [
            arm_data[0], -arm_data[1], -arm_data[3], arm_data[4],
            135 + arm_data[5], arm_data[6] - 30
        ]

        red_btn, blue_btn, atom_btn = arm_data[9], arm_data[10], arm_data[7]

        # if red_btn == 0:
        #     threading.Thread(target=control_gripper, args=(arm, 100)).start()
        # elif blue_btn == 0:
        #     threading.Thread(target=control_gripper, args=(arm, 0)).start()

        if blue_btn == 0 and red_btn == 0:
            threading.Thread(target=adjust_body_height, args=(arm,)).start()
            while True:
                arm_data = obj.get_arm_data(arm)
                if arm_data[9] != 0 or arm_data[10] != 0:
                    body.stop(1)
                    break
                time.sleep(0.01)

        if atom_btn == 0:
            threading.Thread(target=head_move, args=(arm,)).start()

        mc.send_angles(mercury_list, speeds)
        time.sleep(0.01)


# ---------------- 主函数 ---------------- #
def main():
    threading.Thread(target=control_arm, args=(1,)).start()
    threading.Thread(target=control_arm, args=(2,)).start()
    while True:
        time.sleep(1)


if __name__ == "__main__":
    main()
