from ultralytics import YOLO

dataset_path = "C:/Users/My PC/Desktop/Mini-Proj/CODE/ultralytics/datasets/Bench-1/data.yaml"

model = YOLO("yolov8n.pt")

model.train(data=dataset_path, epochs=30, imgsz=640, batch=16, name="bench_detection")