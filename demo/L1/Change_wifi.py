import time

from pymycobot import *

m = MyAGVPro("/dev/ttyCH340", 1000000, debug=1)
print(m.get_wifi_ip_port())

m.set_communication_state(1)
time.sleep(1)
