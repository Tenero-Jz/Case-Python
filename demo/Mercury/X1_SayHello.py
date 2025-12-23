from pymycobot import Mercury
import time

# 初始化左右机械臂
ml = Mercury("/dev/left_arm")
mr = Mercury("/dev/right_arm")

ml.set_movement_type(0)
mr.set_movement_type(0)

# # 设置右手手爪角度
# for i in range(1, 5):
#     mr.set_hand_gripper_angle(i, 0)
#     time.sleep(0.1)
# mr.set_hand_gripper_angle(6, 30)
# mr.set_hand_gripper_angle(5, 40)
#
# # 设置左手手爪角度
# ml.set_hand_gripper_angle(1, 0)
# ml.set_hand_gripper_angle(4, 0)
# ml.set_hand_gripper_angle(2, 100)
# ml.set_hand_gripper_angle(3, 100)
# ml.set_hand_gripper_angle(5, 60)
# ml.set_hand_gripper_angle(6, 90)

# # 设置左手固定姿势
# left_pose = [7.468, 25.816, -13.513, -65.267, 12.673, 141.074, -8.023]
# for joint, angle in enumerate(left_pose, start=1):
#     ml.send_angle(joint, angle, 20)
#     time.sleep(0.1)

# 设置右手初始打招呼姿势（按顺序 7→6→5→1→2→3→4）
init_pose = [-10.297, 58.307, 83.722, -103.229, -80, 171.277, -82.914]
joint_order = [7, 6, 5, 1, 2, 3, 4]

for joint in joint_order:
    angle = init_pose[joint - 1]  # 因为列表是从0开始
    mr.send_angle(joint, angle, 20)
    time.sleep(0.1)


# 打招呼动作：关节3左右摆动
try:
    while True:
        mr.send_angle(3, 50, 25)  # 向内摆
        time.sleep(0.3)
        mr.send_angle(3, 100, 25)  # 向外摆
        time.sleep(0.3)
except KeyboardInterrupt:
    print("已停止打招呼动作。")
