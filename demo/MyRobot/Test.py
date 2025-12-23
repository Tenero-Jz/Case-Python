from pymyrobot import MyRobot

mc = MyRobot('COM37', 1000000)

while True:
    numbers = mc.read_pressure_value()
    print(numbers)
