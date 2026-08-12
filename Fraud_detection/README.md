# EduSaaS AI Proctoring & Fraud Detection System

## 1. Project Overview

The EduSaaS AI Proctoring System is a real-time examination monitoring system designed to detect suspicious student behavior during online assessments.

The system uses:

* Browser-based camera capture
* JavaScript browser-event monitoring
* Node.js WebSocket gateway
* Python FastAPI AI service
* MediaPipe Tasks API
* Computer vision models
* Fraud detection logic
* Real-time WebSocket communication

The system continuously analyzes the student's camera feed and browser activity while the assessment is running.

The system can detect events such as:

* Face missing
* Multiple faces
* Looking left
* Looking right
* Looking up
* Looking down
* Eyes closed / blink
* Mouth open
* Phone detection
* Tab switching
* Window focus loss
* Fullscreen exit
* Copy attempt
* Paste attempt
* Cut attempt
* Right-click attempt

---

# 2. High-Level Architecture

The system follows a three-layer architecture:

```text
                         EduSaaS AI Proctoring
                                  |
                                  |
                           Student Browser
                                  |
                                  |
                         WebSocket Connection
                                  |
                                  v
                         +----------------+
                         |    Node.js     |
                         | WebSocket      |
                         | Gateway        |
                         +-------+--------+
                                 |
                                 |
                          WebSocket Proxy
                                 |
                                 v
                         +----------------+
                         | Python FastAPI |
                         | AI Proctoring  |
                         | Service        |
                         +-------+--------+
                                 |
                +----------------+----------------+
                |                |                |
                v                v                v
         Face Detection     Face Mesh       Fraud Engine
                |                |                |
                +----------------+----------------+
                                 |
                                 v
                            AI Result
                                 |
                                 v
                         Python FastAPI
                                 |
                                 v
                            Node.js
                                 |
                                 v
                             Browser
                                 |
                  +--------------+--------------+
                  |              |              |
                Normal         Warning       Terminate
                               / Pause         Exam
```

---

# 3. Project Structure

The project is divided into two major services.

```text
Fraud_detection/
│
├── face-presence-monitoring/
│   │
│   ├── main.py
│   ├── face_presence.py
│   ├── face_mesh.py
│   ├── eye_tracker.py
│   ├── blink_detector.py
│   ├── mouth_detector.py
│   ├── head_pose.py
│   ├── phone_detection.py
│   ├── fraud_engine.py
│   │
│   └── models/
│       ├── face_detector.task
│       └── face_landmarker.task
│
│
└── node_server/
    │
    ├── server.js
    ├── proctoring.js
    ├── proctoring_test.html
    ├── package.json
    └── package-lock.json
```

---

# 4. Technology Stack

## Frontend

* HTML5
* CSS3
* JavaScript
* WebRTC / `getUserMedia()`
* Fullscreen API
* WebSocket API

## Node.js

* Node.js
* Express
* `ws` WebSocket library

## Python

* Python 3.13.3
* FastAPI
* Uvicorn
* OpenCV
* MediaPipe
* NumPy

## AI / Computer Vision

* MediaPipe Face Detector
* MediaPipe Face Landmarker
* Face landmarks
* Eye tracking
* Blink detection
* Mouth detection
* Head pose estimation
* Phone detection
* Fraud detection engine

---

# 5. Why Node.js Is Used

Node.js acts as the WebSocket gateway between the browser and Python AI service.

The browser does **not** directly communicate with Python.

Instead:

```text
Browser
   |
   | WebSocket
   v
Node.js
   |
   | WebSocket
   v
Python
```

This provides a clean separation between:

### Browser Layer

Responsible for:

* Camera access
* Exam UI
* Fullscreen
* Browser event detection
* Displaying warnings
* Displaying pause countdown
* Displaying termination

### Node.js Layer

Responsible for:

* WebSocket gateway
* Browser connection management
* Forwarding browser messages to Python
* Forwarding Python responses to browser

### Python Layer

Responsible for:

* AI processing
* Computer vision
* Fraud detection
* Violation counting
* Warning decisions
* Exam termination decisions

---

# 6. Browser → Node.js Connection

