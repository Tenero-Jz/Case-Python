import time
import threading
import traceback
import pandas as pd
import ast
import serial.tools.list_ports
from pymycobot import MyArmC, MyArmM
from pymycobot.error import MyArmDataException


def get_port():
    port_list = serial.tools.list_ports.comports()
    res = {}
    for i, port in enumerate(port_list, 1):
        print(f"{i} - {port.device}")
        res[str(i)] = port.device
    return res


def processing_data(angle):
    angle = [float(i) for i in angle]
    angle[1] *= -1
    gripper_angle = angle.pop(-1)
    angle.append((gripper_angle - 0.08) / (-95.27 - 0.08) * (-123.13 + 1.23) - 1.23)
    joint_limits = [(-160, 160), (-60, 90), (-80, 40), (-150, 150), (-70, 70), (-140, 140), (-115, 0)]
    for i in range(min(len(angle), len(joint_limits))):
        low, high = joint_limits[i]
        angle[i] = max(min(angle[i], high), low)
    return angle


# =============== 控制线程：摇操功能 ================
class AngleTransfer(threading.Thread):
    def __init__(self, myarm_c, myarm_m, speed=100):
        super().__init__()
        self.c = myarm_c
        self.m = myarm_m
        self.speed = speed
        self.running = False
        self.angle = []

    def run(self):
        self.running = True
        while self.running:
            angle = self.c.get_joints_angle()
            if angle:
                self.angle = angle
            time.sleep(0.05)
            if self.angle:
                try:
                    processed = processing_data(self.angle)
                    processed[2] += 10
                    processed[3] += 10
                    self.m.set_joints_angle(processed, self.speed)
                except MyArmDataException:
                    pass

    def stop(self):
        self.running = False


class ExcelRunner(threading.Thread):
    def __init__(self, myarm_m, file_path):
        super().__init__()
        self.m = myarm_m
        self.running = False
        self.file_path = file_path
        self.done = False

    def run(self):
        self.running = True
        try:
            df = pd.read_excel(self.file_path, engine='openpyxl')
            angle_list = df.iloc[1:, 1].dropna().tolist()
            for angle_str in angle_list:
                if not self.running:
                    break
                angles = ast.literal_eval(angle_str)
                if angles[6] <= -118:
                    angles[6] = -116
                if angles[6] > -90:
                    angles[6] = -30
                self.m.set_joints_angle(angles, 15)
                time.sleep(0.03)
        except Exception:
            print("表格执行错误:", traceback.format_exc())
        finally:
            self.done = True

    def stop(self):
        self.running = False


class MyArmSystem:
    def __init__(self, c_port, m_port, file_path, name="Arm"):
        self.myarm_c = MyArmC(c_port, debug=False)
        self.myarm_m = MyArmM(m_port, 1000000, debug=False)
        self.file_path = file_path
        self.name = name

        self.joystick_thread = None
        self.excel_thread = None
        self.current_mode = "idle"
        self.last_btn_status = [0, 0]

    def run(self):
        print(f"[{self.name}] 等待按钮触发模式...（红=摇操，蓝=表格）")
        while True:
            try:
                red = self.myarm_c.is_tool_btn_clicked(2)
                blue = self.myarm_c.is_tool_btn_clicked(3)

                if red is None or blue is None:
                    time.sleep(0.1)
                    continue

                red_btn = red[0]
                blue_btn = blue[0]

                # 红色按钮按下：进入摇操模式
                if red_btn == 1 and self.last_btn_status[0] == 0:
                    print(f"[{self.name}] >>> 红色按钮按下：切换到摇操模式")
                    if self.current_mode == "excel" and self.excel_thread:
                        self.excel_thread.stop()
                        self.excel_thread.join()
                    if not self.joystick_thread or not self.joystick_thread.is_alive():
                        self.joystick_thread = AngleTransfer(self.myarm_c, self.myarm_m)
                        self.joystick_thread.start()
                    self.current_mode = "joystick"

                # 蓝色按钮按下：进入表格模式
                elif blue_btn == 1 and self.last_btn_status[1] == 0:
                    print(f"[{self.name}] >>> 蓝色按钮按下：切换到读取表格模式")
                    if self.current_mode == "joystick" and self.joystick_thread:
                        self.joystick_thread.stop()
                        self.joystick_thread.join()
                    if not self.excel_thread or not self.excel_thread.is_alive():
                        self.excel_thread = ExcelRunner(self.myarm_m, self.file_path)
                        self.excel_thread.start()
                        self.current_mode = "excel"

                # 表格模式下执行完毕自动重启
                if self.current_mode == "excel":
                    if self.excel_thread and self.excel_thread.done:
                        print(f"[{self.name}] >>> 表格动作执行完毕，重新开始读取...")
                        self.excel_thread = ExcelRunner(self.myarm_m, self.file_path)
                        self.excel_thread.start()

                self.last_btn_status = [red_btn, blue_btn]
                time.sleep(0.1)

            except KeyboardInterrupt:
                print(f"[{self.name}] >>> 中断退出")
                break

        if self.joystick_thread:
            self.joystick_thread.stop()
            self.joystick_thread.join()
        if self.excel_thread:
            self.excel_thread.stop()
            self.excel_thread.join()


def main():
    # 文件
    file_path_1 = "Data_2025-05-12_14-29-09.xlsx"

    # 端口
    system1 = MyArmSystem("COM8", "COM11", file_path_1, name="Arm1")
    system2 = MyArmSystem("COM43", "COM18", file_path_1, name="Arm2")

    # 启动两个线程
    t1 = threading.Thread(target=system1.run)
    t2 = threading.Thread(target=system2.run)

    t1.start()
    t2.start()

    # 等待线程结束
    t1.join()
    t2.join()


if __name__ == "__main__":
    main()
