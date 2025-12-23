import time
import threading
from pymycobot import MyArmC
from pymycobot import Pro450Client

c650 = MyArmC("COM33", debug=False)  # 你的 C650 串口
pro450 = Pro450Client("192.168.0.232", 4500)  # Pro450 的 IP 和端口

pro450.set_fresh_mode(1)
pro450.set_limit_switch(2, 0)
time.sleep(0.1)


class GripperController:
    def __init__(self, pro450):
        self.p = pro450
        self.last_state = None  # "open" 或 "close"

    def open(self):
        self.p.set_digital_output(5, 0)
        self.p.set_digital_output(6, 1)

    def close(self):
        self.p.set_digital_output(5, 1)
        self.p.set_digital_output(6, 0)

    def update(self, angle):
        want_state = "close" if angle > -50 else "open"
        if want_state == self.last_state:
            return

        self.last_state = want_state

        if want_state == "close":
            print(">>> 执行：夹爪关闭")
            self.close()
        else:
            print(">>> 执行：夹爪打开")
            self.open()


gripper = GripperController(pro450)


class AngleSyncThread(threading.Thread):
    def __init__(self, c_arm, p_arm, speed=100):
        super().__init__()
        self.c = c_arm
        self.p = p_arm
        self.speed = speed
        self.running = False

    def run(self):
        self.running = True
        print("开始遥控同步线程...")

        while self.running:
            start = time.time()

            angles = self.c.get_joints_angle()
            get_angle_time = time.time() - start
            print("获取角度时间：", get_angle_time*1000)
            if angles and len(angles) == 7:
                pro_angles = angles[:6]
                pro_angles[1] *= -1
                pro_angles[2] = -pro_angles[2] - 90
                pro_angles[4] = angles[3]
                pro_angles[3] = -angles[4]

                try:
                    self.p.send_angles(pro_angles, self.speed, _async=True)
                except Exception as e:
                    print("发送角度失败：", e)

                # gripper.update(angles[6])

            # loop_dt = time.time() - start
            # if loop_dt < 0.01:  # 20ms → 50Hz 控制频率
            #     time.sleep(0.01 - loop_dt)
            total_time = time.time() - start
            print("总时间：", total_time*1000)

    def stop(self):
        self.running = False


if __name__ == "__main__":
    print("开始遥控：C650 → Pro450（含夹爪控制）")
    sync_thread = AngleSyncThread(c650, pro450)
    sync_thread.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("停止遥控...")
        sync_thread.stop()