When the student clicks:

```text
Start Assessment
```

the JavaScript creates the proctoring object:

```javascript
proctor = new window.Proctoring({

    wsUrl:
        "ws://localhost:3000/ws/proctor",

    frameRate: 5,

    cameraWidth: 640,

    cameraHeight: 480,

    jpegQuality: 0.65

});
```

The browser therefore connects to:

```text
ws://localhost:3000/ws/proctor
```

This is the Node.js WebSocket endpoint.

---

# 7. Node.js → Python Connection

Node.js receives the browser WebSocket connection.

It then creates another WebSocket connection:

```text
ws://localhost:8000/ws/proctor
```

This connects Node.js to the Python FastAPI service.

The complete connection becomes:

```text
Browser
   |
   | ws://localhost:3000/ws/proctor
   |
   v
Node.js
   |
   | ws://localhost:8000/ws/proctor
   |
   v
Python FastAPI
```

Node.js forwards messages in both directions.

---

# 8. Starting the Assessment

When the student clicks:

```text
Start Assessment
```

the following sequence occurs.

```text
1. User clicks Start Assessment
              |
              v
2. Browser requests camera permission
              |
              v
3. Camera permission granted
              |
              v
4. Browser enters fullscreen
              |
              v
5. Exam page becomes visible
              |
              v
6. Proctoring object is created
              |
              v
7. WebSocket connects to Node.js
              |
              v
8. Node.js connects to Python
              |
              v
9. Camera starts
              |
              v
10. Video frames start streaming
              |
              v
11. Python AI starts processing
```

---

# 9. Camera Processing

The browser requests access to the student's camera using:

```javascript
navigator.mediaDevices.getUserMedia({
    video: true,
    audio: false
});
```

The video is displayed in the bottom-right corner:

```html
<video
    id="cameraVideo"
    autoplay
    muted
    playsinline
></video>
```

The video is also used to capture frames.

---

# 10. Frame Processing

The browser captures frames from the camera.

The frame is converted into JPEG data:

```javascript
canvas.toDataURL(
    "image/jpeg",
    0.65
);
```

The frame is then sent through WebSocket:

```text
Browser
   |
   | VIDEO_FRAME
   v
Node.js
   |
   | VIDEO_FRAME
   v
Python
```

The browser currently sends approximately:

```text
5 frames / second
```

depending on the configured `frameRate`.

---

# 11. Python AI Processing

Python receives the video frame through:

```text
/ws/proctor
```

The frame is decoded using OpenCV.

The AI pipeline then processes the frame.

```text
Incoming Frame
      |
      v
OpenCV
      |
      v
Face Presence Detection
      |
      v
Face Mesh
      |
      +--------------------+
      |                    |
      v                    v
Eye Tracking          Head Pose
      |                    |
      v                    v
Blink Detection       Direction
      |                    |
      +----------+---------+
                 |
                 v
          Mouth Detection
                 |
                 v
         Phone Detection
                 |
                 v
          Fraud Engine
```

---

# 12. Face Presence Detection

The face detector determines how many faces are visible.

Possible results:

```text
FACE_MISSING
FACE_PRESENT
MULTIPLE_FACES
```

### No face

```text
FACE_MISSING
```

This can indicate that the student has moved away from the camera.

### One face

```text
FACE_PRESENT
```

This is the normal condition.

### Multiple faces

```text
MULTIPLE_FACES
```

This can indicate another person is present.

---

# 13. Face Mesh

The Face Landmarker generates facial landmarks.

The landmarks are converted into normal Python dictionaries such as:

```python
{
    "x": 0.52,
    "y": 0.43,
    "z": -0.02
}
```

This is important because the AI modules operate on numeric landmark coordinates rather than raw MediaPipe protobuf objects.

The system therefore avoids sending non-serializable MediaPipe objects through JSON.

---

# 14. Eye Tracking

The eye tracking system uses facial landmarks to estimate the student's gaze direction.

Possible states include:

```text
LOOKING_LEFT
LOOKING_RIGHT
LOOKING_CENTER
```

The eye position is normalized relative to the eye corners.

---

# 15. Blink Detection

