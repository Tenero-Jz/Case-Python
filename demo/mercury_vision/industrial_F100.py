import threading
import rospy
import time
import sys
import actionlib
import numpy as np
from pymycobot import Mercury

from actionlib_msgs.msg import *
from actionlib_msgs.msg import GoalID
from move_base_msgs.msg import MoveBaseAction, MoveBaseGoal
from geometry_msgs.msg import Point
from geometry_msgs.msg import Twist
from geometry_msgs.msg import PoseWithCovarianceStamped
from tf.transformations import quaternion_from_euler
from camera_detect import camera_detect

camera_params = np.load("camera_params.npz")  # 相机配置文件
mtx, dist = camera_params["mtx"], camera_params["dist"]
ml = Mercury("/dev/left_arm")  # 设置左臂端口
mr = Mercury("/dev/right_arm")  # 设置右臂端口
ml_obj = camera_detect(2, 32, mtx, dist, 0)
mr_obj = camera_detect(6, 32, mtx, dist, 1)
angle_move_speed = 10  # 关节控制速度
coord_move_speed = 10  # 坐标控制速度
sp = 20  # 设置移动速度


# ml_obj.camera_open()
# ml_obj.camera_open_loop()

class MapNavigation:
    def __init__(self):
        self.goalReached = False
        rospy.init_node('map_navigation', anonymous=False)

        # ros publisher
        self.pub = rospy.Publisher('/cmd_vel', Twist, queue_size=10)
        self.pub_setpose = rospy.Publisher('/initialpose', PoseWithCovarianceStamped, queue_size=10)
        self.pub_cancel = rospy.Publisher('/move_base/cancel', GoalID, queue_size=10)

    # init robot  pose AMCL
    def set_pose(self, xGoal, yGoal, orientation_z, orientation_w, covariance):
        pose = PoseWithCovarianceStamped()
        pose.header.seq = 0
        pose.header.stamp.secs = 0
        pose.header.stamp.nsecs = 0
        pose.header.frame_id = 'map'
        pose.pose.pose.position.x = xGoal
        pose.pose.pose.position.y = yGoal
        pose.pose.pose.position.z = 0.0
        q = quaternion_from_euler(0, 0, 1.57)
        pose.pose.pose.orientation.x = 0.0
        pose.pose.pose.orientation.y = 0.0
        pose.pose.pose.orientation.z = orientation_z
        pose.pose.pose.orientation.w = orientation_w
        pose.pose.covariance = [0.25, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.25, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                                0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                                0.0, 0.0, 0.0, 0.0, covariance]
        rospy.sleep(1)
        self.pub_setpose.publish(pose)
        rospy.loginfo('Published robot pose: %s' % pose)

    # move_base
    def moveToGoal(self, xGoal, yGoal, orientation_z, orientation_w):
        ac = actionlib.SimpleActionClient("move_base", MoveBaseAction)
        while (not ac.wait_for_server(rospy.Duration.from_sec(5.0))):
            sys.exit(0)

        goal = MoveBaseGoal()
        goal.target_pose.header.frame_id = "map"
        goal.target_pose.header.stamp = rospy.Time.now()
        goal.target_pose.pose.position = Point(xGoal, yGoal, 0)
        goal.target_pose.pose.orientation.x = 0.0
        goal.target_pose.pose.orientation.y = 0.0
        goal.target_pose.pose.orientation.z = orientation_z
        goal.target_pose.pose.orientation.w = orientation_w

        rospy.loginfo("Sending goal location ...")
        ac.send_goal(goal)

        ac.wait_for_result(rospy.Duration(60))

        if (ac.get_state() == GoalStatus.SUCCEEDED):
            rospy.loginfo("You have reached the destination")
            return True
        else:
            rospy.loginfo("The robot failed to reach the destination")
            return False

    # speed command
    def pub_vel(self, x, y, theta):
        twist = Twist()
        twist.linear.x = x
        twist.linear.y = y
        twist.linear.z = 0
        twist.angular.x = 0
        twist.angular.y = 0
        twist.angular.z = theta
        self.pub.publish(twist)

    def vel_control(self, direction=[0, 0, 0], speed=0.0, control_time=0.0):
        """
        Function to control velocity.

        Parameters:
            - direction (list): An array containing three elements representing the direction of motion.
            - speed (float): Speed value.
            - time (float): Time value.

        Raises:
            - ValueError: If the direction is not a list containing three elements.

        Usage:
            >>> vel_control([1, 0, 0], 0.2, 5)
        """
        duration, vel = control_time, speed
        start_time = time.time()
        # Motion control
        if isinstance(direction, list) and len(direction) == 3:
            while (time.time() - start_time) < duration:
                self.pub_vel(direction[0] * abs(vel), direction[1] * abs(vel), direction[2] * abs(vel))
            self.pub_vel(0, 0, 0)
        else:
            print("Direction should be a list containing three elements")

    def turnRight(self, speed, control_time):
        self.vel_control([0, 0, -1], speed, control_time)

    def turnLeft(self, speed, control_time):
        self.vel_control([0, 0, 1], speed, control_time)

    def goStraight(self, speed, control_time):
        self.vel_control([1, 0, 0], speed, control_time)

    def goBack(self, speed, control_time):
        self.vel_control([-1, 0, 0], speed, control_time)


