from ultralytics import YOLO

dataset_path = r"C:\Users\My PC\Desktop\Mini-Proj\CODE\ultralytics\datasets\ID-Card-1\id_card.yaml"

model = YOLO("yolov8n.pt")

model.train(data=dataset_path, epochs=100, imgsz=640, batch=16, name="ID_Card_detection")