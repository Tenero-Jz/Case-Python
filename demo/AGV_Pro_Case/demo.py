from pymycobot import Mercury, Phoenix
import time

# e = Phoenix()
# e.tool_serial_restore
m = Mercury()


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


def wait_done():
    time.sleep(0.3)
    if m.is_moving() == 1:
        time.sleep(0.1)


pose = [[0, 0, 0, 0, 0, 0],
        [45000, 65535, 65535, 65535, 65535, 0],
        [45000, 0, 65535, 65535, 65535, 0],
        [45000, 0, 0, 65535, 65535, 0],
        [45000, 0, 0, 0, 65535, 0],
        [45000, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0],
        [43087, 31863, 0, 0, 0, 60827],
        [0, 0, 0, 0, 0, 0],
        [43087, 0, 34035, 0, 0, 65535],
        [0, 0, 0, 0, 0, 0]]

mengo = [[0, 0, 0, 0, 0, 65535], [32000, 10000, 10000, 10000, 10000, 65535], [0, 0, 0, 0, 0, 65535]]
apple = [[0, 0, 0, 0, 0, 65535], [14000, 10000, 10000, 10000, 10000, 65535], [0, 0, 0, 0, 0, 65535]]
banana = [[0, 0, 0, 0, 0, 65535], [31000, 18000, 21000, 21000, 21000, 65535], [0, 0, 0, 0, 0, 65535]]

point1 = [[34.59, -40.934, -13.918, -122.406, -20.56, 244.053, 106.648]
          ]
grab_point = [[3.477, -26.679, -11.311, -123.732, -1.475, 155.38, 123.367],
              [3.428, 16.358, -29.572, -146.837, 1.592, 204.485, 123.893],
              [3.447, 25.964, -6.441, -122.922, 8.606, 190.371, 124.421],
              [3.448, 2.562, 6.919, -143.239, 7.202, 178.26, 124.372],
              [3.196, 18.037, 31.368, -115.207, 5.901, 175.705, 124.372]
              ]

a = [[-3.239, -12.563, -25.208, -134.239, -11.354, 170.459, 135.938],
     [-3.232, 22.152, -25.193, -149.156, -9.486, 222.264, 136.002],
     [3.451, 6.254, 52.191, -119.962, 1.353, 173.866, 128.488]]
b = [[3.452, -6.086, -5.387, -136.297, 1.087, 186.463, 128.489],
     [3.455, 19.875, 0.523, -138.6, 0.118, 204.746, 128.489],
     [3.451, 6.254, 52.191, -119.962, 1.353, 173.866, 128.488]]
c = [[-3.241, -44.833, 21.079, -150.959, 12.152, 150.151, 128.496],
     [3.459, -6.618, 23.405, -162.297, 11.894, 196.684, 128.497],
     [3.451, 6.254, 52.191, -119.962, 1.353, 173.866, 128.488]]

# m.send_angles(a[0], 50)
# wait_done()
set_hand_joints_value(banana[0], m)
time.sleep(2)
# m.send_angles(a[1], 50)
# wait_done()
set_hand_joints_value(banana[1], m)
time.sleep(2)
# m.send_angles(a[0], 50)
# wait_done()
# m.send_angles(a[2], 50)
# wait_done()
set_hand_joints_value(banana[0], m)
time.sleep(2)

# m.send_angles(b[0], 50)
# wait_done()
# set_hand_joints_value(banana[0], m)
# time.sleep(2)
# m.send_angles(b[1], 50)
# wait_done()
# set_hand_joints_value(mengo[1], m)
# time.sleep(2)
# m.send_angles(b[0], 50)
# wait_done()
# m.send_angles(b[2], 50)
# wait_done()
# set_hand_joints_value(banana[0], m)
# time.sleep(2)
# m.send_angles(b[0], 50)
# wait_done()
#
# m.send_angles(c[0], 50)
# wait_done()
# set_hand_joints_value(banana[0], m)
# time.sleep(2)
# m.send_angles(c[1], 50)
# wait_done()
# set_hand_joints_value(apple[1], m)
# time.sleep(2)
# m.send_angles(c[0], 50)
# wait_done()
# m.send_angles(c[2], 50)
# wait_done()
# set_hand_joints_value(banana[0], m)
# time.sleep(2)
# m.send_angles(c[0], 50)
# wait_done()
# m.send_angles(grab_point[0],50)
# wait_done()
# set_hand_joints_value(banana[0],m)
# time.sleep(2)
# m.send_angles(grab_point[1],50)
# wait_done()
# set_hand_joints_value(banana[1],m)
# time.sleep(2)
# m.send_angles(grab_point[0],50)
# wait_done()
# m.send_angles(grab_point[-1],50)
# wait_done()
# set_hand_joints_value(banana[0],m)
# time.sleep(2)
# m.send_angles(grab_point[0],50)
# wait_done()

# m.send_angles(grab_point[0],50)
# wait_done()
# set_hand_joints_value(mengo[0],m)
# time.sleep(2)
# m.send_angles(grab_point[2],50)
# wait_done()
# set_hand_joints_value(mengo[1],m)
# time.sleep(2)
# m.send_angles(grab_point[0],50)
# wait_done()
# m.send_angles(grab_point[-1],50)
# wait_done()
# set_hand_joints_value(banana[0],m)
# time.sleep(2)
# m.send_angles(grab_point[0],50)
# wait_done()

# m.send_angles(grab_point[0],50)
# wait_done()
# set_hand_joints_value(banana[0],m)
# time.sleep(2)
# m.send_angles(grab_point[3],50)
# wait_done()
# set_hand_joints_value(apple[1],m)
# time.sleep(2)
# m.send_angles(grab_point[0],50)
# wait_done()
# m.send_angles(grab_point[-1],50)
# wait_done()
# set_hand_joints_value(banana[0],m)
# time.sleep(2)
# m.send_angles(grab_point[0],50)
# wait_done()
