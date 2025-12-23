#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import time
import dmmotordrive

# ################################################################ MyArmE1 控制器
dmm = dmmotordrive.DMMotorDrive("/dev/ttyACM0")
angle = dmm.get_angle(1)
print(f"Angle: {angle}")
dmm.send_angle(1, 90, 10)
time.sleep(3)
angle = dmm.get_angle(1)
print(f"Angle: {angle}")

# ################################################################ L1 控制器
sd = dmmotordrive.SD100("/dev/ttyACM0")
sd.set_pos(1, 10, 100, 200, 200)






