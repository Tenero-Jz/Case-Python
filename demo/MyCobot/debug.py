import time

from pymycobot import *

mc = MyCobot320("COM29")
# mc.release_all_servos()
# mc.focus_all_servos()
# print(mc.get_angles())
# mc.send_angles([90, 0, 0, 0, 0, 0], 100)
# time.sleep(1)
while True:
    # mc.send_angles([90, 0, 0, 0, 0, 0], 100)
    # time.sleep(1)
    mc.send_angles([90, -90, 90, 90, 90, 90], 100)
    time.sleep(1)
    mc.send_angles([-90, 90, -90, -90, -90, -90], 100)
    time.sleep(1)

