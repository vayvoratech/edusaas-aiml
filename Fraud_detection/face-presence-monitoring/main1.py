import cv2
from ultralytics import YOLO

# Load YOLO model
model = YOLO("yolov8n.pt")

# Open webcam
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Unable to open camera")
    exit()

while True:

    ret, frame = cap.read()

    if not ret:
        break

    # Run YOLO
    results = model(frame, verbose=False)

    person_count = 0

    for result in results:

        for box in result.boxes:

            cls = int(box.cls[0])

            # COCO class 0 = Person
            if cls == 0:
                person_count += 1

    # Decide Status
    if person_count == 0:
        status = "FACE_MISSING"

    elif person_count == 1:
        status = "FACE_PRESENT"

    else:
        status = "MULTIPLE_FACES"

    # Draw detections
    annotated = results[0].plot()

    cv2.putText(
        annotated,
        status,
        (20, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (0, 255, 0),
        2
    )

    cv2.imshow("Face Presence Monitoring", annotated)

    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()




                         EduSaaS
                            │
                    ┌───────▼────────┐
                    │ Student Browser│
                    │                │
                    │ Exam Questions │
                    │ Timer          │
                    │ Clean Webcam   │
                    └───────┬────────┘
                            │
                         WebSocket
                            │
                    ┌───────▼────────┐
                    │    Node.js     │
                    │ Examination API│
                    └───────┬────────┘
                            │
                         WebSocket
                            │
                    ┌───────▼────────┐
                    │ Python AI      │
                    │ Proctoring     │
                    ├────────────────┤
                    │ MediaPipe      │
                    │ Face           │
                    │ Eyes           │
                    │ Blink          │
                    │ Head Pose      │
                    │ Mouth          │
                    ├────────────────┤
                    │ YOLO11s        │
                    │ Phone          │
                    └───────┬────────┘
                            │
                    ┌───────▼────────┐
                    │ Fraud Engine   │
                    └───────┬────────┘
                            │
                ┌───────────┼───────────┐
                ▼           ▼           ▼
             NORMAL      WARNING     PAUSE
                            │           │
                            └─────┬─────┘
                                  ▼
                             Node.js
                                  │
                                  ▼
                           Examination UI
                                  │
                                  ▼
                              PostgreSQL
                              
                              
                              
                              
                              
                              
                              Student Browser
      │
      ├── Camera
      │
      ├── Browser monitoring
      │      ├── Tab switch
      │      ├── Window blur
      │      ├── Fullscreen exit
      │      ├── Copy / Paste / Cut
      │      ├── Right click
      │      └── Keyboard shortcuts
      │
      ▼
Node.js WebSocket Server
      │
      ▼
Python AI Service
      │
      ├── MediaPipe
      ├── YOLO11s
      └── Fraud Detection
      │
      ▼
Node.js
      │
      ▼
Browser
      │
      ├── Warning
      ├── Pause
      └── Terminate
      
      
      
      
      Mobile detected
      │
      ▼
Persistence threshold reached
      │
      ▼
1st detection
      │
      ├── WARNING
      └── PAUSE_EXAM for 10 seconds
             ↓
          10...9...8...1
             ↓
          Resume exam

2nd detection
      │
      ├── WARNING
      └── PAUSE_EXAM for 10 seconds
             ↓
          10...9...8...1
             ↓
          Resume exam

3rd detection
      │
      └── TERMINATE_EXAM