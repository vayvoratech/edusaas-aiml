import cv2
import time

from ultralytics import RTDETR


model = RTDETR("rtdetr-l.pt")

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Camera error")
    exit()


frame_count = 0
start_time = time.time()


while True:

    ret, frame = cap.read()

    if not ret:
        break

    results = model.predict(
        frame,
        imgsz=640,
        conf=0.25,
        verbose=False
    )

    frame_count += 1

    elapsed = time.time() - start_time

    fps = frame_count / elapsed

    cv2.putText(
        frame,
        f"RT-DETR FPS: {fps:.2f}",
        (20, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (0, 255, 0),
        2
    )

    cv2.imshow("RT-DETR FPS Test", frame)

    if cv2.waitKey(1) & 0xFF == 27:
        break


cap.release()
cv2.destroyAllWindows()

print("Average FPS:", frame_count / (time.time() - start_time))