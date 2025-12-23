import cv2
import threading
import os
import time
from datetime import datetime

# 创建视频保存文件夹
video_folder = "Video_recording"
if not os.path.exists(video_folder):
    os.makedirs(video_folder)


# 生成当前时间字符串（格式：YYYY-MM-DD_HH-MM-SS）
def get_timestamp():
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")


class CameraRecorder(threading.Thread):
    def __init__(self, camera_index, filename):
        super().__init__()
        self.camera_index = camera_index
        self.filename = filename
        self.running = True  # 运行标志
        self.cap = cv2.VideoCapture(camera_index)  # 打开摄像头
        self.fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # 视频编码格式
        self.fps = 20  # 帧率
        self.frame_width = int(self.cap.get(3))  # 获取帧宽
        self.frame_height = int(self.cap.get(4))  # 获取帧高
        self.out = cv2.VideoWriter(self.filename, self.fourcc, self.fps,
                                   (self.frame_width, self.frame_height))  # 视频写入对象

    def run(self):
        while self.running:
            ret, frame = self.cap.read()
            if ret:
                self.out.write(frame)  # 写入视频
            time.sleep(0.02)  # 20ms 控制帧率

    def stop(self):
        self.running = False
        time.sleep(1)  # 确保最后一帧写入
        self.cap.release()
        self.out.release()
        print(f"视频 {self.filename} 录制完成并保存.")


def start_recording():
    timestamp = get_timestamp()

    # 创建摄像头录制线程
    left_camera = CameraRecorder(0, os.path.join(video_folder, f"left_video_{timestamp}.mp4"))
    right_camera = CameraRecorder(1, os.path.join(video_folder, f"right_video_{timestamp}.mp4"))
    top_camera = CameraRecorder(2, os.path.join(video_folder, f"top_video_{timestamp}.mp4"))

    # 启动摄像头录制线程
    left_camera.start()
    right_camera.start()
    top_camera.start()

    return left_camera, right_camera, top_camera