Blink detection calculates the Eye Aspect Ratio (EAR).

Conceptually:

```text
EAR =
vertical eye opening
--------------------
horizontal eye width
```

The result is used to determine:

```text
EYES_OPEN
EYES_CLOSED
```

---

# 16. Mouth Detection

The mouth detector calculates the Mouth Aspect Ratio (MAR).

Conceptually:

```text
MAR =
vertical mouth opening
----------------------
horizontal mouth width
```

Possible states:

```text
MOUTH_OPEN
MOUTH_CLOSED
```

---

# 17. Head Pose Detection

Head pose estimation uses facial landmarks and OpenCV's `solvePnP()`.

The system calculates:

```text
Pitch
Yaw
Roll
```

Possible states include:

```text
LOOKING_CENTER
LOOKING_LEFT
LOOKING_RIGHT
LOOKING_UP
LOOKING_DOWN
```

Example:

```text
Pitch: -4.2
Yaw:   18.3
Roll:   1.4
```

A large yaw value can indicate that the student is looking away from the screen.

---

# 18. Phone Detection

The phone detection component analyzes the camera frame for a mobile phone.

When a phone is detected, the Fraud Engine can register a violation.

---

# 19. Browser Event Monitoring

AI camera analysis is only one part of the proctoring system.

The browser also monitors examination events.

The system can detect:

```text
TAB_SWITCH
WINDOW_BLUR
FULLSCREEN_EXIT
COPY_ATTEMPT
PASTE_ATTEMPT
CUT_ATTEMPT
RIGHT_CLICK
```

For example:

```javascript
document.addEventListener(
    "visibilitychange",
    ...
);
```

detects when the browser page becomes hidden.

---

# 20. Important Browser Limitation

A normal browser cannot completely disable operating-system-level tab switching.

JavaScript can:

* Detect tab switching
* Detect page visibility changes
* Detect fullscreen exits
* Prevent copy/paste events
* Detect window focus loss
* Report those events to the backend

Therefore, the system uses **detection and violation handling** rather than claiming to physically disable browser/OS tab switching.

---

# 21. Fraud Engine

The Fraud Engine is responsible for converting detections into examination actions.

The basic policy is:

```text
First violation
       |
       v
Warning
       |
       v
Pause exam
       |
       v
10-second countdown
       |
       v
Resume exam
```

The second violation:

```text
Second violation
       |
       v
Terminate examination
```

---

# 22. First Violation

When the first violation occurs:

```text
AI detects violation
        |
        v
Fraud Engine
        |
        v
WARNING
        |
        v
Node.js
        |
        v
Browser
        |
        v
Screen blurred
        |
        v
Exam paused
        |
        v
10
9
8
7
6
5
4
3
2
1
0
        |
        v
Exam resumes
```

The student sees the warning and countdown on the page.

---

# 23. Second Violation

If another violation occurs:

```text
AI detects violation
        |
        v
Fraud Engine
        |
        v
TERMINATE_EXAM
        |
        v
Node.js
        |
        v
Browser
        |
        v
Exam Terminated
```

The exam page is hidden and the termination screen is displayed.

---

# 24. WebSocket Message Flow

## Browser → Node

Example:

```json
{
    "type": "VIDEO_FRAME",
    "frame": "data:image/jpeg;base64,..."
}
```

Node forwards this message to Python.

---

## Node → Python

The message is forwarded without changing the payload.

```text
Browser
   |
   | VIDEO_FRAME
   v
Node
   |
   | VIDEO_FRAME
   v
Python
```

---

## Python → Node

Python sends an AI result.

Example:

```json
{
    "type": "PROCTORING_RESULT",
    "fraud": {
        "action": "WARNING",
        "message": "Please remain focused on the examination.",
        "violation_count": 1
    }
}
```

---

## Node → Browser

Node forwards the AI result.

```text
Python
   |
   | PROCTORING_RESULT
   v
Node
   |
   | PROCTORING_RESULT
   v
Browser
```

The browser then calls:

```javascript
onResult(data)
```

and handles the appropriate action.

---

# 25. Normal Examination Flow

