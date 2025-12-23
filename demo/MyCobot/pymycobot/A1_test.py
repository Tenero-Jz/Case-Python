"""
A1_test.py
This module controls the robotic arm movements.

Author: Wang Weijian
Date: 2025-06-10
"""

from pymycobot import *
import time

mc =Mercury('COM33')

if mc.is_power_on() == 1:
    mc.power_on()

speed = 100
angles_1 = [73.632, 84.605, -8.222, -22.29, 0.87, 89.998, 0.0]
angles_2 = [71, -50, -50, -22.29, 90.87, 89.998, 0.0]
angles_3 = [165, -50, -157, -71.29, -90.87, 89.998, 0.0]
angles_4 = [102, 93, -101, -43.29, 100.87, 89.998, 0.0]

for i in  range(3):
    mc.send_angles(angles_1, speed)
    mc.send_angles(angles_2, speed)
    mc.send_angles(angles_3, speed)
    mc.send_angles(angles_4, speed)

# mc.over_limit_return_zero()
mc.send_angles([0,0,0,0,0,90, 0], 100)