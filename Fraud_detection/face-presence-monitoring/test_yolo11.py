import cv2
import time
from ultralytics import YOLO


model = YOLO("yolo11s.pt")

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Unable to access camera")
    exit()


frame_count = 0
start_time = time.time()


while True:

    ret, frame = cap.read()

    if not ret:
        break

    model.predict(
        frame,
        imgsz=640,
        conf=0.15,
        verbose=False
    )

    frame_count += 1

    elapsed = time.time() - start_time

    fps = frame_count / elapsed

    cv2.putText(
        frame,
        f"YOLO11s FPS: {fps:.2f}",
        (20, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.9,
        (0, 255, 0),
        2
    )

    cv2.imshow(
        "YOLO11s FPS Test",
        frame
    )

    if cv2.waitKey(1) & 0xFF == 27:
        break


elapsed = time.time() - start_time

print()
print("==============================")
print("YOLO11s Performance")
print("==============================")
print(f"Frames      : {frame_count}")
print(f"Time        : {elapsed:.2f} sec")
print(
    f"Average FPS : "
    f"{frame_count / elapsed:.2f}"
)
print("==============================")


cap.release()
cv2.destroyAllWindows()