import traceback

import pandas as pd
import threading
import time
from pymycobot import Mercury

# 初始化左右臂
ml = Mercury("/dev/left_arm")
mr = Mercury("/dev/right_arm")
# 设置双臂为速度融合模式
ml.set_movement_type(3)
mr.set_movement_type(3)
# 设置VR模式
ml.set_vr_mode(1)
mr.set_vr_mode(1)

# # 设置夹爪运行模式
# ml.set_gripper_mode(0)
# mr.set_gripper_mode(0)
#
#
# def gripper_control(mc, value):
#     mc.set_gripper_value(value, 100)


def process_arm_data(arm, data):
    try:
        # print(data)
        mc = ml if arm == 'left' else mr
        for index, row in data.iterrows():
            # print(f"Processing row {index} for {arm} arm")

            angles = [row[f'Joint{i + 1}'] for i in range(7) if i != 2]
            # print(f"{arm} arm sending angles: {angles}")

            mc.send_angles(angles, 5, _async=True)
            time.sleep(0.01)
            # print(f"{arm} arm finished sending angles")

            # # 处理夹爪控制
            # if row['Button1'] == 0:
            #     threading.Thread(target=gripper_control, args=(mc, 5,)).start()
            # if row['Button2'] == 0:
            #     threading.Thread(target=gripper_control, args=(mc, 100,)).start()
            if row['Button1'] == 1 and row['Button2'] == 1:
                time.sleep(0.01)
                continue

            time.sleep(0.01)
    except Exception as e:
        error = traceback.format_exc()
        print(f"Error occurred in {arm} arm thread: {error}")


file_path = "arm_data_20250327_191104.xlsx"
df = pd.read_excel(file_path)

# 根据 arm 列区分左右臂数据
left_arm_data = df[df['Arm'] == 'Left']
right_arm_data = df[df['Arm'] == 'Right']

# 启动线程控制左右机械臂
threading.Thread(target=process_arm_data, args=('left', left_arm_data)).start()
threading.Thread(target=process_arm_data, args=('right', right_arm_data)).start()
