import os
import threading
import time
import serial
from pymycobot import Pro450Client
from pymycobot.utils import get_port_list

Pro450 = Pro450Client("192.168.0.232", 4500, debug=1)
# Pro450.release_all_servos()
# Pro450.send_angles([0, 0, 0, 0, 0, 0], 60)
# Pro450.send_angle(1,150,100)
# print(Pro450.get_angles())
# Pro450.power_on()
Pro450.set_pro_gripper_angle(10)
# while True:
#     Pro450.send_angles([0, 0, 0, 0, 0, 0], 60)
#     time.sleep(2)
#     Pro450.send_angles([-90.0, 90.0, -89.99, -89.99, -90.0, -90.0], 60)
#     time.sleep(2)
#     Pro450.send_angles([89.99, -89.99, 89.99, 89.99, 89.99, 89.99], 60)
#     time.sleep(2)
#     Pro450.send_angles([90.76, 0, 0.67, 0.01, -90.11, 0.01], 60)
#     time.sleep(2)
#     Pro450.send_angles([90.76, -56.94, 107.64, -46.97, -90.11, 0.01], 60)
#     time.sleep(2)
#     Pro450.send_angles([90.76, 58.84, -108.66, 52.64, -90.11, 0.01], 60)
#     time.sleep(2)
