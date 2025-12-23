import time

from pymycobot import MyArmM

robot = MyArmM("COM32", 1000000)
# robot.set_servo_enabled(1, 0)

robot.set_tool_led_color(0, 255, 0)
# for i in range(1, 8):
#     robot.set_servo_enabled(i, 0)
#     time.sleep(1)

# while True:
#     print(robot.get_joints_angle())
#     time.sleep(0.01)