import cv2
import numpy as np
import time


SHELF_SLOTS = {
    "spicy_strip": {"name_cn": "辣条", "roi": (20, 80, 160, 300)},
    "cola":        {"name_cn": "可乐", "roi": (170, 80, 310, 300)},
    "tissue":      {"name_cn": "纸巾", "roi": (320, 80, 460, 300)},
    "medicine":    {"name_cn": "感冒药", "roi": (470, 80, 620, 300)},
}


DIFF_THRESHOLD = 25
MISS_FRAMES = 8
CAMERA_ID = 0

miss_counter = {k: 0 for k in SHELF_SLOTS.keys()}

bg = cv2.imread("D:/Company/pythonProject/Case/demo/Pro450/shelf_full.jpg")
if bg is None:
    raise RuntimeError("无法读取 shelf_full.jpg，请确认文件路径")

bg_gray = cv2.cvtColor(bg, cv2.COLOR_BGR2GRAY)


cap = cv2.VideoCapture(CAMERA_ID)
if not cap.isOpened():
    raise RuntimeError("摄像头打开失败")

print("开始货架监视")

print("摄像头分辨率:",
      int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
      int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))


while True:
    ret, frame = cap.read()
    if not ret or frame is None:
        print("摄像头帧读取失败，跳过")
        time.sleep(0.1)
        continue

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    h, w = gray.shape

    missing_items = []

    for key, slot in SHELF_SLOTS.items():
        x1, y1, x2, y2 = slot["roi"]

        x1 = max(0, min(x1, w - 1))
        x2 = max(0, min(x2, w))
        y1 = max(0, min(y1, h - 1))
        y2 = max(0, min(y2, h))

        if x2 <= x1 or y2 <= y1:
            print(f"ROI 无效: {slot['name_cn']}")
            continue

        roi_bg = bg_gray[y1:y2, x1:x2]
        roi_now = gray[y1:y2, x1:x2]

        if roi_bg.size == 0 or roi_now.size == 0:
            print(f"ROI 为空: {slot['name_cn']}")
            continue

        diff = cv2.absdiff(roi_bg, roi_now)
        mean_diff = float(np.mean(diff))

        if mean_diff > DIFF_THRESHOLD:
            miss_counter[key] += 1
        else:
            miss_counter[key] = 0

        if miss_counter[key] >= MISS_FRAMES:
            missing_items.append(slot["name_cn"])
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 3)
            cv2.putText(frame, "EMPTY",
                        (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.7, (0, 0, 255), 2)
        else:
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

        cv2.putText(frame,
                    f"{mean_diff:.1f}",
                    (x1 + 5, y2 - 5),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5, (255, 255, 0), 1)

    if missing_items:
        print(f"识别到货架缺少：{', '.join(missing_items)}")

    cv2.imshow("Shelf Monitor", frame)

    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
print("监视结束")
