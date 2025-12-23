import cv2
import threading
import os

class CameraRecorder(threading.Thread):
    def __init__(self, camera_source, output_file):
        threading.Thread.__init__(self)
        self.camera_source = camera_source
        self.output_file = output_file
        self.running = True
        self.frame_size = (1280, 720)  # 根据实际分辨率调整
        self.fps = 30

    def run(self):
        # 初始化摄像头（必须使用设备路径）
        cap = cv2.VideoCapture(self.camera_source)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.frame_size[0])
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.frame_size[1])
        cap.set(cv2.CAP_PROP_FPS, self.fps)

        if not cap.isOpened():
            print(f"[错误] 无法打开摄像头 {self.camera_source}")
            return

        # 配置MP4编码器（需系统支持）
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # 或 'X264'/'H264'
        out = cv2.VideoWriter(
            self.output_file,
            fourcc,
            self.fps,
            self.frame_size
        )

        print(f"开始录制：{self.output_file}")
        while self.running:
            ret, frame = cap.read()
            if ret:
                out.write(frame)
            else:
                print(f"摄像头 {self.camera_source} 帧读取失败")
                break

        cap.release()
        out.release()
        print(f"停止录制：{self.output_file}")

    def stop(self):
        self.running = False

def main():
    # 配置相机参数（注意检查设备路径）
    cameras = [
        {"source": "/dev/video4", "output": "camera0.mp4"},
        {"source": "/dev/video6", "output": "camera1.mp4"},
        {"source": "/dev/video8", "output": "camera2.mp4"}
    ]

    # 启动多线程录制
    recorders = []
    for cam in cameras:
        output_path = os.path.join(os.path.dirname(__file__), cam["output"])
        recorder = CameraRecorder(cam["source"], output_path)
        recorder.start()
        recorders.append(recorder)

    input("按回车键停止录制...\n")

    for recorder in recorders:
        recorder.stop()
    for recorder in recorders:
        recorder.join()

    print("所有录制已停止")

if __name__ == "__main__":
    main()