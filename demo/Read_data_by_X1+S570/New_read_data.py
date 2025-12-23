import threading
import time
import os
import traceback
import shutil
import pygame
import time
from pymycobot import Mercury
from openpyxl import load_workbook

# 设置权限
os.system("sudo chmod 777 /dev/ttyACM*")

# 初始化对象
ml = Mercury("/dev/left_arm")
mr = Mercury("/dev/right_arm")

if ml.is_power_on() != 1:
    ml.power_on()
if mr.is_power_on() != 1:
    mr.power_on()

# 设置双臂参数
for arm in (ml, mr):
    arm.set_tool_reference([0, 0, 156.5, 0, 0, 0])  # 设置工具坐标系

# ------------------------鼠标控制部分---------------------------#
# 设置夹爪透传模式
ml.set_gripper_mode(0)

THRESHOLD = 0.7  # 鼠标轴触发运动的阈值
DEAD_ZONE = 0.2  # 归零判断阈值

# jog 坐标运动速度
jog_speed = 10

# 夹爪速度
gripper_speed = 70

# 初始点运动速度
home_speed = 10

# 夹爪状态（默认张开）
gripper_state = True

# 6D 轴映射关系，鼠标轴 -> 机械臂坐标ID映射
AXIS_MAPPING = {
    0: 2,
    1: 1,
    2: 3,
    3: 4,
    4: 5,
    5: 6
}

# 轴运动方向映射
DIRECTION_MAPPING = {
    0: (-1, 1),  # 轴0 (Y) -> 负向 -1，正向 1
    1: (-1, 1),  # 轴1 (X) -> 负向 -1，正向 1
    2: (-1, 1),  # 轴2 (Z) -> 负向 -1，正向 1
    3: (-1, 1),  # 轴3 (RX) -> 负向 -1，正向 1
    4: (1, -1),  # 轴4 (RY) -> 负向 1，正向 -1
    5: (1, -1)  # 轴5 (RZ) -> 负向 1，正向 -1
}


def handle_mouse_event(jog_callback, stop_callback, gripper_callback):
    """
    监听 6D 鼠标事件，并调用传入的回调函数控制机械臂
    :param jog_callback: 运动回调函数 (coord_id, direction)
    :param stop_callback: 停止运动回调函数 (coord_id)
    :param gripper_callback: 夹爪开合回调函数 ()
    """
    pygame.init()
    pygame.joystick.init()

    if pygame.joystick.get_count() == 0:
        print("未检测到 6D 鼠标设备！")
        return

    joystick = pygame.joystick.Joystick(0)
    joystick.init()
    print(f"已连接 6D 鼠标: {joystick.get_name()}")

    active_axes = {}  # 记录当前运动状态
    home_active = False  # 记录初始点运动状态

    try:
        while True:
            for event in pygame.event.get():
                # 处理轴运动
                if event.type == pygame.JOYAXISMOTION:
                    axis_id = event.axis
                    value = event.value

                    if axis_id in AXIS_MAPPING:
                        coord_id = AXIS_MAPPING[axis_id]
                        pos_dir, neg_dir = DIRECTION_MAPPING[axis_id]

                        if value > THRESHOLD and active_axes.get(axis_id) != 1:
                            jog_callback(coord_id, pos_dir)
                            active_axes[axis_id] = 1

                        elif value < -THRESHOLD and active_axes.get(axis_id) != -1:
                            jog_callback(coord_id, neg_dir)
                            active_axes[axis_id] = -1

                        elif -DEAD_ZONE < value < DEAD_ZONE and axis_id in active_axes:
                            stop_callback(coord_id)
                            del active_axes[axis_id]

                # 处理按键（按钮 0 回到初始点，按钮 1 控制夹爪）
                elif event.type == pygame.JOYBUTTONDOWN:
                    if event.button == 0:  # 按下按钮 0，回到初始点
                        home_callback()
                        home_active = True
                    elif event.button == 1:  # 按下按钮 1，切换夹爪状态
                        gripper_callback()

                elif event.type == pygame.JOYBUTTONUP:
                    if event.button == 0 and home_active:  # 松开按钮 0，停止初始点运动
                        home_stop_callback()
                        home_active = False

            time.sleep(0.01)
    except KeyboardInterrupt:
        print("监听结束")
        pygame.quit()


# 定义回调函数
def jog_callback(coord_id, direction):
    """触发机械臂JOG坐标运动"""
    if direction != 1:
        direction = 0
    if coord_id in [1, 2, 3]:
        ml.jog_base_coord(coord_id, direction, jog_speed)
    else:
        model = [2, 1, 3]
        model_dir = [0, 1, 1]
        model_id = model[coord_id - 4]
        model_dire = direction ^ model_dir[coord_id - 4]
        ml.jog_rpy(model_id, model_dire, jog_speed)


def stop_callback(coord_id):
    """停止机械臂运动"""
    ml.stop(1)


def gripper_callback():
    """控制夹爪开合"""
    global gripper_state
    gripper_state = not gripper_state
    flag = 1 if gripper_state else 0
    ml.set_gripper_state(flag, gripper_speed)


