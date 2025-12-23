import os
import threading
import time
import serial
from pymycobot import *
from pymycobot.utils import get_port_list

os.system("sudo chmod 777 /dev/ttyACM*")
move = ChassisControl(port="/dev/wheeltec_controller")
obj = Exoskeleton(port="/dev/ttyACM4")
ml = Mercury("/dev/left_arm")
mr = Mercury("/dev/right_arm")

# 设置模式
ml.set_movement_type(3)
mr.set_movement_type(3)
ml.set_vr_mode(1)
mr.set_vr_mode(1)

# 定义全局状态变量
last_move_cmd = None
last_rotation_cmd = None
move_lock = threading.Lock()

banana = [[0, 10000, 10000, 10000, 10000, 65535], [31000, 25000, 26000, 24000, 24000, 65535],
          [0, 10000, 10000, 10000, 10000, 65535]]


class Command():
    ID = 2
    Code = 16
    Address_High = 4
    Address_LOW = 111
    Len = 12
    Number_High = 0
    Number_LOW = 6
    Value_High = 0
    Value_LOW = 0
    Joint_High = 0
    Joint_LOW = 0
    cmd_list = [ID, Code, Address_High, Address_LOW, Number_High, Number_LOW, Len,
                Joint_High, Joint_LOW,
                Joint_High, Joint_LOW,
                Joint_High, Joint_LOW,
                Joint_High, Joint_LOW,
                Joint_High, Joint_LOW,
                Joint_High, Joint_LOW,
                ]


cmd_list = Command().cmd_list


def byte_deal(*args):
    result = []
    for value in args:
        high_byte = (value >> 8) & 0xFF
        low_byte = value & 0xFF
        result.extend([high_byte, low_byte])
    return result


def crc16_modbus(data: bytes) -> bytes:
    crc = 0xFFFF
    for pos in data:
        crc ^= pos
        for _ in range(8):
            if (crc & 0x0001) != 0:
                crc >>= 1
                crc ^= 0xA001
            else:
                crc >>= 1
    return crc.to_bytes(2, byteorder='little')


def set_hand_joints_value(value, a1=None):
    tmp = []
    for i in range(len(value)):
        tmp.extend(byte_deal(value[i]))
    for i in range(len(tmp)):
        cmd_list[i + 7] = tmp[i]
    send_data = bytes(cmd_list) + crc16_modbus(cmd_list)
    send_data = send_data.hex().upper()
    hex_list = [int(send_data[i:i + 2], 16) for i in range(0, len(send_data), 2)]
    if a1 is not None:
        a1.tool_serial_write_data(hex_list)
    else:
        print(send_data)


# 控制力控夹爪开闭
def control_gripper(mode):
    if mode == 1:
        set_hand_joints_value(banana[0], ml)
    elif mode == 2:
        set_hand_joints_value(banana[1], ml)
    else:
        raise ValueError("error arm")


# 控制底盘移动
def control_move(x, y):
    global last_move_cmd
    with move_lock:
        if y < 50:
            if last_move_cmd != 'forward':
                move.go_straight(0.2)
                last_move_cmd = 'forward'
        elif y > 200:
            if last_move_cmd != 'backward':
                move.go_back(-0.2)
                last_move_cmd = 'backward'
        elif x > 200:
            if last_move_cmd != 'left':
                move.turn_left(0.2)
                last_move_cmd = 'left'
        elif x < 50:
            if last_move_cmd != 'right':
                move.turn_right(-0.2)
                last_move_cmd = 'right'
        elif 50 < y < 200 and 50 < x < 200:
            if last_move_cmd != 'stop':
                move.stop()
                last_move_cmd = 'stop'


# 停止移动
def stop():
    global last_move_cmd
    with move_lock:
        if last_move_cmd != 'stop':
            move.stop()
            last_move_cmd = 'stop'


def control_arm(arm):
    global last_rotation_cmd
    while True:
        if arm == 2:
            arm_data = obj.get_arm_data(1)
            mc = mr
            mercury_list = [
                arm_data[0], -arm_data[1] + 10, arm_data[2],
                -arm_data[3], arm_data[4], 135 + arm_data[5], arm_data[6] - 20
            ]

        elif arm == 1:
            arm_data = obj.get_arm_data(2)
            x, y = arm_data[11], arm_data[12]
            mc = ml
            threading.Thread(target=control_move, args=(x, y,)).start()
            mercury_list = [
                arm_data[0], -arm_data[1] + 10, arm_data[2],
                -arm_data[3], arm_data[4], 135 + arm_data[5], arm_data[6] + 20
            ]

        else:
            raise ValueError("error arm")

        red_btn = arm_data[9]
        blue_btn = arm_data[10]
        if red_btn == 0:
            threading.Thread(target=control_gripper, args=(1,)).start()

        elif blue_btn == 0:
            threading.Thread(target=control_gripper, args=(2,)).start()

        if red_btn == 0 and blue_btn == 0:
            time.sleep(0.01)
            continue

        mc.send_angles(mercury_list, 6, _async=True)
        time.sleep(0.01)


def main():
    threading.Thread(target=control_arm, args=(1,)).start()  # 左臂
    threading.Thread(target=control_arm, args=(2,)).start()  # 右臂
    while True:
        time.sleep(1)


if __name__ == "__main__":
    main()