# 等待机械臂运行结束
def wait():
    # pass
    time.sleep(0.2)
    while (ml.is_moving()) or (mr.is_moving()):
        time.sleep(0.03)


def waitL():
    # pass
    time.sleep(0.2)
    while ml.is_moving():
        time.sleep(0.03)


def waitR():
    # pass
    time.sleep(0.2)
    while mr.is_moving():
        time.sleep(0.03)


def camera_get_coords():
    ml_obj.camera_open()
    target_l = ml_obj.stag_robot_identify(ml)
    ml_obj.release()
    mr_obj.camera_open()
    target_r = mr_obj.stag_robot_identify(mr)
    mr_obj.release()
    return target_l, target_r


def r_gripper_open():
    mr.set_pro_gripper_angle(14, 100)


def r_gripper_close():
    mr.set_pro_gripper_angle(14, 10)


def l_gripper_open():
    ml.set_pro_gripper_angle(14, 100)


def l_gripper_close():
    ml.set_pro_gripper_angle(14, 10)


def l_down_desk1(target_l):
    ml.send_angles([-22.598, 22.776, -96.601, 81.595, 70.088, -110.293], sp)  # 过渡点
    waitL()
    # ml.send_angle(6, -80, sp)
    # waitL()
    l_coords = ml.get_base_coords()  # 获取机械臂当前坐标
    l_coords[0] = target_l[0] + 20
    l_coords[1] = target_l[1] - 49
    l_coords[2] = target_l[2] - 65
    ml.send_base_coords(l_coords, sp)


def r_down_desk1(target_r):
    mr.send_angles([20.074, 25.849, -92.246, -79.021, 73.714, 103.416], sp)
    waitR()
    # mr.send_angle(6, 80, sp)
    # waitR()
    r_coords = mr.get_base_coords()  # 获取机械臂当前坐标
    # print("target_coords", target_coords)
    # r_coords[0] = target_r[0]
    r_coords[1] = target_r[1] + 60
    r_coords[2] = target_r[2] - 40
    mr.send_base_coords(r_coords, sp)


def l_down_desk2(target_l):
    # ml.send_angle(6, -80, sp)
    # waitL()
    l_coords = ml.get_base_coords()  # 获取机械臂当前坐标
    l_coords[0] = target_l[0] + 75
    l_coords[1] = target_l[1] + 80
    l_coords[2] = target_l[2]
    ml.send_base_coords(l_coords, sp)


def r_down_desk2(target_r):
    r_coords = mr.get_base_coords()  # 获取机械臂当前坐标
    # print("target_coords", target_coords)
    r_coords[0] = target_r[0] + 55
    r_coords[1] = target_r[1] - 46
    r_coords[2] = target_r[2] + 42.5
    mr.send_base_coords(r_coords, sp)


def l_up():
    ml.send_base_coord(3, 300, sp)


def r_up():
    mr.send_base_coord(3, 300, sp)


def l_out():
    ml.send_base_coord(1, 410, sp)


def r_out():
    mr.send_base_coord(1, 410, sp)


