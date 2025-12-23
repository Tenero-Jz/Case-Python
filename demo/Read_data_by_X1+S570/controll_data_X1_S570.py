import traceback
import pandas as pd
import threading
import time
from pymycobot import Mercury
import ast
import openpyxl

# 初始化左右臂
ml = Mercury("/dev/left_arm")
mr = Mercury("/dev/right_arm")
ml.set_movement_type(4)
mr.set_movement_type(4)
ml.set_vr_mode(1)
mr.set_vr_mode(1)


def process_arm_data(arm, angle_strings):
    try:
        mc = ml if arm == 'left' else mr
        for angle_str in angle_strings:
            # 把字符串解析成真正的 Python 列表对象
            angles = ast.literal_eval(angle_str)
            angles = [a for i, a in enumerate(angles)]
            mc.send_angles(angles, 10, _async=True)
            time.sleep(0.25)

    except Exception as e:
        error = traceback.format_exc()
        print(f"Error occurred in {arm} arm thread: {error}")


# 读取新格式 Excel
file_path = "coffee.xlsx"
df = pd.read_excel(file_path, engine='openpyxl')

left_angles = df.iloc[1:, 1].dropna().tolist()  # B列，从第2行开始
right_angles = df.iloc[1:, 2].dropna().tolist()  # C列，从第2行开始

# 启动线程控制左右机械臂
threading.Thread(target=process_arm_data, args=('left', left_angles)).start()
time.sleep(0.01)
threading.Thread(target=process_arm_data, args=('right', right_angles)).start()
