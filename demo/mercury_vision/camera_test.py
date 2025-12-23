#!/usr/bin/env python
import cv2
import uvc_camera
import typing as T

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


if __name__ == "__main__":
    camera = UVCCamera(0, mtx, dist)
    # 打开摄像头open camera(ok)
    camera.capture()
    while True:
        camera.update_frame()
        frame = camera.color_frame()
        cv2.imshow("test", frame)
        cv2.waitKey(1)
