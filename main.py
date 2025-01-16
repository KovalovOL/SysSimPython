import cv2
from ultralytics import YOLO


model = YOLO('yolov8n.pt')

cap = cv2.VideoCapture(1)

if not cap.isOpened():
    print("Error: Can not Capture Video")
    exit()

rectangle_color = (0, 230, 0)
rectangle_thickness = 1
min_confidence = 0.5
sheep_class_id = 18

while True:
    ret, frame = cap.read()
    if not ret:
        print("Error: Can not get frame")
        break


    results = model(frame)

    filtered_results = [result for result in results[0].boxes if result.cls == sheep_class_id]

    for result in filtered_results:
        x1, y1, x2, y2 = result.xyxy[0].tolist()
        confidence = result.conf[0]

        if confidence >= min_confidence:
            cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), rectangle_color, rectangle_thickness)
            cv2.putText(frame, f"Sheep: {confidence:.2f}%", (int(x1), int(y1) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, rectangle_color, 1)

    cv2.imshow("Sheep Detection", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
