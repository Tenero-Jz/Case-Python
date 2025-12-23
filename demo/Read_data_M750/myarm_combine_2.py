import time
import threading
import traceback
import pandas as pd
import ast
import serial.tools.list_ports
from pymycobot import MyArmC, MyArmM
from pymycobot.error import MyArmDataException


# =============== 通用设置 =================
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
            time.sleep(0.01)
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


# =============== 控制线程：读取表格动作 ================
class ExcelRunner(threading.Thread):
    def __init__(self, myarm_m, file_path):
        super().__init__()
        self.m = myarm_m
        self.running = False
        self.file_path = file_path
        self.done = False  # ✅ 用于标记是否执行完成

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
                self.m.set_joints_angle(angles, 20)
                time.sleep(0.01)
        except Exception as e:
            print("表格执行错误:", traceback.format_exc())
        finally:
            self.done = True  # ✅ 标记为执行完成

    def stop(self):
        self.running = False


# =============== 主程序：监听按钮并切换模式 ================
def main():
    # port_dict = get_port()
    # port_c = input("input myArm C port: ")
    # port_m = input("input myArm M port: ")
    # c_port = port_dict[port_c]
    # m_port = port_dict[port_m]

    myarm_c = MyArmC("COM43", debug=False)
    myarm_m = MyArmM("COM18", 1000000, debug=False)

    file_path = "Data_2025-05-12_14-29-09.xlsx"

    current_mode = "idle"
    joystick_thread = None
    excel_thread = None

    print("等待按钮触发模式...（红=摇操，蓝=表格）")
    last_btn_status = [0, 0]

    try:
        while True:
            red = myarm_c.is_tool_btn_clicked(2)
            blue = myarm_c.is_tool_btn_clicked(3)

            if red is None or blue is None:
                time.sleep(0.1)
                continue

            red_btn = red[0]
            blue_btn = blue[0]

            # 红色按钮：进入摇操模式
            if red_btn == 1 and last_btn_status[0] == 0:
                print(">>> 红色按钮按下：切换到摇操模式")
                if current_mode == "excel" and excel_thread:
                    excel_thread.stop()
                    excel_thread.join()
                if not joystick_thread or not joystick_thread.is_alive():
                    joystick_thread = AngleTransfer(myarm_c, myarm_m)
                    joystick_thread.start()
                current_mode = "joystick"

            # 蓝色按钮：进入表格模式
            elif blue_btn == 1 and last_btn_status[1] == 0:
                print(">>> 蓝色按钮按下：切换到读取表格模式")
                if current_mode == "joystick" and joystick_thread:
                    joystick_thread.stop()
                    joystick_thread.join()
                if not excel_thread or not excel_thread.is_alive():
                    excel_thread = ExcelRunner(myarm_m, file_path)
                    excel_thread.start()
                    current_mode = "excel"

            # ✅ 如果当前是表格模式，且动作执行完毕，就重新执行
            if current_mode == "excel":
                if excel_thread and excel_thread.done:
                    print(">>> 表格动作执行完毕，重新开始读取...")
                    excel_thread = ExcelRunner(myarm_m, file_path)
                    excel_thread.start()

            last_btn_status = [red_btn, blue_btn]
            time.sleep(0.1)

    except KeyboardInterrupt:
        print("退出程序...")
        if joystick_thread:
            joystick_thread.stop()
            joystick_thread.join()
        if excel_thread:
            excel_thread.stop()
            excel_thread.join()


if __name__ == "__main__":
    main()
