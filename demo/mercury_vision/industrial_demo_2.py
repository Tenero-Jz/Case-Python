import threading
import rospy
import time
import sys
import actionlib

from pymycobot import Mercury

from actionlib_msgs.msg import *
from actionlib_msgs.msg import GoalID
from move_base_msgs.msg import MoveBaseAction, MoveBaseGoal
from geometry_msgs.msg import Point
from geometry_msgs.msg import Twist
from geometry_msgs.msg import PoseWithCovarianceStamped
from tf.transformations import quaternion_from_euler


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


def l_down():
    ml.send_base_coord(3, 218, 30)


def l_down_2():
    ml.send_base_coord(3, 200, 30)


def r_down():
    mr.send_base_coord(3, 225, 30)


def r_down_2():
    mr.send_base_coord(3, 210, 30)


def l_up():
    ml.send_base_coord(3, 300, 30)


def r_up():
    mr.send_base_coord(3, 300, 30)


def r_gripper_open():
    mr.set_gripper_value(90, 100)


def r_gripper_close():
    mr.set_gripper_value(0, 100)


def l_gripper_open():
    ml.set_gripper_value(90, 100)


def l_gripper_close():
    ml.set_gripper_value(0, 100)


def pick_up_1():
    mr.send_angles(mr_angle_table["pick_init"], angle_move_speed)
    ml.send_angles(ml_angle_table["pick_init"], angle_move_speed)
    # 等待机械臂运动结束
    waitl()
    # 向下夹取
    threading.Thread(target=r_gripper_open, args=()).start()
    threading.Thread(target=l_gripper_open, args=()).start()
    time.sleep(2)
    threading.Thread(target=l_down, args=()).start()
    threading.Thread(target=r_down, args=()).start()
    waitl()
    # 夹取完向上运动
    threading.Thread(target=r_gripper_close, args=()).start()
    threading.Thread(target=l_gripper_close, args=()).start()
    time.sleep(2)
    threading.Thread(target=l_up, args=()).start()
    threading.Thread(target=r_up, args=()).start()
    waitl()


def pick_up_2():
    mr.send_angles(mr_angle_table["pick_init"], angle_move_speed)
    ml.send_angles(ml_angle_table["pick_init"], angle_move_speed)
    # 等待机械臂运动结束
    waitl()
    # 向下夹取
    threading.Thread(target=r_gripper_open, args=()).start()
    threading.Thread(target=l_gripper_open, args=()).start()
    time.sleep(2)
    threading.Thread(target=l_down_2, args=()).start()
    threading.Thread(target=r_down_2, args=()).start()
    waitl()
    # 夹取完向上运动
    threading.Thread(target=r_gripper_close, args=()).start()
    threading.Thread(target=l_gripper_close, args=()).start()
    time.sleep(2)
    threading.Thread(target=l_up, args=()).start()
    threading.Thread(target=r_up, args=()).start()
    waitl()


def pick_down():
    # 向下放置
    threading.Thread(target=l_down, args=()).start()
    threading.Thread(target=r_down, args=()).start()
    waitl()
    threading.Thread(target=r_gripper_open, args=()).start()
    threading.Thread(target=l_gripper_open, args=()).start()
    time.sleep(2)
    # 放置完回到初始位
    threading.Thread(target=l_up, args=()).start()
    threading.Thread(target=r_up, args=()).start()
    waitl()


def load():
    mr_coords = mr.get_base_coords()  # 获取当前左臂位姿
    ml_coords = ml.get_base_coords()  # 获取当前左臂位姿

    mr_coords[2] -= 50  # z轴下降
    ml_coords[2] -= 50  # z轴下降

    mr.send_base_coords(mr_coords, coord_move_speed)  # 坐标控制
    ml.send_base_coords(ml_coords, coord_move_speed)  # 坐标控制
    waitl()

    mr.set_gripper_value(50, 50)
    ml.set_gripper_value(50, 50)


# 等待机械臂运行结束
def waitl():
    time.sleep(0.2)
    while (ml.is_moving()) or (mr.is_moving()):
        time.sleep(0.03)


if __name__ == "__main__":
    ml = Mercury("/dev/left_arm")  # 设置左臂端口
    mr = Mercury("/dev/right_arm")  # 设置右臂端口
    map_navigation = MapNavigation()

    angle_move_speed = 10  # 关节控制速度
    coord_move_speed = 10  # 坐标控制速度

    # Tool_LEN = 175
    # # 设置工具坐标系
    # ml.set_tool_reference([0, 0, Tool_LEN, 0, 0, 0])
    # # 将末端坐标系设置为工具
    # ml.set_end_type(1)

    # # 设置工具坐标系
    # mr.set_tool_reference([0, 0, Tool_LEN, 0, 0, 0])
    # # 将末端坐标系设置为工具
    # mr.set_end_type(1)

    ml.set_gripper_mode(0)
    mr.set_gripper_mode(0)

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
        "pick_init": [25.38, 41.45, -61.83, -81.06, 71.99, 42],
    }

    ml_angle_table = {
        "zero_position": [0, 0, 0, 0, 90, 0],
        "pick_init": [-24.99, 41.45, -61.83, 81.06, 65.99, -50.99],
        # [-28.02, 29.78, -77.2, 89.82, 61.69, -52.1],
    }

    x_goal, y_goal, orientation_z, orientation_w = goal_1_forward
    print("goal_1_forward", goal_1_forward)
    flag_goalReached = map_navigation.moveToGoal(x_goal, y_goal, orientation_z, orientation_w)  # 导航到一号点位
    if flag_goalReached:
        x_goal, y_goal, orientation_z, orientation_w = goal_1_todesk
        print("goal_1_forward", goal_1_todesk)
        map_navigation.moveToGoal(x_goal, y_goal, orientation_z, orientation_w)  # 调整姿态

        map_navigation.goStraight(0.1, 2.5)  # 往前走
        # 抓取
        pick_up_1()
        print("pick")
        # time.sleep(5)  # 模拟抓取

        map_navigation.goBack(0.1, 3.7)  # 底座发送后退速度，防止导航撞到桌子

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
            # time.sleep(5)

            map_navigation.goBack(0.1, 3.5)  # 底座发送后退速度

            x_goal, y_goal, orientation_z, orientation_w = goal_1_backward
            goal_1_backward_flag_goalReached = map_navigation.moveToGoal(x_goal, y_goal, orientation_z,
                                                                         orientation_w)  # 回去一号点，姿态朝后
            if goal_1_backward_flag_goalReached:
                map_navigation.turnLeft(0.5, 3)
                time.sleep(0.1)
                map_navigation.goStraight(0.1, 2.5)  # 往前走

                # 抓取
                pick_up_2()
                print("pick")
                # time.sleep(5)
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
