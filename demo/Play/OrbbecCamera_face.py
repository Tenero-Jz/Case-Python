import cv2
import numpy as np
import time
from pymycobot import ElephantRobot
from pyorbbecsdk import *


def frame_to_bgr_image(frame):
    data = frame.get_data()
    img = np.frombuffer(data, dtype=np.uint8).reshape((frame.get_height(), frame.get_width(), 3))
    return cv2.cvtColor(img, cv2.COLOR_RGB2BGR)


# 相机初始化类
class OrbbecCamera:
    def __init__(self):
        self.cameraMatrix = np.array([
            [517.532776, 0.0, 321.615479],
            [0.0, 517.502808, 236.746033],
            [0.0, 0.0, 1.0]
        ], dtype=np.float64)
        self.distCoeffs = np.array(
            [47.747471, -99.448395, 0.000553, -0.000151, 121.854881,
             47.591953, -99.191154, 122.301498],
            dtype=np.float64)

        self.config = Config()
        self.pipeline = Pipeline()

        profile_color = self.pipeline.get_stream_profile_list(OBSensorType.COLOR_SENSOR).get_video_stream_profile(
            640, 0, OBFormat.RGB, 30)
        profile_depth = self.pipeline.get_stream_profile_list(OBSensorType.DEPTH_SENSOR).get_video_stream_profile(
            640, 400, OBFormat.Y16, 30)

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


face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")


def detect_face(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.2, minNeighbors=5, minSize=(60, 60))
    if len(faces) > 0:
        # 取最大的人脸
        x, y, w, h = max(faces, key=lambda rect: rect[2] * rect[3])
        cx, cy = x + w // 2, y + h // 2
        return cx, cy, w, h
    return None


def draw_fancy_box(img, x, y, w, h, color=(230, 216, 173), thickness=2, length=20):
    """绘制四角框"""
    cv2.line(img, (x, y), (x + length, y), color, thickness)
    cv2.line(img, (x, y), (x, y + length), color, thickness)

    cv2.line(img, (x + w, y), (x + w - length, y), color, thickness)
    cv2.line(img, (x + w, y), (x + w, y + length), color, thickness)

    cv2.line(img, (x, y + h), (x + length, y + h), color, thickness)
    cv2.line(img, (x, y + h), (x, y + h - length), color, thickness)

    cv2.line(img, (x + w, y + h), (x + w - length, y + h), color, thickness)
    cv2.line(img, (x + w, y + h), (x + w, y + h - length), color, thickness)


def follow_face(robot: ElephantRobot, coords):
    X, Y, Z = coords
    print("人脸坐标:", coords)
    target = [X, Y, Z + 300, 180, 0, -90]
    robot.write_coords(target, 1000)
    robot.command_wait_done()


if __name__ == "__main__":
    cam = OrbbecCamera()

    # robot = ElephantRobot("192.168.137.182", 5001)
    # robot.start_client()
    # time.sleep(1)

    while True:
        color_img, depth_img, _ = cam.get_frame()
        if color_img is None:
            continue

        result = detect_face(color_img)
        if result:
            cx, cy, w, h = result
            x, y = cx - w // 2, cy - h // 2

            draw_fancy_box(color_img, x, y, w, h, color=(230, 216, 173), thickness=2, length=25)

            cv2.circle(color_img, (cx, cy), 5, (255, 255, 255), -1)

            print("成功识别人脸")
            coords = cam.get_coords(cx, cy, depth_img)
            text = f"{coords[0]:.1f}, {coords[1]:.1f}, {coords[2]:.1f}"
            cv2.putText(color_img, text, (cx + 10, cy - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 1)

            # 跟随人脸
            # follow_face(robot, coords)

        cv2.imshow("face detect", color_img)
        if cv2.waitKey(1) & 0xFF == 27:  # ESC退出
            break

    cv2.destroyAllWindows()
