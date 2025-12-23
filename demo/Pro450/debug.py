import os
import threading
import time
import serial
from pymycobot import Exoskeleton, Pro450Client
from pymycobot.utils import get_port_list

Pro450 = Pro450Client("192.168.0.232", 4500, debug=1)
# Pro450.set_pro_gripper_angle(0)
# print(Pro450.get_robot_status())
# Pro450.release_all_servos()
# Pro450.send_angle(2,-10,10)
# Pro450.send_angles([0, -10, -60, 0, 0, -45], 50)
# Pro450.over_limit_return_zero()
# Pro450.power_off()
# obj = Exoskeleton("COM7")
# Pro450.resume()
# time.sleep(1)
# Pro450.power_on()
time.sleep(1)
print(Pro450.get_robot_status())
# Pro450.flash_tool_firmware("1.2", 0)
# print(Pro450.get_tool_modify_version(), Pro450.get_atom_version())
# Pro450.set_servo_calibration(6)
# time.sleep(1)
# print(Pro450.get_angles())
# Pro450.send_angle(6,-15,10)
# Pro450.send_angles([0, 0, 0, 0, 0, 0], 50)
# Pro450.set_fresh_mode()
# print(Pro450.get_servo_status())
# Pro450.send_angle(4, -95, 50)

