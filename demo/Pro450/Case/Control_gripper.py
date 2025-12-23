# -*- coding: utf-8 -*-
import time
from Pro450.Case.pymycobot import Exoskeleton, Pro450Client

Pro450 = Pro450Client("192.168.0.232", 4500, debug=1)
print(Pro450.get_angles())
# Pro450.release_all_servos()
# Pro450.set_pro_gripper_speed(100)
# while True:
#     Pro450.set_pro_gripper_angle(0)
#     time.sleep(1)
#     Pro450.set_pro_gripper_angle(100)
#     time.sleep(1)

