# ******************************************************************************
#  Copyright (c) 2023 Orbbec 3D Technology, Inc
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http:# www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
# ******************************************************************************
import cv2

from pyorbbecsdk import *
import numpy as np
from utils import frame_to_bgr_image
import time

ESC_KEY = 27

PRINT_INTERVAL = 1  # seconds
MIN_DEPTH = 20  # 20mm
MAX_DEPTH = 10000  # 10000mm
cx = None
cy = None


# 创建回调函数用于处理鼠标事件
def mouse_callback(event, x, y, flags, param):
    global cx, cy
    """
    鼠标回调函数，用于捕获鼠标事件
    """
    # 当鼠标左键按下时
    if event == cv2.EVENT_LBUTTONDOWN:
        print(f"左键点击 - 坐标: ({x}, {y})")
        cx = x
        cy = y


class TemporalFilter:
    def __init__(self, alpha):
        self.alpha = alpha
        self.previous_frame = None

    def process(self, frame):
        if self.previous_frame is None:
            result = frame
        else:
            result = cv2.addWeighted(frame, self.alpha, self.previous_frame, 1 - self.alpha, 0)
        self.previous_frame = result
        return result


class Orbbec_Camare:
    def __init__(self):
        self.cameraMatrix = np.array([
            [517.532776, 0.0, 321.615479],  # [fx, 0, cx]
            [0.0, 517.502808, 236.746033],  # [0, fy, cy]
            [0.0, 0.0, 1.0]  # [0, 0, 1]
        ], dtype=np.float64)
        self.distCoeffs = np.array([
            47.747471,  # k1
            -99.448395,  # k2
            0.000553,  # p1
            -0.000151,  # p2
            121.854881,  # k3
            47.591953,  # k4
            -99.191154,  # k5
            122.301498  # k6
        ], dtype=np.float64)
        self.config = Config()
        self.pipeline = Pipeline()
        self.temporal_filter = TemporalFilter(alpha=0.5)
        try:
            profile_list = self.pipeline.get_stream_profile_list(OBSensorType.COLOR_SENSOR)
            profile_list2 = self.pipeline.get_stream_profile_list(OBSensorType.DEPTH_SENSOR)
            try:
                color_profile = profile_list.get_video_stream_profile(640, 0, OBFormat.RGB, 30)
                depth_profile = profile_list2.get_video_stream_profile(640, 400, OBFormat.Y16, 30)
            except OBError as e:
                print(e)
                color_profile = profile_list.get_default_video_stream_profile()
                print("color profile: ", color_profile)
            self.config.enable_stream(color_profile)
            self.config.enable_stream(depth_profile)
        except Exception as e:
            print(e)
            return
        self.config.set_align_mode(OBAlignMode.HW_MODE)
        self.pipeline.enable_frame_sync()
        self.pipeline.start(self.config)
        # time.sleep(2)
        # frames = self.pipeline.wait_for_frames(100)
        # for i in range(10):
        #     color_frame = frames.get_color_frame()

    def get_frame_data(self):
        while 1:
            try:
                frames = self.pipeline.wait_for_frames(100)
                if frames is None:
                    continue
                color_frame = frames.get_color_frame()
                if color_frame is None:
                    continue
                # covert to RGB format
                color_image = frame_to_bgr_image(color_frame)
                depth_frame = frames.get_depth_frame()
                if depth_frame is None:
                    continue
                width = depth_frame.get_width()
                height = depth_frame.get_height()
                scale = depth_frame.get_depth_scale()

                depth_data = np.frombuffer(depth_frame.get_data(), dtype=np.uint16)
                depth_data = depth_data.reshape((height, width))

                depth_data = depth_data.astype(np.float32) * scale

                depth_data = depth_data.astype(np.uint16)
                # Apply temporal filtering
                depth_data = self.temporal_filter.process(depth_data)

                depth_image = cv2.normalize(depth_data, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)
                # print("center_distance=",center_distance )
                depth_image = cv2.applyColorMap(depth_image, cv2.COLORMAP_JET)

                # cv2.imshow("Color Viewer", color_image)

                # cv2.imshow("Depth Viewer", depth_image)
                # key = cv2.waitKey(1)
                # if key == ord('q') or key == ESC_KEY:
                #     break

                if color_image is not None:
                    return [color_image, depth_image, depth_data]

            except:
                print("fail")
                break

    def close_cam(self):
        self.pipeline.stop()

    def get_cam_coords(self, cx, cy, depth_data):
        # cam_Z=depth_data[cy,cx]
        #     # cam_Z=depth_data[max(0,cy-10):min(cy+479), max(0,cx-10):min(cx+10,639)]
        # points = np.array([cx, cy], dtype=np.float32)
        # undistorted = cv2.undistortPoints(points, self.cameraMatrix,self.distCoeffs)

        # x_norm = undistorted[0,0,0]
        # y_norm = undistorted[0,0,1]
        # cam_X = round(x_norm * cam_Z, 2)
        # cam_Y = round(y_norm * cam_Z, 2)
        # return [cam_X,cam_Y,cam_Z]
        # if cy >480:
        #     cy=479
        # if cx >640:
        #     cx=639
        try:
            cam_Z = depth_data[cy, cx]
            # cam_Z=depth_data[max(0,cy-10):min(cy+479), max(0,cx-10):min(cx+10,639)]
            points = np.array([cx, cy], dtype=np.float32)
            undistorted = cv2.undistortPoints(points, self.cameraMatrix, self.distCoeffs)

            x_norm = undistorted[0, 0, 0]
            y_norm = undistorted[0, 0, 1]
            cam_X = round(x_norm * cam_Z, 2)
            cam_Y = round(y_norm * cam_Z, 2)
            return [cam_X, cam_Y, cam_Z]
        except Exception as e:
            print(f"发生错误: {e}")
            return [0, 0, 0]


if __name__ == "__main__":
    cam = Orbbec_Camare()
    save_count = 0
    cv2.namedWindow('color')
    cv2.namedWindow('color2')
    cv2.setMouseCallback('color2', mouse_callback)
    cv2.setMouseCallback('color', mouse_callback)

    while 1:
        result = cam.get_frame_data()

        if result[0] is not None:
            cv2.imshow("color", result[0])
        if result[1] is not None:
            cv2.imshow("color2", result[1])
            # print(cx,cy)
            if cx is not None and cy is not None:
                # print("dkvmkdmvkdmv")
                print(cam.get_cam_coords(cx, cy, result[-1]))
                cx = None
                cy = None
        key = cv2.waitKey(1)

        # 按下空格键保存图片
        if key == 32:  # 32是空格键的ASCII码
            filename = f"captured_image_{save_count}.jpg"
            cv2.imwrite(filename, result[0])
            print(f"Saved: {filename}")
            save_count += 1  # 计数器递增
        # if result[1] is not None:
        #     cv2.imshow("depth",result[1])
        # if result[2] is not None:
        #     print(cam.get_cam_coords(320,240,result[2]))

        # cv2.waitKey(1)
        # de=cam.get_depth_frame()
        # cv2.imshow("color",result)
        # if de[0].any():
        #     cv2.imshow("de",de[0])
        # cv2.waitKey(1)
        # print(result)
        # if result[0].any():
        #     cv2.imshow("color",result[0])
        #     cv2.imshow("depth",result[1])
        #     print("dis=",result[2][240,320])
        #     cv2.waitKey(1)
    # main()
