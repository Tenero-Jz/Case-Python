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
ml.clear_error_information()
mr.clear_error_information()

ml_obj = camera_detect(2, 32, mtx, dist, 0)  # 1摄像头id， 2stag码大小 ，3、4相机配置文件，5:0左臂，1右臂
mr_obj = camera_detect(6, 32, mtx, dist, 1)
sp = 30  # 设置移动速度
# ml_obj.camera_open()
# ml_obj.camera_open_loop() # 打开左相机循环


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


def l_init():
    ml.send_angles([-32.4, 37.79, -58.87, 86.77, 60.72, -131.52], sp)


def r_init():
    mr.send_angles([32.86, 44.99, -53.5, -89.3, 61.97, 130.1], sp)


def camera_get_coords():
    ml_obj.camera_open()  # 打开相机
    time.sleep(0.5)
    try:
        target_l = ml_obj.stag_robot_identify(ml)   # 获取不到报错，移动位置再次获取
    except:
        try:
            ml.send_angles([-33.44, 7.7, -71.74, 99.25, 60.23, -111.31], sp)
            waitL()
            target_l = ml_obj.stag_robot_identify(ml)
        except:
            ml_obj.release()
            raise ValueError
    ml_obj.release()

    mr_obj.camera_open()
    time.sleep(0.5)
    try:
        target_r = mr_obj.stag_robot_identify(mr)
    except:
        try:
            mr.send_angles([30.35, 23.64, -69.67, -92.81, 62.45, 120.91], sp)
            waitR()
            target_r = mr_obj.stag_robot_identify(mr)
        except:
            mr_obj.release()
            raise ValueError
    mr_obj.release()
    print(target_l, target_r)
    return target_l, target_r


def l_catch(target_l):
    l_coords = ml.get_base_coords()  # 获取机械臂当前坐标，为了获取旋转角rxryrz
    ml.send_angles([-23.91, 3.85, -48.87, 110.99, 75.18, -86.55], sp)
    waitL()
    ml.send_angles([26.99, 17.75, -39.33, 78.08, 114.55, -85.07], sp)  # 防止坐标到限位
    waitL()
    # ml.send_base_coord(3, 150, sp)
    # waitL()
    l_coords[0] = target_l[0] + 50
    l_coords[1] = target_l[1] + 101
    l_coords[2] = 100
    ml.send_base_coords(l_coords, sp)
    waitL()
    # ml.send_angle(6, -102, sp)


def r_catch(target_r):
    r_coords = mr.get_base_coords()  # 获取机械臂当前坐标
    mr.send_angles([33.94, 4.36, -52.98, -117.05, 73.42, 82.47], sp)
    waitR()
    mr.send_angles([-22.86, 12.6, -47.56, -83.46, 112.61, 90.48], sp)
    waitR()
    # mr.send_base_coord(3, 160, sp)
    # waitR()
    r_coords[0] = target_r[0] + 30
    r_coords[1] = target_r[1] - 109
    r_coords[2] = 110
    mr.send_base_coords(r_coords, sp)
    waitR()


def l_up():
    l_coords = ml.get_base_coords()  # 获取机械臂当前坐标
    l_coords[1] = 312
    l_coords[2] = 250
    ml.send_base_coords(l_coords, sp)
    # ml.send_base_coord(3, 250, sp)


def r_up():
    r_coords = mr.get_base_coords()  # 获取机械臂当前坐标
    r_coords[1] = -312
    r_coords[2] = 250
    mr.send_base_coords(r_coords, sp)
    # mr.send_base_coord(3, 250, sp)


def pick_up():
    target_l, target_r = camera_get_coords()
    l_catch(target_l)
    r_catch(target_r)
    # exit()
    # threading.Thread(target=l_down, args=(target_l,)).start()
    # threading.Thread(target=r_down, args=(target_r,)).start()
    wait()
    # l_up()
    # r_up()
    threading.Thread(target=l_up, args=()).start()
    threading.Thread(target=r_up, args=()).start()
    wait()


def l_down():
    ml.send_base_coord(3, 150, sp)


def r_down():
    mr.send_base_coord(3, 150, sp)


def l_leave():
    ml.send_base_coord(2, 350, sp)


def l_up_2():
    ml.send_base_coord(3, 310, sp)