```text
Student
   |
   v
Start Assessment
   |
   +--> Camera Permission
   |
   +--> Fullscreen
   |
   +--> WebSocket → Node
                |
                +--> WebSocket → Python
                                  |
                                  v
                               AI Models
                                  |
                                  v
                              No Violation
                                  |
                                  v
                              Continue Exam
```

---

# 26. Violation Flow

```text
Student behavior
       |
       v
Camera / Browser Event
       |
       v
Node.js
       |
       v
Python AI
       |
       v
Fraud Engine
       |
       v
Violation detected
       |
       +----------------------+
       |                      |
       v                      v
 First Violation        Second Violation
       |                      |
       v                      v
    Warning                Terminate
       |                      |
       v                      v
     Pause                  Stop
       |
       v
 10-second countdown
       |
       v
    Resume
```

---

# 27. Running the Python Service

Open a terminal:

```powershell
cd C:\EduSaaS\Fraud_detection\face-presence-monitoring
```

Activate your environment if required:

```powershell
myenv\Scripts\activate
```

Run:

```powershell
python main.py
```

Expected server:

```text
AI Models Ready

Uvicorn running on:
http://0.0.0.0:8000
```

Python WebSocket endpoint:

```text
ws://localhost:8000/ws/proctor
```

---

# 28. Running the Node.js Service

Open another terminal:

```powershell
cd C:\EduSaaS\Fraud_detection\node_server
```

Install dependencies:

```powershell
npm install
```

Run the server:

```powershell
node server.js
```

Expected output:

```text
======================================
EduSaaS Node Proctoring Gateway
======================================

HTTP Server:
http://localhost:3000

WebSocket:
ws://localhost:3000/ws/proctor

Python AI:
ws://localhost:8000/ws/proctor

======================================
```

---

# 29. Opening the Assessment

Open:

```text
http://localhost:3000/proctoring_test.html
```

Do not open the HTML file directly using:

```text
file:///...
```

Use the Node.js HTTP server.

---

# 30. Complete Startup Sequence

Start Python first:

```text
Terminal 1
    |
    v
python main.py
    |
    v
Python :8000
```

Then start Node:

```text
Terminal 2
    |
    v
node server.js
    |
    v
Node :3000
```

Then open:

```text
Browser
    |
    v
http://localhost:3000/proctoring_test.html
```

---

# 31. Complete Runtime Architecture

```text
┌────────────────────────────────────────────────────────────┐
│                         BROWSER                             │
│                                                            │
│  proctoring_test.html                                     │
│                                                            │
│  ┌───────────────┐     ┌──────────────────────────────┐   │
│  │ Exam UI       │     │ Camera                       │   │
│  │               │     │                              │   │
│  │ Questions     │     │ <video id="cameraVideo">     │   │
│  └───────────────┘     └──────────────┬───────────────┘   │
│                                       │                   │
│                               proctoring.js               │
└───────────────────────────────────────┼───────────────────┘
                                        │
                                        │ WebSocket
                                        │ :3000
                                        ▼
┌────────────────────────────────────────────────────────────┐
│                         NODE.JS                            │
│                                                            │
│                     WebSocket Gateway                      │
│                                                            │
│                Browser ↔ Python Proxy                      │
└───────────────────────────────┬────────────────────────────┘
                                │
                                │ WebSocket
                                │ :8000
                                ▼
┌────────────────────────────────────────────────────────────┐
│                       PYTHON FASTAPI                        │
│                                                            │
│                       /ws/proctor                           │
│                                                            │
│  ┌──────────────────────────────────────────────────────┐  │
│  │                  AI PROCESSING                       │  │
│  │                                                      │  │
│  │  Face Presence                                      │  │
│  │       ↓                                              │  │
│  │  Face Mesh                                          │  │
│  │       ↓                                              │  │
│  │  Eye / Blink                                         │  │
│  │       ↓                                              │  │
│  │  Head Pose                                           │  │
│  │       ↓                                              │  │
│  │  Mouth Detection                                     │  │
│  │       ↓                                              │  │
│  │  Phone Detection                                     │  │
│  │       ↓                                              │  │
│  │  Fraud Engine                                        │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                            │
└───────────────────────────────┬────────────────────────────┘
                                │
                                │ AI Result
                                ▼
                         Node.js Gateway
                                │
                                ▼
                             Browser
                                │
                ┌───────────────┼───────────────┐
                │               │               │
                ▼               ▼               ▼
             Normal          Warning        Terminate
                                │
                                ▼
                         Pause + Countdown
                                │
                                ▼
                             Resume
```

