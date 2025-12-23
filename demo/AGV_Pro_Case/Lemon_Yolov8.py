import cv2
import numpy as np
import time
from pymycobot import ElephantRobot
from pyorbbecsdk import *
from utils import frame_to_bgr_image
from ultralytics import YOLO  # 新增：导入YOLO模型


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

    # def get_frame(self):
    #     frames = self.pipeline.wait_for_frames(100)
    #     if frames is None:
    #         return None, None, None
    #     color_frame = frames.get_color_frame()
    #     depth_frame = frames.get_depth_frame()
    #     if color_frame is None or depth_frame is None:
    #         return None, None, None
    #
    #     color_image = frame_to_bgr_image(color_frame)
    #     width = 480  # depth_frame.get_width()
    #     height = 640  # depth_frame.get_height()
    #     print("Depth frame size:", depth_frame.get_width(), depth_frame.get_height())
    #     scale = depth_frame.get_depth_scale()
    #
    #     # depth_data = np.frombuffer(depth_frame.get_data(), dtype=np.uint16).reshape((height, width))
    #     depth_data = np.asarray(depth_frame.get_data(), dtype=np.uint16).reshape((height, width)).copy()
    #     if not depth_data.flags['C_CONTIGUOUS']:
    #         depth_data = np.ascontiguousarray(depth_data)
    #
    #     depth_data = depth_data.astype(np.float32) * scale
    #     return color_image, depth_data.astype(np.uint16), scale
    def get_frame(self):
        frames = self.pipeline.wait_for_frames(100)
        if frames is None:
            return None, None, None
        color_frame = frames.get_color_frame()
        depth_frame = frames.get_depth_frame()
        if color_frame is None or depth_frame is None:
            return None, None, None

        color_image = frame_to_bgr_image(color_frame)

        width = depth_frame.get_width()  # 640
        height = depth_frame.get_height()  # 480
        scale = depth_frame.get_depth_scale()

        depth_bytes = np.array(depth_frame.get_data(), dtype=np.uint8).copy()
        depth_raw = depth_bytes.view(np.uint16)
        depth_data = depth_raw.reshape((height, width))
        # print("Depth data shape:", depth_data.shape)
        # print("Depth data dtype:", depth_data.dtype)

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


# YOLO识别柠檬
model = YOLO("best.pt")


def detect_lemon(image):
    results = model(image)[0]  # 推理
    for box in results.boxes:
        cls_id = int(box.cls.item())
        conf = box.conf.item()
        if conf < 0.5:
            continue
        x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
        cx = (x1 + x2) // 2
        cy = (y1 + y2) // 2
        radius = max((x2 - x1), (y2 - y1)) // 2
        return cx, cy, radius
    return None


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


if __name__ == "__main__":
    cam = OrbbecCamera()

    # robot = ElephantRobot("192.168.137.182", 5001)
    # robot.start_client()
    # time.sleep(1)
    # robot.set_gripper_mode(0)
    # robot.set_gripper_state(1, 100)
    # time.sleep(1)

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
            text = f"{coords[0]:.1f}, {coords[1]:.1f}, {coords[2]:.1f}"
            print("识别柠檬坐标:", text)
            cv2.putText(color_img, text, (cx + 10, cy - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            # pick_lemon(robot, coords)
            # break

        cv2.imshow("lemon detect", color_img)
        if cv2.waitKey(1) & 0xFF == 27:
            break

    cv2.destroyAllWindows()