def r_leave():
    mr.send_base_coord(2, -350, sp)


def r_up_2():
    mr.send_base_coord(3, 310, sp)


def pick_down():
    # 向下放置
    threading.Thread(target=l_down, args=()).start()
    threading.Thread(target=r_down, args=()).start()
    wait()
    threading.Thread(target=l_leave, args=()).start()
    threading.Thread(target=r_leave, args=()).start()
    wait()
    threading.Thread(target=l_up_2, args=()).start()
    threading.Thread(target=r_up_2, args=()).start()
    wait()
    threading.Thread(target=l_init, args=()).start()
    threading.Thread(target=r_init, args=()).start()
    wait()


def load():
    mr_coords = mr.get_base_coords()  # 获取当前左臂位姿
    ml_coords = ml.get_base_coords()  # 获取当前左臂位姿

    mr_coords[2] -= 50  # z轴下降
    ml_coords[2] -= 50  # z轴下降

    mr.send_base_coords(mr_coords, 50)  # 坐标控制
    ml.send_base_coords(ml_coords, 50)  # 坐标控制
    wait()

    mr.set_gripper_value(50, 50)
    ml.set_gripper_value(50, 50)


def robot_init():
    # ml.send_base_coord(2, 180, 10)
    # mr.send_base_coord(2, -180, 10)
    # wait()

    # mr.send_angles([49.08, 75.33, -12.34, -91.7, 46, 120.18], sp)
    # ml.send_angles([-49.08, 75.33, -12.34, 91.7, 46, -110.18], sp)
    # wait()
    threading.Thread(target=l_init, args=()).start()
    threading.Thread(target=r_init, args=()).start()
    wait()


if __name__ == "__main__":
    robot_init()
    # pick_up()
    # pick_down()
    # exit()
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

        map_navigation.goStraight(0.1, 1.4)  # 往前走
        # 抓取
        # exit()
        pick_up()
        print("pick")
        # time.sleep(5)  # 模拟抓取
        # sys.exit()  # 退出代码
        map_navigation.goBack(0.1, 3.7)  # 底座发送后退速度，防止导航撞到桌子
    else:
        print("goal_1_forward_failed")

    for i in range(3):
        x_goal, y_goal, orientation_z, orientation_w = goal_2_forward  # 导航到二号点位
        goal_2_forward_flag_goalReached = map_navigation.moveToGoal(x_goal, y_goal, orientation_z, orientation_w)
        if goal_2_forward_flag_goalReached:
            time.sleep(0.5)
            map_navigation.turnLeft(0.5, 3)
            time.sleep(0.1)

            map_navigation.goStraight(0.1, 3)  # 往前走

            # 放置
            pick_down()
            print("load")
            # exit()
            time.sleep(5)

            map_navigation.goBack(0.1, 3.5)  # 底座发送后退速度

            x_goal, y_goal, orientation_z, orientation_w = goal_1_backward
            goal_1_backward_flag_goalReached = map_navigation.moveToGoal(x_goal, y_goal, orientation_z,
                                                                         orientation_w)  # 回去一号点，姿态朝后
            if goal_1_backward_flag_goalReached:
                map_navigation.turnLeft(0.5, 3.2)
                time.sleep(0.3)
                map_navigation.goStraight(0.1, 3.7)  # 往前走

                # 抓取
                pick_up()
                print("pick")

                # time.sleep(5)
                map_navigation.goBack(0.1, 3.7)  # 底座发送后退速度，防止导航撞到桌子

                # x_goal, y_goal, orientation_z, orientation_w = goal_3_forward  # 导航到三号点位
                # flag_goalReached = map_navigation.moveToGoal(x_goal, y_goal, orientation_z, orientation_w)
                # if flag_goalReached:
                #     map_navigation.turnLeft(0.5, 3)
                #     map_navigation.goStraight(0.1, 3)  # 往前走
                #     # 放置
                #     pick_down()
                #     print("load")
                #
                #     time.sleep(5)
                #     map_navigation.goBack(0.1, 3.5)  # 底座发送后退速度
                #
                # else:
                #     print("goal_3_forward_failed")
            else:
                print("goal_1_backward_failed")
        else:
            print("goal_2_forward_failed")
