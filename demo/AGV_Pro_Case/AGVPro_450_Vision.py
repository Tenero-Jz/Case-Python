import cv2
import random
from ultralytics import YOLO

model = YOLO("yolov8n.pt")

# 为每个类别生成一种颜色
colors = {}


def get_color(cls):
    if cls not in colors:
        colors[cls] = [random.randint(0, 255) for _ in range(3)]
    return colors[cls]


cap = cv2.VideoCapture(1)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # 模型推理
    results = model(frame, stream=True)

    for r in results:
        boxes = r.boxes
        for box in boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            cls = int(box.cls[0])
            conf = float(box.conf[0])
            label = model.names[cls]

            # 获取该类别的颜色
            color = get_color(cls)

            # 画框
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            cv2.putText(frame, f"{label} {conf:.2f}",
                        (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX,
                        0.6, color, 2)

    cv2.imshow("Desk Object Detection", frame)

    if cv2.waitKey(1) & 0xFF == 27:  # ESC退出
        break

cap.release()
cv2.destroyAllWindows()

# import cv2
# import numpy as np
#
# # 定义颜色范围（HSV）
# COLOR_RANGES = {
#     "dark_red": [(0, 120, 80), (10, 255, 180)],
#     "green": [(35, 60, 60), (85, 255, 255)],
#     "yellow": [(20, 100, 100), (30, 255, 255)],
#     # "light_yellow": [(15, 50, 150), (25, 150, 255)],
#     # "pink": [(145, 60, 120), (175, 200, 255)],
#     "orange": [(10, 150, 150), (25, 255, 255)],
#     "light_blue": [(85, 80, 80), (110, 255, 255)]
# }
#
# # 背景黑白墙（不画框）
# BLACK_RANGE = [(0, 0, 0), (180, 255, 60)]
# WHITE_RANGE = [(0, 0, 170), (180, 60, 255)]
#
# # 框颜色（BGR）
# BOX_COLORS = {
#     "dark_red": (0, 0, 139),  # 深红色框（深红 / 暗红色）
#     "green": (0, 255, 0),
#     "yellow": (0, 255, 255),
#     # "light_yellow": (120, 255, 255),
#     "orange": (0, 165, 255),
#     "light_blue": (255, 255, 0),
#     # "pink": (203, 192, 255)
# }
#
#
# def is_background(hsv_pixel):
#     """判断是否为背景墙（黑色或白色）"""
#     h, s, v = hsv_pixel
#
#     # 判断黑色
#     if BLACK_RANGE[0][0] <= h <= BLACK_RANGE[1][0] and \
#             BLACK_RANGE[0][1] <= s <= BLACK_RANGE[1][1] and \
#             BLACK_RANGE[0][2] <= v <= BLACK_RANGE[1][2]:
#         return True
#
#     # 判断白色
#     if WHITE_RANGE[0][0] <= h <= WHITE_RANGE[1][0] and \
#             WHITE_RANGE[0][1] <= s <= WHITE_RANGE[1][1] and \
#             WHITE_RANGE[0][2] <= v <= WHITE_RANGE[1][2]:
#         return True
#
#     return False
#
#
# # 打开摄像头
# cap = cv2.VideoCapture(1)
#
# while True:
#     ret, frame = cap.read()
#     if not ret:
#         break
#
#     hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
#
#     for color_name, (lower, upper) in COLOR_RANGES.items():
#         mask = cv2.inRange(hsv, np.array(lower), np.array(upper))
#
#         # 提取轮廓
#         contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
#
#         for cnt in contours:
#             area = cv2.contourArea(cnt)
#             if area < 1000:
#                 continue
#
#             x, y, w, h = cv2.boundingRect(cnt)
#
#             # 判断中心颜色是否为背景
#             center_hsv = hsv[y + h // 2, x + w // 2]
#             if is_background(center_hsv):
#                 continue
#
#             # 画框
#             cv2.rectangle(frame, (x, y), (x + w, y + h), BOX_COLORS[color_name], 2)
#             # cv2.putText(frame, color_name, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, BOX_COLORS[color_name], 2)
#
#     cv2.imshow("Color Detection", frame)
#     if cv2.waitKey(1) & 0xFF == 27:  # ESC退出
#         break
#
# cap.release()
# cv2.destroyAllWindows()