---

# 32. Python 3.13.3

The Python AI service is designed around the modern MediaPipe Tasks API.

The project uses:

```text
Python 3.13.3
```

The face detection and face landmark models are stored under:

```text
models/
```

Example:

```text
models/
├── face_detector.task
└── face_landmarker.task
```

The Python code converts MediaPipe landmark results into standard Python numeric structures before passing them to the downstream detection modules.

This allows the data to be safely processed and prevents MediaPipe protobuf objects from being directly serialized into JSON.

---

# 33. Security and Privacy Considerations

The current development setup uses:

```text
localhost
```

for both Node.js and Python.

For production deployment, additional security controls should be considered:

* HTTPS
* Secure WebSockets (`wss://`)
* Authentication
* Authorization
* Assessment/session IDs
* Student IDs
* Secure session management
* Server-side validation
* Rate limiting
* Logging
* Data retention policies
* Encryption
* Access control
* Privacy and consent requirements

Camera access should only be requested after the student intentionally starts the assessment.

---

# 34. Troubleshooting

## Node server cannot start

Check Node installation:

```powershell
node --version
npm --version
```

Install dependencies:

```powershell
npm install
```

---

## Python server cannot start

Check Python:

```powershell
python --version
```

Expected:

```text
Python 3.13.3
```

---

## Browser says `proctoring.js not loaded`

Check:

```text
node_server/
├── proctoring.js
└── proctoring_test.html
```

and HTML:

```html
<script src="./proctoring.js"></script>
```

---

## `Video element not found`

Make sure the HTML contains:

```html
<video
    id="cameraVideo"
    autoplay
    muted
    playsinline
></video>
```

The ID must exactly be:

```text
cameraVideo
```

---

## WebSocket connection failed

Check that both services are running.

Python:

```text
ws://localhost:8000/ws/proctor
```

Node:

```text
ws://localhost:3000/ws/proctor
```

The browser must use:

```javascript
wsUrl:
    "ws://localhost:3000/ws/proctor"
```

The browser should **not** directly use port `8000`.

---

## Python receives no frames

Check:

```text
Browser
   ↓
Node :3000
   ↓
Python :8000
```

Look at the Node terminal for:

```text
Browser WebSocket connected.
Node → Python WebSocket connected.
```

Then check Python for:

```text
WebSocket /ws/proctor [accepted]
connection open
Examination started.
```

---

# 35. Development Ports

| Service        | Port | Purpose                   |
| -------------- | ---: | ------------------------- |
| Node.js        | 3000 | Browser HTTP + WebSocket  |
| Python FastAPI | 8000 | AI processing + WebSocket |

Endpoints:

```text
Browser:
http://localhost:3000/proctoring_test.html

Browser → Node:
ws://localhost:3000/ws/proctor

Node → Python:
ws://localhost:8000/ws/proctor
```

---

# 36. Summary

The EduSaaS AI Proctoring System separates the application into three layers:

```text
1. Browser
       ↓
2. Node.js WebSocket Gateway
       ↓
3. Python FastAPI AI Service
```

The browser handles the student-facing examination experience.

Node.js acts as the communication gateway.

Python performs the AI and fraud analysis.

The complete data flow is:

```text
Camera
   ↓
Browser
   ↓
proctoring.js
   ↓
Node.js WebSocket Gateway
   ↓
Python FastAPI
   ↓
Computer Vision
   ↓
Fraud Engine
   ↓
AI Result
   ↓
Python
   ↓
Node.js
   ↓
Browser
   ↓
Warning / Pause / Resume / Termination
```

This architecture provides a clean separation between the **frontend examination environment**, **communication layer**, and **AI proctoring backend**, making it easier to extend the system later with additional AI models, authentication, assessment management, analytics, and production infrastructure.
