import traceback

from pymycobot import *
import time


# mc = MechArm270('COM5', debug=True)
#
# print(mc.get_angles())
#
# # 开启吸泵
# def pump_on():
#     # mc.set_basic_output(2, 0)
#     time.sleep(0.05)
#     # 打开电磁阀
#     mc.set_basic_output(5, 0)
#     time.sleep(0.05)
#
# # 停止吸泵
# def pump_off():
#     # 泄气阀门开始工作
#     # mc.set_basic_output(2, 0)
#     # 关闭电磁阀
#     mc.set_basic_output(5, 1)
#     # time.sleep(1.5)
#     # # 泄气阀门开始工作
#     # mc.set_basic_output(2, 1)
#     time.sleep(0.05)
#
#
# pump_off()
# # time.sleep(3)
# pump_on()
# time.sleep(5)
# pump_off()
# # time.sleep(3)
mc = MyCobot320('com51', 115200, debug=True)

# while True:
#     print(mc.get_joints_angle())
#     time.sleep(1)

# for i in range(1, 7):
#     mc.set_master_out_io_state(i,0)
#     time.sleep(1)
# def pump_on():
#     mc.set_basic_output(1, 1)
#     time.sleep(0.2)
#     mc.set_basic_output(2, 0)
#     time.sleep(0.2)
# #
# def pump_off():
#     mc.set_basic_output(1, 0)
#     time.sleep(0.2)
#     mc.set_basic_output(2, 1)
#     time.sleep(0.2)
#
#
# mc.set_basic_output(1, 1)
# mc.set_basic_output(2, 1)
# # time.sleep(5)
# # mc.set_basic_output(3, 1)
# # # time.sleep(2)
#
# # pump_on()
# # time.sleep(3)
# # pump_off()
# # time.sleep(1)
# from pymycobot.mercury import Mercury
#
# mc=Mercury()
#
# mc.set_pro_gripper_open(14)

try:
    print('1111111111111')
    mc.jog_increment_angle(1, 327, 10)
    time.sleep(1)
except Exception as e:
    e = traceback.format_exc()
    print(e)