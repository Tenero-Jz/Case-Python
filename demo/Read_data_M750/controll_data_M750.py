import traceback
import pandas as pd
import threading
import time
from pymycobot import MyArmM
import ast
import openpyxl

# 初始化左右臂
ml = MyArmM("COM36", 1000000)

ml.set_tool_led_color(0, 255, 0)


def process_arm_data(arm, angle_strings):
    try:
        if arm == 'left':
            mc = ml
            for angle_str in angle_strings:
                # 把字符串解析成真正的 Python 列表对象
                angles = ast.literal_eval(angle_str)
                angles = [a for i, a in enumerate(angles)]
                print(angles)
                if angles[6] <= -118:
                    angles[6] = -116
                if angles[6] > -90:
                    angles[6] = -30
                mc.set_joints_angle(angles, 15)
                time.sleep(0.03)

    except Exception as e:
        error = traceback.format_exc()
        print(f"Error occurred in {arm} arm thread: {error}")


# 读取新格式 Excel
file_path = "Data_2025-05-12_14-29-09.xlsx"
df = pd.read_excel(file_path, engine='openpyxl')

left_angles = df.iloc[1:, 1].dropna().tolist()  # B列，从第2行开始

# 启动线程控制左右机械臂
threading.Thread(target=process_arm_data, args=('left', left_angles)).start()
