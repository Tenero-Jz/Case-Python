#!/usr/bin/env python
import cv2
import numpy as np
import time
import typing as T
import stag
from pymycobot import Mercury
import rospy
import tf2_ros
import geometry_msgs.msg

mr = Mercury("/dev/right_arm")
ml = Mercury("/dev/left_arm")
ml.power_off()
mr.power_off()
ml.power_on()
mr.power_on()
ml.send_angles([0,0,0,0,90,0],20)
mr.send_angles([0,0,0,0,90,0],20)
class UVCCamera:
    def __init__(self, cam_index=0, mtx=None, dist=None, capture_size: T.Tuple[int, int] = (640, 480)):
        super().__init__()
        self.cam_index = cam_index
        self.mtx = mtx
        self.dist = dist
        self.curr_color_frame: T.Union[np.ndarray, None] = None
        self.capture_size = capture_size

    def capture(self):
        self.cap = cv2.VideoCapture(self.cam_index)
        width, height = self.capture_size
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

    def update_frame(self) -> bool:
        ret, self.curr_color_frame = self.cap.read()
        return ret

    def color_frame(self) -> T.Union[np.ndarray, None]:
        return self.curr_color_frame

    def release(self):
        self.cap.release()

# 夹爪工具长度
Tool_LEN = 175
# 相机中心到法兰距离
Camera_LEN = 78

np.set_printoptions(suppress=True, formatter={'float_kind': '{:.2f}'.format})

# 相机配置文件
camera_params = np.load("camera_params.npz")
mtx, dist = camera_params["mtx"], camera_params["dist"]

# 二维码大小
MARKER_SIZE = 32

# 设置左臂端口
ml = Mercury("/dev/left_arm")

# 将旋转矩阵转为欧拉角
def CvtRotationMatrixToEulerAngle(pdtRotationMatrix):
    pdtEulerAngle = np.zeros(3)
    pdtEulerAngle[2] = np.arctan2(pdtRotationMatrix[1, 0], pdtRotationMatrix[0, 0])
    fCosRoll = np.cos(pdtEulerAngle[2])
    fSinRoll = np.sin(pdtEulerAngle[2])
    pdtEulerAngle[1] = np.arctan2(-pdtRotationMatrix[2, 0], (fCosRoll * pdtRotationMatrix[0, 0]) + (fSinRoll * pdtRotationMatrix[1, 0]))
    pdtEulerAngle[0] = np.arctan2((fSinRoll * pdtRotationMatrix[0, 2]) - (fCosRoll * pdtRotationMatrix[1, 2]), (-fSinRoll * pdtRotationMatrix[0, 1]) + (fCosRoll * pdtRotationMatrix[1, 1]))
    return pdtEulerAngle

# 将欧拉角转为旋转矩阵
def CvtEulerAngleToRotationMatrix(ptrEulerAngle):
    ptrSinAngle = np.sin(ptrEulerAngle)
    ptrCosAngle = np.cos(ptrEulerAngle)
    ptrRotationMatrix = np.zeros((3, 3))
    ptrRotationMatrix[0, 0] = ptrCosAngle[2] * ptrCosAngle[1]
    ptrRotationMatrix[0, 1] = ptrCosAngle[2] * ptrSinAngle[1] * ptrSinAngle[0] - ptrSinAngle[2] * ptrCosAngle[0]
    ptrRotationMatrix[0, 2] = ptrCosAngle[2] * ptrSinAngle[1] * ptrCosAngle[0] + ptrSinAngle[2] * ptrSinAngle[0]
    ptrRotationMatrix[1, 0] = ptrSinAngle[2] * ptrCosAngle[1]
    ptrRotationMatrix[1, 1] = ptrSinAngle[2] * ptrSinAngle[1] * ptrSinAngle[0] + ptrCosAngle[2] * ptrCosAngle[0]
    ptrRotationMatrix[1, 2] = ptrSinAngle[2] * ptrSinAngle[1] * ptrCosAngle[0] - ptrCosAngle[2] * ptrSinAngle[0]
    ptrRotationMatrix[2, 0] = -ptrSinAngle[1]
    ptrRotationMatrix[2, 1] = ptrCosAngle[1] * ptrSinAngle[0]
    ptrRotationMatrix[2, 2] = ptrCosAngle[1] * ptrCosAngle[0]
    return ptrRotationMatrix

