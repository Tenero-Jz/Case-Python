import threading
import time

from pymycobot import *

my280 = MyCobot280("COM1")
my320 = MyCobot320("COM4")
my450 = Pro450Client("192.168.0.232", 4500)
my630 = ElephantRobot("192.168.10.158", 5001)


def move_280():
    my280.send_angles([90, -90, 90, 90, 90, 90], 100)
    time.sleep(2)
    my280.send_angles([-90, 90, -90, -90, -90, -90], 100)
    time.sleep(2)


def move_320():
    # 第一个位置mc.send_angles([90, 0, 0, 0, 0, 0], 100)
    # 第二个位置mc.send_angles([90, -46.66, 95.18, -46.4, 0, 0], 100)
    # 第三个位置mc.send_angles([90, 48.95, -91.23, 42.71, 0, 0], 100)
    my320.send_angles([90, -90, 90, 90, 90, 90], 100)
    time.sleep(2)
    my320.send_angles([-90, 90, -90, -90, -90, -90], 100)
    time.sleep(2)


def move_450():
    my450.send_angles([-90.0, 90.0, -89.99, -89.99, -90.0, -90.0], 60)
    time.sleep(2)
    my450.send_angles([89.99, -89.99, 89.99, 89.99, 89.99, 89.99], 60)
    time.sleep(2)


def move_630():
    my630.write_angles([-90.0, 90.0, -89.99, -89.99, -90.0, -90.0], 60)
    time.sleep(2)
    my630.write_angles([89.99, -89.99, 89.99, 89.99, 89.99, 89.99], 60)
    time.sleep(2)


threading.Thread(target=move_450, args=()).start()
threading.Thread(target=move_630, args=()).start()
threading.Thread(target=move_320, args=()).start()
threading.Thread(target=move_280, args=()).start()