def l_point():
    ml.send_angles([-67.331, 33.031, -82.811, 93.925, 80.354, 59.363], sp)  # 过渡点1
    waitL()
    ml.send_angles([-29.556, 16.088, -105.442, 154.703, 113.949, 72.274], sp)  # 过渡点2
    waitL()


def r_point():
    mr.send_angles([52.208, 18.497, -113.159, -134.424, 105.072, -38.491], sp)  # 过渡点1
    waitR()
    mr.send_angles([26.992, 21.856, -105.18, -153.623, 112.735, -70.812], sp)  # 过渡点2
    waitR()


def pick_up():  # 从桌子上拿取木块
    self.console.info("正在识别二维码...")
    target_l, target_r = camera_get_coords()
    print("l:", target_l)
    print("r:", target_r)

    # l_down(target_l)
    # r_down(target_r)
    self.console.info("正在执行抓取动作...")
    threading.Thread(target=l_down_desk1, args=(target_l,)).start()
    threading.Thread(target=r_down_desk1, args=(target_r,)).start()
    wait()
    time.sleep(5)
    self.console.info("夹爪正在关闭...")
    threading.Thread(target=r_gripper_close, args=()).start()
    threading.Thread(target=l_gripper_close, args=()).start()
    time.sleep(2)
    # # l_up()
    # # r_up()
    self.console.info("抓取完成，正在执行抬起动作...")
    threading.Thread(target=l_up, args=()).start()
    threading.Thread(target=r_up, args=()).start()
    wait()


def pick_down():  # 放在桌的架子上
    threading.Thread(target=l_point, args=()).start()
    threading.Thread(target=r_point, args=()).start()
    wait()
    self.console.info("正在识别二维码...")
    target_l, target_r = camera_get_coords()
    print("l2:", target_l)
    print("r2:", target_r)

    # 向前放置
    self.console.info("正在执行放置动作...")
    threading.Thread(target=l_down_desk2, args=(target_l,)).start()
    threading.Thread(target=r_down_desk2, args=(target_r,)).start()
    wait()
    time.sleep(5)
    self.console.info("夹爪正在打开...")
    threading.Thread(target=r_gripper_open, args=()).start()
    threading.Thread(target=l_gripper_open, args=()).start()
    time.sleep(2)
    # # 放置完回到初始位
    self.console.info("放置完成，正在执行抬起动作...")
    threading.Thread(target=l_out, args=()).start()
    threading.Thread(target=r_out, args=()).start()
    wait()


def load():
    mr_coords = mr.get_base_coords()  # 获取当前左臂位姿
    ml_coords = ml.get_base_coords()  # 获取当前左臂位姿

    mr_coords[2] -= 50  # z轴下降
    ml_coords[2] -= 50  # z轴下降

    mr.send_base_coords(mr_coords, coord_move_speed)  # 坐标控制
    ml.send_base_coords(ml_coords, coord_move_speed)  # 坐标控制
    wait()

    mr.set_gripper_value(50, 50)
    ml.set_gripper_value(50, 50)


def robot_init():  # 双臂初始位置
    self.console.info("右臂正在回到初始位...")
    mr.send_angles([23.128, 18.229, -110.313, -74.179, 73.648, 114.621], sp)
    wait()
    self.console.info("左臂正在回到初始位...")
    ml.send_angles([-25.019, 17.607, -108.705, 77.618, 69.336, -117.957], sp)
    wait()
    self.console.info("夹爪正在打开...")
    threading.Thread(target=l_gripper_open, args=()).start()
    threading.Thread(target=r_gripper_open, args=()).start()
    # ml.send_angles([-66.36, 31.31, -55.66, 97.58, 25.51, 66.19], sp)
    wait()


