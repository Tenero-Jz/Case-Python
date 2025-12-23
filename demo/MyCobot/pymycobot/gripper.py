from pymycobot import *
import time

m = MyCobot280("com25",debug=True)

def is_bit3_zero(value):
    return ((value & (1 << 3)) == 0)

def change_gripper_system_data():
    for i in range(3):
        value = m.get_servo_data(7, 18, 1)
        print("value ", value)
        if is_bit3_zero(value) == 0:
            print("need change ", value)
            m.set_servo_data(7, 18, value-8)
        else:
            print("now gripper sp give 0,can stop")

def gripper_run():            
    m.set_gripper_state(0, 1,1,1)
    time.sleep(0.3)
    m.set_gripper_state(0, 0,1,1)
    m.set_gripper_value(20, 5, 1,1)
    time.sleep(0.1)
    m.set_gripper_state(0, 0,1,1)

change_gripper_system_data()
#gripper_run()
#print("torque ", m.get_HTS_gripper_torque())
# m.set_HTS_gripper_torque(210)
# print("torque ", m.get_HTS_gripper_torque())
