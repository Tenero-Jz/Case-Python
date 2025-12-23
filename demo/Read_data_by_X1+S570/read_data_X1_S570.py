import threading
import time
import os
import sys
import traceback
import shutil
from pymycobot import Mercury
from exoskeleton_api import Exoskeleton
from openpyxl import load_workbook, Workbook

# 设置权限
os.system("sudo chmod 777 /dev/ttyACM*")

# 初始化对象
obj = Exoskeleton(port="/dev/ttyACM3")
ml = Mercury("/dev/left_arm")
mr = Mercury("/dev/right_arm")

if ml.is_power_on() != 1:
    ml.power_on()
if mr.is_power_on() != 1:
    mr.power_on()

# 控制模式
l_control_mode, r_control_mode = 1, 1
l_last_mode, r_last_mode = 0, 0

# 设置双臂参数
for arm in (ml, mr):
    arm.set_movement_type(3)  # 设置速度融合模式
    arm.set_vr_mode(1)  # 设置VR模式
    # arm.set_gripper_mode(0)  # 设置夹爪模式
    # arm.set_tool_reference([0, 0, 156.5, 0, 0, 0])  # 设置工具坐标系

# 腰部、颈部、头部回零
for i in range(11, 14):
    ml.send_angle(i, 0, 50)
    time.sleep(0.1)


def joint_limit(angles):
    max_limits = [165, 120, 175, 0, 175, 180, 175]
    min_limits = [-165, -50, -175, -175, -175, 60, -175]
    return [max(min(angle, max_limits[i]), min_limits[i]) for i, angle in enumerate(angles)]


def gripper_control(mc, value):
    mc.set_gripper_value(value, 100)


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
            left_angles = ml.get_angles()
            right_angles = mr.get_angles()
            left_coords = ml.get_base_coords()
            right_coords = mr.get_base_coords()
            left_gripper_angle = 0
            right_gripper_angle = 0

            # 把一条数据存到缓存
            data_buffer.append([
                count,
                str(left_angles),
                str(right_angles),
                str(left_coords),
                str(right_coords),
                # left_gripper_angle,
                # right_gripper_angle,
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


def control_arm(arm):
    """控制机械臂运动"""
    global l_control_mode, l_last_mode, r_control_mode, r_last_mode
    mc = ml if arm == 1 else mr
    last_mode = l_last_mode if arm == 1 else r_last_mode
    control_mode = l_control_mode if arm == 1 else r_control_mode
    dir_off = 1.0
    while True:
        try:
            arm_data = obj.get_arm_data(arm)
            if arm == 1:
                dir_off = -1.0
            else:
                dir_off = 1.0

            mercury_list = joint_limit([
                arm_data[0] + 10 * dir_off, -arm_data[1], arm_data[2], -arm_data[3]-10,
                arm_data[4], 115 + arm_data[5], arm_data[6] - 30
            ])

            # 切换控制模式
            if arm_data[7] == 0 and last_mode == 0:
                last_mode = 1
                control_mode = (control_mode % 3) + 1
                obj.set_color(arm, *([(0, 255, 0), (0, 0, 255), (255, 0, 0)][control_mode - 1]))
            elif arm_data[7] == 1:
                last_mode = 0

            # 设定控制时间
            TI = {1: 10, 2: 5, 3: 3}[control_mode]

            # 控制夹爪
            # if arm_data[9] == 0:
            #     threading.Thread(target=gripper_control, args=(mc, 0)).start()
            #     # gripper_control(mc, 0)
            # elif arm_data[10] == 0:
            #     threading.Thread(target=gripper_control, args=(mc, 100)).start()
                # gripper_control(mc, 100)

            if arm_data[9] == 0 and arm_data[10] == 0:
                time.sleep(0.01)
                continue

            # 发送角度指令
            mc.send_angles(mercury_list, TI, _async=True)
            time.sleep(0.01)

        except Exception as e:
            print("控制机械臂时发生异常:", e)
            print(traceback.format_exc())


# 启动控制线程和写入线程
threading.Thread(target=control_arm, args=(1,)).start()
threading.Thread(target=control_arm, args=(2,)).start()
# time.sleep(0.01)
threading.Thread(target=write_data_to_excel).start()

