import cv2


def main():
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("摄像头打开失败")
        return

    print("摄像头已打开，按 q 退出")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("摄像头帧读取失败")
            break

        cv2.imshow("Camera", frame)

        # 按 q 键退出
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
