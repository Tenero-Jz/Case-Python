from ultralytics import YOLO

model = YOLO("yolov8s.pt")
results = model("test/images/fruit_output_1980_png.rf.7200bbb928e5fc5812d12b170de4e712.jpg")

results[0].show()


# if __name__ == "__main__":
#     model = YOLO("yolov8s.pt")
#     model.train(
#         data="Lemon/data.yaml",
#         epochs=100,
#         imgsz=640,
#         batch=16,
#         name="lemon_detector",
#         device=0
#     )
