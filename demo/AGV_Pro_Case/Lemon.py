import cv2
import numpy as np
import time
from pymycobot import ElephantRobot
from pyorbbecsdk import *
from utils import frame_to_bgr_image
from pymycobot import Pro630Client


# 相机初始化类
class OrbbecCamera:
    def __init__(self):
        self.cameraMatrix = np.array([
            [517.532776, 0.0, 321.615479],
            [0.0, 517.502808, 236.746033],
            [0.0, 0.0, 1.0]
        ], dtype=np.float64)
        self.distCoeffs = np.array(
            [47.747471, -99.448395, 0.000553, -0.000151, 121.854881, 47.591953, -99.191154, 122.301498],
            dtype=np.float64)

        self.config = Config()
        self.pipeline = Pipeline()

        profile_color = self.pipeline.get_stream_profile_list(OBSensorType.COLOR_SENSOR).get_video_stream_profile(640,
                                                                                                                  0,
                                                                                                                  OBFormat.RGB,
                                                                                                                  30)
        profile_depth = self.pipeline.get_stream_profile_list(OBSensorType.DEPTH_SENSOR).get_video_stream_profile(640,
                                                                                                                  400,
                                                                                                                  OBFormat.Y16,
                                                                                                                  30)

        self.config.enable_stream(profile_color)
        self.config.enable_stream(profile_depth)
        self.config.set_align_mode(OBAlignMode.HW_MODE)
        self.pipeline.enable_frame_sync()
        self.pipeline.start(self.config)

    def get_frame(self):
        frames = self.pipeline.wait_for_frames(1000)
        if frames is None:
            return None, None, None
        color_frame = frames.get_color_frame()
        depth_frame = frames.get_depth_frame()
        if color_frame is None or depth_frame is None:
            return None, None, None

        color_image = frame_to_bgr_image(color_frame)
        width = depth_frame.get_width()
        height = depth_frame.get_height()
        scale = depth_frame.get_depth_scale()

        depth_data = np.frombuffer(depth_frame.get_data(), dtype=np.uint16).reshape((height, width))
        depth_data = depth_data.astype(np.float32) * scale
        return color_image, depth_data.astype(np.uint16), scale

    def get_coords(self, cx, cy, depth_data):
        try:
            cam_Z = depth_data[cy, cx]
            point = np.array([cx, cy], dtype=np.float32)
            undistorted = cv2.undistortPoints(point[None, None, :], self.cameraMatrix, self.distCoeffs)
            x_norm = undistorted[0, 0, 0]
            y_norm = undistorted[0, 0, 1]
            cam_X = round(x_norm * cam_Z, 2)
            cam_Y = round(y_norm * cam_Z, 2)
            return [cam_X, cam_Y, cam_Z]
        except Exception as e:
            print("获取坐标出错:", e)
            return [0, 0, 0]


# 颜色识别柠檬（黄色）
def detect_lemon(image):
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    lower_yellow = np.array([20, 100, 100])
    upper_yellow = np.array([35, 255, 255])
    mask = cv2.inRange(hsv, lower_yellow, upper_yellow)

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if contours:
        c = max(contours, key=cv2.contourArea)
        (x, y), radius = cv2.minEnclosingCircle(c)
        if radius > 10:  # 忽略小物体
            return int(x), int(y), int(radius)
    return None


# 控制机械臂抓取柠檬
def pick_lemon(robot: ElephantRobot, target_coords):
    X, Y, Z = target_coords
    print("机械臂移动到柠檬上方")
    robot.write_coords([X, Y, Z + 100, 180, 0, -90], 2000)
    robot.command_wait_done()

    print("下降夹取")
    robot.jog_relative("Z", -100, 1000, 1)
    robot.command_wait_done()

    robot.set_gripper_value(30, 100)
    robot.wait(1)

    print("抬升")
    robot.jog_relative("Z", 100, 1000, 0)
    robot.command_wait_done()

    print("移动至放置区")
    robot.write_coords([200, -200, 250, 180, 0, -90], 2000)
    robot.command_wait_done()

    robot.set_gripper_value(100, 100)
    robot.wait(1)

    print("回安全位置")
    robot.write_angles([94.828, -143.513, 135.283, -82.969, -87.257, -44.033], 1000)
    robot.command_wait_done()


# 主程序
if __name__ == "__main__":
    # 初始化相机
    cam = OrbbecCamera()

    # 初始化机械臂
    robot = ElephantRobot("192.168.137.182", 5001)
    robot.start_client()
    time.sleep(1)
    robot.set_gripper_mode(0)
    robot.set_gripper_state(1, 100)
    time.sleep(1)

    while True:
        color_img, depth_img, _ = cam.get_frame()
        if color_img is None:
            continue

        result = detect_lemon(color_img)
        if result:
            cx, cy, r = result
            cv2.circle(color_img, (cx, cy), r, (0, 255, 0), 2)
            cv2.circle(color_img, (cx, cy), 5, (0, 0, 255), -1)
            coords = cam.get_coords(cx, cy, depth_img)
            print("识别柠檬坐标:", coords)
            text = f"{coords[0]:.1f}, {coords[1]:.1f}, {coords[2]:.1f}"
            cv2.putText(color_img, text, (cx + 10, cy - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            # pick_lemon(robot, coords)
            # break

        cv2.imshow("lemon detect", color_img)
        if cv2.waitKey(1) & 0xFF == 27:
            break

    cv2.destroyAllWindows()