# 坐标转换为齐次变换矩阵，（x,y,z,rx,ry,rz）单位 rad
def Transformation_matrix(coord):
    position_robot = coord[:3]
    pose_robot = coord[3:]
    # 将欧拉角转为旋转矩阵
    RBT = CvtEulerAngleToRotationMatrix(pose_robot)
    PBT = np.array([[position_robot[0]], [position_robot[1]], [position_robot[2]]])
    temp = np.concatenate((RBT, PBT), axis=1)
    array_1x4 = np.array([[0, 0, 0, 1]])
    # 将两个数组按行拼接起来
    matrix = np.concatenate((temp, array_1x4), axis=0)
    return matrix

def Eyes_in_hand_left(coord, camera):
    # 相机坐标
    Position_Camera = np.transpose(camera[:3])
    # 机械臂坐标矩阵
    Matrix_BT = Transformation_matrix(coord)
    # 手眼矩阵
    Matrix_TC = np.array([
        [0, -1, 0, Camera_LEN],
        [1, 0, 0, 0],
        [0, 0, 1, -Tool_LEN],
        [0, 0, 0, 1]
    ])
    # 物体坐标（相机系）
    Position_Camera = np.append(Position_Camera, 1)
    # 物体坐标（基坐标系）
    Position_B = Matrix_BT @ Matrix_TC @ Position_Camera
    return Position_B

# 等待机械臂运行结束
def waitl():
    time.sleep(0.2)
    while ml.is_moving():
        time.sleep(0.03)

# 获取物体坐标(相机系)
def calc_markers_base_position(corners: T.List[np.ndarray], ids: T.List[int], marker_size: int, mtx: np.ndarray, dist: np.ndarray) -> T.List[np.ndarray]:
    if len(corners) == 0:
        return []
    # 通过二维码角点获取物体旋转向量和平移向量
    rvecs, tvecs = solve_marker_pnp(corners, marker_size, mtx, dist)
    for i, tvec, rvec in zip(ids, tvecs, rvecs):
        tvec = tvec.squeeze().tolist()
        rvec = rvec.squeeze().tolist()
        rotvector = np.array([[rvec[0], rvec[1], rvec[2]]])
        # 将旋转向量转为旋转矩阵
        Rotation = cv2.Rodrigues(rotvector)[0]
        # 将旋转矩阵转为欧拉角
        Euler = CvtRotationMatrixToEulerAngle(Rotation)
        # 物体坐标(相机系)
        target_coords = np.array([tvec[0], tvec[1], tvec[2], Euler[0], Euler[1], Euler[2]])
        return target_coords

def publish_transform():
    rospy.init_node('my_tf_broadcaster')
    br = tf2_ros.TransformBroadcaster()
    t = geometry_msgs.msg.TransformStamped()

    t.header.stamp = rospy.Time.now()
    t.header.frame_id = "base_footprint"
    t.child_frame_id = "base_link"
    t.transform.translation.x = 0.0
    t.transform.translation.y = 0.0
    t.transform.translation.z = 0.0
    t.transform.rotation.x = 0.0
    t.transform.rotation.y = 0.0
    t.transform.rotation.z = 0.0
    t.transform.rotation.w = 1.0

    rate = rospy.Rate(10.0)
    while not rospy.is_shutdown():
        t.header.stamp = rospy.Time.now()
        br.sendTransform(t)
        rate.sleep()


if __name__ == "__main__":
        camera = UVCCamera(6, mtx, dist)
        # 打开摄像头open camera(ok)
        camera.capture()
        while True:
            camera.update_frame()
            frame = camera.color_frame()
            (corners, ids, rejected_corners) = stag.detectMarkers(frame, 11)
            marker_pos_pack = calc_markers_base_position(corners, ids, MARKER_SIZE, mtx, dist)
            print(marker_pos_pack)
            cv2.imshow("test", frame)
            cv2.waitKey(1)
