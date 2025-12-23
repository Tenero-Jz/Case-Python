"""
socket_test.py
This module controls the robotic arm movements.

Author: Wang Weijian
Date: 2025-07-21
"""
from pymycobot import *
import time

mc = Pro450Client('192.168.0.232', 4500, debug=True)

time.sleep(1)
print(mc.get_angles())
# mc.send_angles([0,0,0,0,0,0], 5)
# while True:
#     print(mc.get_angles())
#     time.sleep(1)