if __name__ == "__main__":
    robot_init()
    pick_up()
    pick_down()
    robot_init()
    exit()
    map_navigation = MapNavigation()

    goal_1_forward = [2.008597469329834, -0.2450547420978546, 0.012209361671327345, 0.9999254629659047]  # 一号点姿态朝前
    goal_1_todesk = [2.008597469329834, -0.2450547420978546, -0.7528947966092002, 0.6812938245898885]  # 一号点对齐桌子姿态
    goal_1_backward = [1.4167612791061401, -0.2550547420978546, 0.9999994503016975, 0.0010485210073752217]  # 一号点姿态朝后
    goal_1_backward_todesk = [1.4167612791061401, -0.2550547420978546, -0.7528947966092002,
                              0.6812938245898885]  # 一号点姿态朝后

    goal_2_forward = [4.2723641395568848, 0.22977185249328613, 0.02547845365282761, 0.9996753715079014]  # 二号点姿态朝前
    goal_2_todesk = [3.7370169162750244, 0.141384916305542, 0.730520275085042, 0.6828910071817277]  # 二号点对齐桌子姿态

    goal_3_forward = [6.736099529266357, 0.22977185249328613, 0.016004544015015228, 0.999871919083075]  # 三号点姿态朝前
    goal_3_todesk = [6.736099529266357, 0.3297177255153656, 0.7171554527462124, 0.6969132346256419]  # 三号点对齐桌子姿态

    mr_angle_table = {
        "zero_position": [0, 0, 0, 0, 90, 0],
        "pick_init": [25.38, 41.45, -61.83, -81.06, 71.99, 34.64],
    }

    ml_angle_table = {
        "zero_position": [0, 0, 0, 0, 90, 0],
        "pick_init": [-28.02, 29.78, -77.2, 89.82, 61.69, -52.1],
    }

    x_goal, y_goal, orientation_z, orientation_w = goal_1_forward
    print("goal_1_forward", goal_1_forward)
    flag_goalReached = map_navigation.moveToGoal(x_goal, y_goal, orientation_z, orientation_w)  # 导航到一号点位
    if flag_goalReached:
        x_goal, y_goal, orientation_z, orientation_w = goal_1_todesk
        print("goal_1_forward", goal_1_todesk)
        map_navigation.moveToGoal(x_goal, y_goal, orientation_z, orientation_w)  # 调整姿态

        map_navigation.goStraight(0.1, 2.3)  # 往前走
        # 抓取
        exit()
        pick_up()
        print("pick")
        # time.sleep(5)  # 模拟抓取
        # sys.exit()  # 退出代码

        map_navigation.goBack(0.1, 3.7)  # 底座发送后退速度，防止导航撞到桌子

        x_goal, y_goal, orientation_z, orientation_w = goal_2_forward  # 导航到二号点位
        goal_2_forward_flag_goalReached = map_navigation.moveToGoal(x_goal, y_goal, orientation_z, orientation_w)
        if goal_2_forward_flag_goalReached:
            time.sleep(0.5)
            map_navigation.turnLeft(0.5, 3)
            time.sleep(0.1)

            map_navigation.goStraight(0.1, 3)  # 往前走

            # 放置
            # pick_down()
            print("load")
            exit()
            time.sleep(5)

            map_navigation.goBack(0.1, 3.5)  # 底座发送后退速度

            x_goal, y_goal, orientation_z, orientation_w = goal_1_backward
            goal_1_backward_flag_goalReached = map_navigation.moveToGoal(x_goal, y_goal, orientation_z,
                                                                         orientation_w)  # 回去一号点，姿态朝后
            if goal_1_backward_flag_goalReached:
                map_navigation.turnLeft(0.5, 3)
                time.sleep(0.1)
                map_navigation.goStraight(0.1, 2.5)  # 往前走

                # 抓取
                # pick_up()
                print("pick")
                time.sleep(5)
                map_navigation.goBack(0.1, 3.7)  # 底座发送后退速度，防止导航撞到桌子

                x_goal, y_goal, orientation_z, orientation_w = goal_3_forward  # 导航到三号点位
                flag_goalReached = map_navigation.moveToGoal(x_goal, y_goal, orientation_z, orientation_w)
                if flag_goalReached:
                    map_navigation.turnLeft(0.5, 3)
                    map_navigation.goStraight(0.1, 3)  # 往前走
                    # 放置
                    pick_down()
                    print("load")

                    time.sleep(5)
                    map_navigation.goBack(0.1, 3.5)  # 底座发送后退速度

                else:
                    print("goal_3_forward_failed")
            else:
                print("goal_1_backward_failed")
        else:
            print("goal_2_forward_failed")
    else:
        print("goal_1_forward_failed")
