# import cv2
#
# cap = cv2.VideoCapture("http://192.168.1.95:8080/video_feed")
# while True:
#     ret, frame = cap.read()
#     if not ret:
#         break
#     cv2.imshow("Robot Camera", frame)
#     if cv2.waitKey(1) & 0xFF == 27:
#         break
# cap.release()
# cv2.destroyAllWindows()

import cv2
url = "rtsp://192.168.123.190:8554/robot_cam"

cap = cv2.VideoCapture(url)

if not cap.isOpened():
    print("无法连接 RTSP 流，请检查 IP 和端口")
    exit()

while True:
    ret, frame = cap.read()
    if not ret:
        print("读取失败，尝试重连...")
        cap = cv2.VideoCapture(url)
        continue

    cv2.imshow("Robot Camera", frame)
    if cv2.waitKey(1) & 0xFF == 27:  # ESC键退出
        break

cap.release()
cv2.destroyAllWindows()

