# !/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
需要安装 cvzone和mediapipe库，注意这两个库会更新numpy的版本
该案例现将手臂摆放置指定位置
"""
import os
import threading
import time
from pymycobot import *


os.system("sudo chmod 777 /dev/ttyAMA1")

ml = Mercury("/dev/ttyAMA1")


# 控制吸泵
def control_suck(mode):
    if mode == 1:
        ml.set_base_io_output(1, 0)
    else:
        ml.set_base_io_output(1, 1)


control_suck(0)
time.sleep(3)
control_suck(1)

