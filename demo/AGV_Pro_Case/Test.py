import time

from pymycobot import *


mc = MyAGVProSocket("192.168.4.1", 9000)

mc.move_forward(0.02)
time.sleep(3)
mc.stop()

mc.move_backward(0.04)
time.sleep(3)
mc.stop()

