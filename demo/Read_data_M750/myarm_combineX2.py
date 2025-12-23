# -*- coding: utf-8 -*-
import time
import threading
import traceback
import pandas as pd
import ast
import serial.tools.list_ports
from pymycobot import MyArmC, MyArmM
from pymycobot.error import MyArmDataException
import os

os.system("sudo chmod 777 /dev/ttyACM*")


def get_port():
    port_list = serial.tools.list_ports.comports()
    res = {}
    for i, port in enumerate(port_list, 1):
        print(f"{i} - {port.device}")
        res[str(i)] = port.device
    return res


def processing_data(angle, reverse_joint2=True):
    angle = [float(i) for i in angle]
    if reverse_joint2:
        angle[1] *= -1
    gripper_angle = angle.pop(-1)
    angle.append((gripper_angle - 0.08) / (-95.27 - 0.08) * (-123.13 + 1.23) - 1.23)
    joint_limits = [(-160, 160), (-60, 90), (-80, 40), (-150, 150), (-70, 70), (-140, 140), (-115, 0)]
    for i in range(min(len(angle), len(joint_limits))):
        low, high = joint_limits[i]
        angle[i] = max(min(angle[i], high), low)
    return angle


class AngleTransfer(threading.Thread):
    def __init__(self, myarm_c, myarm_m, speed=100, name="", reverse_joint2=True):
        super().__init__(name=name)
        self.c = myarm_c
        self.m = myarm_m
        self.speed = speed
        self.running = False
        self.angle = []
        self.name = name
        self.reverse_joint2 = reverse_joint2

    def run(self):
        self.running = True
        print(f"[{self.name}] 摇操线程启动")
        while self.running:
            angle = self.c.get_joints_angle()
            if angle:
                self.angle = angle
            time.sleep(0.01)
            if self.angle:
                try:
                    processed = processing_data(self.angle, reverse_joint2=self.reverse_joint2)
                    processed[2] += 10
                    processed[3] += 10
                    self.m.set_joints_angle(processed, self.speed)
                except MyArmDataException:
                    pass
        print(f"[{self.name}] 摇操线程停止")

    def stop(self):
        self.running = False


class ExcelRunner(threading.Thread):
    def __init__(self, myarm_m, file_path, name=""):
        super().__init__(name=name)
        self.m = myarm_m
        self.running = False
        self.file_path = file_path
        self.done = False
        self.name = name

    def run(self):
        self.running = True
        print(f"[{self.name}] 表格线程启动")
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
                self.m.set_joints_angle(angles, 20)
                time.sleep(0.01)
        except Exception as e:
            print(f"[{self.name}] 表格执行错误:\n{traceback.format_exc()}")
        finally:
            self.done = True
            print(f"[{self.name}] 表格线程结束")

    def stop(self):
        self.running = False


class ArmSystem:
    def __init__(self, name, c_port, m_port, file_path, reverse_joint2=True):
        self.name = name
        self.myarm_c = MyArmC(c_port, debug=False)
        self.myarm_m = MyArmM(m_port, 1000000, debug=False)
        self.file_path = file_path
        self.current_mode = "idle"
        self.joystick_thread = None
        self.excel_thread = None
        self.last_btn_status = [0, 0]
        self.reverse_joint2 = reverse_joint2

    def update(self):
        red = self.myarm_c.is_tool_btn_clicked(2)
        blue = self.myarm_c.is_tool_btn_clicked(3)

        if red is None or blue is None:
            return

        red_btn = red[0]
        blue_btn = blue[0]

        if red_btn == 1 and self.last_btn_status[0] == 0:
            print(f"[{self.name}] 红色按钮按下：切换到摇操模式")
            if self.current_mode == "excel" and self.excel_thread:
                self.excel_thread.stop()
                self.excel_thread.join()
            if not self.joystick_thread or not self.joystick_thread.is_alive():
                self.joystick_thread = AngleTransfer(self.myarm_c, self.myarm_m, name=f"{self.name}-摇操",
                                                     reverse_joint2=self.reverse_joint2)
                self.joystick_thread.start()
            self.current_mode = "joystick"

        elif blue_btn == 1 and self.last_btn_status[1] == 0:
            print(f"[{self.name}] 蓝色按钮按下：切换到表格模式")
            if self.current_mode == "joystick" and self.joystick_thread:
                self.joystick_thread.stop()
                self.joystick_thread.join()
            if not self.excel_thread or not self.excel_thread.is_alive():
                self.excel_thread = ExcelRunner(self.myarm_m, self.file_path, name=f"{self.name}-表格")
                self.excel_thread.start()
                self.current_mode = "excel"

        if self.current_mode == "excel":
            if self.excel_thread and self.excel_thread.done:
                print(f"[{self.name}] 表格动作执行完毕，重新开始读取...")
                self.excel_thread = ExcelRunner(self.myarm_m, self.file_path, name=f"{self.name}-表格")
                self.excel_thread.start()

        self.last_btn_status = [red_btn, blue_btn]

    def stop_all(self):
        if self.joystick_thread:
            self.joystick_thread.stop()
            self.joystick_thread.join()
        if self.excel_thread:
            self.excel_thread.stop()
            self.excel_thread.join()
        print(f"[{self.name}] 已停止所有线程")


def main():
    # 第一套
    system_A = ArmSystem(
        name="系统A",
        c_port="/dev/ttyACM0",  # C650
        m_port="/dev/ttyACM1",  # M750
        file_path="Data_2025-05-12_14-29-09.xlsx",
        reverse_joint2=False
    )

    # 第二套
    system_B = ArmSystem(
        name="系统B",
        c_port="/dev/ttyACM2",  # 第二台 C650
        m_port="/dev/ttyACM3",  # 第二台 M750
        file_path="Data_2025-05-12_14-29-09.xlsx",
        reverse_joint2=True
    )

    print("等待按钮触发模式...（红=摇操，蓝=表格）")
    try:
        while True:
            system_A.update()
            system_B.update()
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("退出程序...")
        system_A.stop_all()
        system_B.stop_all()


if __name__ == "__main__":
    main()
