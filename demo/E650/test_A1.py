from pymycobot import *
import time
my = Mercury("com3", 1000000, debug=1)
angles = [
    [0, 0, 0, 30, 0, 0, 0],
    [37.36, 7.39, 43.2, 90.84, -1.78, 8.29, -0.01],
    [35.76, -1.19, 47.35, 89.44, -2.63, 92.61, -140.98],
    [4.77, -38.17, 3.85, 77.99, -5.78, 70.95, -87.91]
]
mode = 0
# my.power_on()
# my.set_servo_calibration()
# my.send_angles(angles[0], 30)
# time.sleep(1)
# print(my.get_angles())
# print(my.get_model_direction())
# my.set_model_direction(4,1)
# my.send_angles(angles[0], 10)
while 1:
    for i in range(len(angles)):
        my.send_angles(angles[i], 80)
        time.sleep(4)
# if mode == 0:
#     while 1:
#         for i in range(len(angles)):
#             my.send_angles(angles[i], 5)
#             time.sleep(6)
# my.set_servo_calibration(7)
# time.sleep(0.5)
# my.send_angles(angles[0], 30)
# print(my.get_angles())
# while 1:
#     print("angle ", my.get_angles())
#     time.sleep(0.2)
