import os
import threading
import time
import serial
from pymycobot import *
from pymycobot.utils import get_port_list
import dmmotordrive

os.system("sudo chmod 777 /dev/ttyACM*")
ml = dmmotordrive.DMMotorDrive("/dev/ttyACM2")
time.sleep(1)
mr = dmmotordrive.DMMotorDrive("/dev/ttyACM1")
time.sleep(1)
body = dmmotordrive.SD100("/dev/ttyACM0")
time.sleep(1)

ml.power_on_all()
mr.power_on_all()


def body_up():
    body.set_pos(1, 0, 100, 200, 200)


def body_down():
    body.set_pos(1, 70, 100, 200, 200)


while True:
    threading.Thread(target=body_up, args=()).start()
    ml.send_angles([36, 31, 79, 78, 77, 39], 50)
    time.sleep(2)
    ml.send_angles([12, -53, 67, 3, 0, -26], 50)
    time.sleep(2)
    threading.Thread(target=body_down, args=()).start()
    ml.send_angles([36, -73, 17, -82, 15, -26], 50)
    time.sleep(2)
    ml.send_angles([14, -86, 35, 1, 44, -26], 50)
    time.sleep(2)
