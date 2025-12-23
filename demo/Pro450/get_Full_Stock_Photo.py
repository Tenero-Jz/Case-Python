import cv2

cap = cv2.VideoCapture(0)

ret, frame = cap.read()
cv2.imwrite("shelf_full.jpg", frame)

cap.release()
print("已保存满货架基准图")