def home_callback():
    """回到初始点"""
    1
    # ml.send_angles([0, 0, 0, -90, 0, 90, 0], home_speed, _async=True)


def home_stop_callback():
    """停止回到初始点"""
    ml.stop(1)


if __name__ == '__main__':
    # 启动监听
    handle_mouse_event(jog_callback, stop_callback, gripper_callback)


# ------------------------鼠标控制部分end---------------------------#

# 夹爪控制函数
def gripper_control(ml, value):
    ml.set_pro_gripper_angle(14, value)


def l_gripper_control_open():
    ml.set_pro_gripper_angle(14, 6)


def r_gripper_control_open():
    mr.set_pro_gripper_angle(14, 20)


def l_gripper_control_close():
    ml.set_pro_gripper_angle(14, 5)


def r_gripper_control_close():
    mr.set_pro_gripper_angle(14, 0)


def torque_control_mode():
    ml.set_control_mode(1)


def pos_control_mode():
    ml.set_control_mode(0)


def mouse_control_mode():
    ml.set_control_mode(0)
    handle_mouse_event(jog_callback, stop_callback, gripper_callback)


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

count = 1
recording = False  # 记录数据的状态
data_buffer = []  # 缓存数据，减少 Excel 写入次数


# 数据记录线程
def write_data_to_excel():
    """记录数据到 Excel，每隔 50ms 读取一次，每 20 次批量写入"""
    global count, recording, data_buffer
    recording = True
    print("开始记录数据")

    last_time = time.time()  # 初始化上次记录的时间
    save_interval = 100  # 每 20 次写入一次 Excel

    while recording:
        try:
            start_time = time.time()

            # 计算时间间隔
            interval = (start_time - last_time) * 1000
            last_time = start_time

            # 读取数据
            left_angles = ml.get_angles()
            right_angles = mr.get_angles()
            left_coords = ml.get_base_coords()
            right_coords = mr.get_base_coords()
            left_gripper_angle = ml.get_pro_gripper_angle(14)
            right_gripper_angle = mr.get_pro_gripper_angle(14)

            # 缓存数据
            data_buffer.append([
                count,
                str(left_angles),
                str(right_angles),
                str(left_coords),
                str(right_coords),
                left_gripper_angle,
                right_gripper_angle,
                interval
            ])

            # print(f"数据采集成功，第 {count} 行，间隔时间: {interval:.2f} 毫秒")
            count += 1

            # 每 20 次写入 Excel
            if len(data_buffer) >= save_interval:
                wb = load_workbook(xls_name)
                ws = wb.active
                for row in data_buffer:
                    ws.append(row)
                wb.save(xls_name)
                wb.close()
                print(f"成功写入 Excel {len(data_buffer)} 行")
                data_buffer.clear()  # 清空缓存

        except Exception as e:
            print("写入 Excel 失败:", e)
            print(traceback.format_exc())

        # 计算耗时，调整 sleep 让间隔保持在 50ms
        elapsed_time = (time.time() - start_time) * 1000
        sleep_time = max(0, 0.05 - elapsed_time / 1000)  # 50ms
        time.sleep(sleep_time)


# **主线程循环处理用户输入**
data_thread = None  # 用于存储数据记录线程
print("-----------------------------------------------------------")
print("输入 1 开始执行数据采集")
print("输入 2 控制左臂夹爪张开")
print("输入 3 控制右臂夹爪张开")
print("输入 4 控制左臂夹爪闭合")
print("输入 5 控制右臂夹爪闭合")
print("输入 6 切换力矩模式")
print("输入 7 切换位置模式")
print("输入 8 切换3d鼠标控制模式")
print("输入 0 停止数据采集")
print("------------------------------------------------------------")

while True:
    cmd = input("请输入指令: ").strip()

    if cmd == '1':
        if data_thread is None or not data_thread.is_alive():
            data_thread = threading.Thread(target=write_data_to_excel, daemon=True)
            data_thread.start()
        else:
            print("数据采集已经在运行中...")

    elif cmd == '2':
        l_gripper_control_open()
        print("左臂夹爪张开")

    elif cmd == '3':
        r_gripper_control_open()
        print("右臂夹爪张开")

    elif cmd == '4':
        l_gripper_control_close()
        print("左臂夹爪闭合")

    elif cmd == '5':
        r_gripper_control_close()
        print("右臂夹爪闭合")

    elif cmd == '6':
        torque_control_mode()
        print("切换力矩模式")

    elif cmd == '7':
        pos_control_mode()
        print("切换位置模式")

    elif cmd == '8':
        mouse_control_mode()
        print("切换3d鼠标控制模式")

    elif cmd == '0':
        recording = False
        if data_thread is not None:
            data_thread.join()
        print("数据采集已停止")

    elif cmd.lower() == 'exit':
        print("退出程序...")
        recording = False
        if data_thread is not None:
            data_thread.join()
        break

    else:
        print("无效指令，请输入 1-5 或 0 退出数据采集")
