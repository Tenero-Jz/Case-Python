import threading
import time
import os
import traceback
import shutil
from pymycobot import MyArmM
from openpyxl import load_workbook, Workbook

# 初始化对象
ml = MyArmM("COM36", 1000000)

# 设置双臂参数
for i in (1, 8):
    ml.set_servo_enabled(i, 0)
    time.sleep(1)

# 获取当前日期
current_time = time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime())
xls_name = f'Data_{current_time}.xlsx'

# 复制模板文件
template_file = "Data.xlsx"
if os.path.exists(template_file):
    shutil.copy(template_file, xls_name)
    print(f"已创建新表格: {xls_name}")
else:
    print(f"未找到模板文件: {template_file}，请检查文件是否存在")
# 计数器
count = 1


def write_data_to_excel():
    """记录数据到 Excel（每50条一起写入，提高效率）"""
    global count
    print("开始记录数据")

    last_time = time.time()  # 初始化上次记录的时间
    data_buffer = []  # 数据缓存列表

    while True:
        try:
            # 计算时间间隔
            current_time = time.time()
            interval = (current_time - last_time) * 1000
            last_time = current_time  # 更新上次时间

            # 读取数据
            left_angles = ml.get_joints_angle()

            # 把一条数据存到缓存
            data_buffer.append([
                count,
                str(left_angles),
                interval
            ])

            print(f"采集第 {count} 条数据，暂存 buffer 中，间隔时间: {interval:.2f} 毫秒")

            count += 1

            # 每累计50条，统一写入Excel
            if len(data_buffer) >= 50:
                wb = load_workbook(xls_name)
                ws = wb.active

                for row in data_buffer:
                    ws.append(row)

                wb.save(xls_name)
                wb.close()

                print(f"已批量写入 {len(data_buffer)} 条数据到Excel")
                data_buffer.clear()  # 清空缓存

        except Exception as e:
            print("写入 Excel 失败:", e)
            print(traceback.format_exc())

        time.sleep(0.01)


threading.Thread(target=write_data_to_excel).start()
