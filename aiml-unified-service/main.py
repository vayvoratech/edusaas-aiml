import base64
import time
import cv2
import numpy as np
import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.wsgi import WSGIMiddleware
from flask import Flask

# -----------------------------------------------------------------------------
# 1. QUIZ SERVICE INTEGRATION (FLASK WSGI MOUNT)
# -----------------------------------------------------------------------------
from modules.quiz.routes.quiz import quiz_bp
from modules.quiz.routes.skill_gap import skill_gap_bp

flask_app = Flask(__name__)
flask_app.register_blueprint(quiz_bp, url_prefix="/")
flask_app.register_blueprint(skill_gap_bp, url_prefix="/")

# -----------------------------------------------------------------------------
# 2. PLAGIARISM SERVICE INTEGRATION (FASTAPI ROUTER)
# -----------------------------------------------------------------------------

# -----------------------------------------------------------------------------
# 3. AI PROCTORING ENGINES & COMPUTER VISION
# -----------------------------------------------------------------------------
from modules.proctoring.face_presence import FacePresenceDetector
from modules.proctoring.face_mesh import FaceMeshDetector
from modules.proctoring.eye_tracking import EyeTracker
from modules.proctoring.blink_detection import BlinkDetector
from modules.proctoring.mouth_detection import MouthDetector
from modules.proctoring.phone_detection import PhoneDetector
from modules.proctoring.fraud_engine import FraudEngine

# -----------------------------------------------------------------------------
# APPLICATION FACTORY & SETUP
# -----------------------------------------------------------------------------
app = FastAPI(
    title="EduSaaS Unified AI & Proctoring Service",
    version="2.0.0",
    description="Unified single-gateway engine for Proctoring, Plagiarism, Quiz, and Skill Gap."
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Modular Routers
app.mount("/api/quiz", WSGIMiddleware(flask_app))
app.mount("/api/skill-gap", WSGIMiddleware(flask_app))

# -----------------------------------------------------------------------------
# PROCTORING CONSTANTS & MODEL LOADING
# -----------------------------------------------------------------------------
BROWSER_EVENT_COOLDOWN_SECONDS = 1.5
PHONE_DETECTED = "PHONE_DETECTED"
NO_FACE = "NO_FACE"

BROWSER_VIOLATIONS = {
    "TAB_SWITCH",
    "FULLSCREEN_EXIT",
}

print("\n==============================================")
print("Loading EduSaaS AI Proctoring Models")
print("==============================================")

face_detector = FacePresenceDetector()
mesh_detector = FaceMeshDetector()
eye_tracker = EyeTracker()
blink_detector = BlinkDetector()
mouth_detector = MouthDetector()
phone_detector = PhoneDetector()

print("\n==============================================")
print("AI Models Ready")
print("==============================================")
print("Face       : Ready")
print("Face Mesh  : Ready")
print("Eye        : Ready")
print("Blink      : Ready")
print("Mouth      : Ready")
print("Phone      : Ready")
print("Head Pose  : REMOVED")
print("==============================================\n")

# -----------------------------------------------------------------------------
# PROCTORING SESSION & STATE
# -----------------------------------------------------------------------------
class ProctoringSession:
    def __init__(self):
        self.violation_count = 0
        self.last_violation_type = None
        self.last_browser_event_times = {}
        self.fraud_engine = FraudEngine()
        self.last_action = "NORMAL"
        self.terminated = False
        self.frames_processed = 0
        self.started_at = time.time()

def convert_landmarks_for_detectors(landmarks):
    converted = []
    if not landmarks:
        return converted

    for landmark in landmarks:
        if isinstance(landmark, dict):
            converted.append((
                float(landmark.get("x", 0.0)),
                float(landmark.get("y", 0.0)),
                float(landmark.get("z", 0.0)),
            ))
            continue

        if isinstance(landmark, (list, tuple)):
            if len(landmark) >= 3:
                converted.append((
                    float(landmark[0]),
                    float(landmark[1]),
                    float(landmark[2]),
                ))
            elif len(landmark) >= 2:
                converted.append((
                    float(landmark[0]),
                    float(landmark[1]),
                    0.0,
                ))
            continue

        if hasattr(landmark, "x") and hasattr(landmark, "y"):
            converted.append((
                float(landmark.x),
                float(landmark.y),
                float(landmark.z) if hasattr(landmark, "z") else 0.0,
            ))

    return converted

def make_json_safe(value):
    if value is None:
        return None
    if isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, np.integer):
        return int(value)
    if isinstance(value, np.floating):
        return float(value)
    if isinstance(value, np.bool_):
        return bool(value)
    if isinstance(value, np.ndarray):
        return make_json_safe(value.tolist())
    if isinstance(value, dict):
        return {str(key): make_json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [make_json_safe(item) for item in value]
    if hasattr(value, "x") and hasattr(value, "y"):
        return {
            "x": float(value.x),
            "y": float(value.y),
            "z": float(value.z) if hasattr(value, "z") else 0.0,
        }
    if hasattr(value, "landmark"):
        try:
            return [make_json_safe(item) for item in value.landmark]
        except Exception:
            pass
    return str(value)

def decode_frame(frame_data):
    try:
        if not frame_data:
            return None
        if isinstance(frame_data, str) and "," in frame_data:
            frame_data = frame_data.split(",", 1)[1]
        image_bytes = base64.b64decode(frame_data)
        image_array = np.frombuffer(image_bytes, dtype=np.uint8)
        return cv2.imdecode(image_array, cv2.IMREAD_COLOR)
    except Exception as error:
        print(f"Frame decode error: {error}")
        return None

def get_violation_name(violation_type):
    names = {
        PHONE_DETECTED: "Phone detected",
        NO_FACE: "Face not present",
        "BLINK": "Blink violation",
        "MOUTH": "Mouth violation",
        "EYE_TRACKING": "Eye tracking violation",
        "TAB_SWITCH": "Tab switch detected",
        "FULLSCREEN_EXIT": "Fullscreen exited",
    }
    return names.get(violation_type, str(violation_type))

def register_violation(session, violation_type):
    if session.terminated:
        return {
            "action": "TERMINATE_EXAM",
            "violation_count": session.violation_count,
            "new_violation": False,
            "violation_type": violation_type,
            "message": "Exam already terminated.",
        }

    session.violation_count += 1
    count = session.violation_count
    session.last_violation_type = violation_type

    if count >= 2:
        session.last_action = "TERMINATE_EXAM"
        session.terminated = True
        message = f"VIOLATION 2: {get_violation_name(violation_type)}. Exam terminated."
        print("\n==============================================")
        print(message)
        print("==============================================\n")
        return {
            "action": "TERMINATE_EXAM",
            "violation_count": count,
            "new_violation": True,
            "violation_type": violation_type,
            "event_source": "PROCTORING",
            "warning": False,
            "pause": False,
            "pause_duration": 0,
            "message": message,
        }

    if violation_type == PHONE_DETECTED:
        session.last_action = "PAUSE_EXAM"
        message = "VIOLATION 1: Phone detected. The exam is paused for 10 seconds."
        print("\n==============================================")
        print(message)
        print("==============================================\n")
        return {
            "action": "PAUSE_EXAM",
            "violation_count": count,
            "new_violation": True,
            "violation_type": violation_type,
            "event_source": "AI",
            "warning": True,
            "pause": True,
            "pause_duration": 10,
            "message": message,
        }

    session.last_action = "WARNING"
    message = f"VIOLATION 1: {get_violation_name(violation_type)}."
    print("\n==============================================")
    print(message)
    print("==============================================\n")
    return {
        "action": "WARNING",
        "violation_count": count,
        "new_violation": True,
        "violation_type": violation_type,
        "event_source": "AI",
        "warning": True,
        "pause": False,
        "pause_duration": 0,
        "message": message,
    }

def browser_event_is_duplicate(session, event_name):
    now = time.time()
    last_time = session.last_browser_event_times.get(event_name, 0.0)
    if now - last_time < BROWSER_EVENT_COOLDOWN_SECONDS:
        return True
    session.last_browser_event_times[event_name] = now
    return False

def process_browser_violation(session, event_name, metadata=None):
    event_name = str(event_name or "").upper()
    metadata = metadata if isinstance(metadata, dict) else {}

    if session.terminated:
        return {
            "action": "TERMINATE_EXAM",
            "violation_count": session.violation_count,
            "new_violation": False,
            "violation_type": event_name,
            "event_source": "BROWSER",
            "message": "Exam already terminated.",
        }

    if event_name not in BROWSER_VIOLATIONS:
        return {
            "action": "NORMAL",
            "violation_count": session.violation_count,
            "new_violation": False,
            "violation_type": event_name,
            "event_source": "BROWSER",
            "message": "Browser event ignored.",
        }

    if browser_event_is_duplicate(session, event_name):
        return {
            "action": "NORMAL",
            "violation_count": session.violation_count,
            "new_violation": False,
            "violation_type": event_name,
            "event_source": "BROWSER",
            "message": "Duplicate browser event ignored.",
        }

    result = register_violation(session, event_name)
    result["event_source"] = "BROWSER"
    result["metadata"] = metadata
    return result

def normalize_blink_result(blink_result):
    if not isinstance(blink_result, dict):
        return {"blink_detected": False}
    if "blink_detected" in blink_result:
        return {**blink_result, "blink_detected": bool(blink_result.get("blink_detected"))}
    if "is_blink" in blink_result:
        return {**blink_result, "blink_detected": bool(blink_result.get("is_blink"))}
    if "blink" in blink_result:
        val = blink_result.get("blink")
        return {**blink_result, "blink_detected": bool(val) if isinstance(val, (int, float, bool)) else False}
    return {**blink_result, "blink_detected": False}

def normalize_mouth_result(mouth_result):
    if not isinstance(mouth_result, dict):
        return {"status": "NORMAL"}
    status = mouth_result.get("status", mouth_result.get("mouth_status", "NORMAL"))
    return {**mouth_result, "status": str(status).upper()}

def normalize_eye_result(eye_direction):
    if eye_direction is None:
        return {"status": "NORMAL"}
    direction = str(eye_direction).upper()
    if direction in {"LOOKING_CENTER", "CENTER", "NORMAL", "UNKNOWN"}:
        return {"status": "NORMAL"}
    return {"status": direction}

def analyze_frame(frame, session):
    session.frames_processed += 1

    try:
        face_result = face_detector.detect(frame)
    except Exception as error:
        print(f"Face detection error: {error}")
        face_result = {"status": "FACE_MISSING", "face_count": 0, "detections": []}

    try:
        mesh_result = mesh_detector.detect(frame)
    except Exception as error:
        print(f"Face mesh error: {error}")
        mesh_result = {"face_count": 0, "landmarks": [], "faces": []}

    eye_direction, blink_result, mouth_result = None, None, None

    if isinstance(mesh_result, dict) and mesh_result.get("face_count", 0) > 0:
        landmarks_list = mesh_result.get("landmarks", [])
        if not landmarks_list:
            faces = mesh_result.get("faces", [])
            if faces:
                landmarks_list = [faces[0].get("landmarks", [])]

        if landmarks_list:
            landmarks = convert_landmarks_for_detectors(landmarks_list[0])
            if len(landmarks) >= 478:
                try:
                    eye_direction = eye_tracker.get_eye_direction(landmarks)
                except Exception as error:
                    print(f"Eye tracking error: {error}")

                try:
                    blink_result = blink_detector.detect(landmarks)
                except Exception as error:
                    print(f"Blink detection error: {error}")

                try:
                    mouth_result = mouth_detector.detect(landmarks)
                except Exception as error:
                    print(f"Mouth detection error: {error}")

    try:
        phone_result = phone_detector.detect(frame)
    except Exception as error:
        print(f"Phone detection error: {error}")
        phone_result = {"status": "NO_PHONE", "count": 0, "confidence": 0.0}

    face_fraud = session.fraud_engine.process_face(face_result)
    phone_fraud = session.fraud_engine.process(phone_result)
    blink_fraud = session.fraud_engine.process_blink(normalize_blink_result(blink_result))
    mouth_fraud = session.fraud_engine.process_mouth(normalize_mouth_result(mouth_result))
    eye_fraud = session.fraud_engine.process_eye_tracking(normalize_eye_result(eye_direction))

    fraud_events = [
        ("FACE", face_fraud),
        ("PHONE", phone_fraud),
        ("BLINK", blink_fraud),
        ("MOUTH", mouth_fraud),
        ("EYE_TRACKING", eye_fraud),
    ]

    selected_event = None
    for source, fraud in fraud_events:
        if not isinstance(fraud, dict):
            continue
        if fraud.get("action", "NORMAL") in {"WARNING", "PAUSE_EXAM", "TERMINATE_EXAM"}:
            selected_event = (source, fraud)
            break

    fraud_result = {
        "action": "NORMAL",
        "violation_count": session.violation_count,
        "new_violation": False,
        "violation_type": None,
        "event_source": None,
        "pause_duration": 0,
        "message": "No new violation.",
    }

    if selected_event is not None:
        source, detector_result = selected_event
        violation_type = detector_result.get("violation_type")
        if not violation_type:
            if source == "FACE":
                violation_type = NO_FACE
            elif source == "PHONE":
                violation_type = PHONE_DETECTED
            else:
                violation_type = source

        fraud_result = register_violation(session, violation_type)
        fraud_result["detector_result"] = detector_result

    result = {
        "type": "PROCTORING_RESULT",
        "timestamp": time.time(),
        "face": {
            "status": face_result.get("status") if isinstance(face_result, dict) else None,
            "face_count": face_result.get("face_count", 0) if isinstance(face_result, dict) else 0,
        },
        "eyes": {"direction": eye_direction},
        "blink": blink_result,
        "mouth": mouth_result,
        "phone": phone_result,
        "fraud": fraud_result,
        "violation_count": session.violation_count,
    }

    return make_json_safe(result)

# -----------------------------------------------------------------------------
# WEBSOCKET PROCTORING ENDPOINT
# -----------------------------------------------------------------------------
@app.websocket("/ws/proctor")
async def proctor_websocket(websocket: WebSocket):
    await websocket.accept()
    print("\n==============================================")
    print("Proctoring Client Connected")
    print("==============================================\n")

    session = ProctoringSession()

    try:
        while True:
            message = await websocket.receive_json()
            if not isinstance(message, dict):
                continue

            message_type = message.get("type")

            if message_type == "START_EXAM":
                print("\nExamination started.")
                await websocket.send_json({
                    "type": "PROCTORING_STARTED",
                    "message": "AI proctoring started.",
                    "violation_count": session.violation_count,
                })
                continue

            if message_type == "STOP_EXAM":
                print("\nExamination stopped.")
                await websocket.send_json({
                    "type": "PROCTORING_STOPPED",
                    "message": "AI proctoring stopped.",
                    "violation_count": session.violation_count,
                })
                break

            if message_type == "BROWSER_VIOLATION":
                if session.terminated:
                    continue

                event_name = message.get("event")
                metadata = message.get("metadata", {})

                print("\nBrowser event:", event_name)
                browser_result = process_browser_violation(session, event_name, metadata)
                print(browser_result.get("message"))

                result = make_json_safe({
                    "type": "PROCTORING_RESULT",
                    "timestamp": time.time(),
                    "browser": {"event": event_name, "metadata": metadata},
                    "fraud": browser_result,
                    "violation_count": session.violation_count,
                })

                await websocket.send_json(result)

                if session.terminated:
                    print("\n==============================================")
                    print("EXAM TERMINATED")
                    print("Reason:", browser_result.get("message"))
                    print("Violation count:", session.violation_count)
                    print("==============================================\n")

                    await websocket.send_json({
                        "type": "EXAM_TERMINATED",
                        "reason": browser_result.get("message"),
                        "violation_type": browser_result.get("violation_type"),
                        "violation_count": session.violation_count,
                    })
                    await websocket.close()
                    break
                continue

            if message_type == "VIDEO_FRAME":
                if session.terminated:
                    continue

                frame_data = message.get("frame")
                if not frame_data:
                    continue

                frame = decode_frame(frame_data)
                if frame is None:
                    continue

                result = analyze_frame(frame, session)
                await websocket.send_json(result)

                if session.terminated:
                    fraud = result.get("fraud", {})
                    print("\n==============================================")
                    print("EXAM TERMINATED")
                    print("Reason:", fraud.get("message"))
                    print("Violation count:", session.violation_count)
                    print("==============================================\n")

                    await websocket.send_json({
                        "type": "EXAM_TERMINATED",
                        "reason": fraud.get("message", "Second violation. Exam terminated."),
                        "violation_type": fraud.get("violation_type"),
                        "violation_count": session.violation_count,
                    })
                    await websocket.close()
                    break
                continue

            print("Unknown message type:", message_type)

    except WebSocketDisconnect:
        print("Proctoring client disconnected.")
    except Exception as error:
        print(f"\n==============================================\nWebSocket error: {error}\n==============================================\n")
        try:
            await websocket.send_json({"type": "PROCTORING_ERROR", "message": str(error)})
        except Exception:
            pass
    finally:
        print("Proctoring session closed.")

# -----------------------------------------------------------------------------
# ROOT & HEALTH CHECK ROUTES
# -----------------------------------------------------------------------------
@app.get("/")
async def root():
    return {
        "service": "EduSaaS Unified AI Platform",
        "status": "running",
        "endpoints": {
            "proctoring_websocket": "/ws/proctor",
            "plagiarism_api": "/api/plagiarism/check",
            "quiz_api": "/api/quiz/*",
            "skill_gap_api": "/api/skill-gap/*"
        },
        "models": {
            "face_presence": "MediaPipe",
            "face_mesh": "MediaPipe",
            "eye_tracking": "MediaPipe",
            "blink": "MediaPipe",
            "mouth": "MediaPipe",
            "phone": "YOLO11s",
            "head_pose": "REMOVED",
        },
        "fraud_policy": {
            "global_violation_limit": 2,
            "violation_1": "WARNING",
            "phone_violation_1": "PAUSE_EXAM_10_SECONDS",
            "violation_2": "TERMINATE_EXAM",
        },
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "aiml-unified-service",
        "components": ["proctoring", "plagiarism", "quiz", "skill-gap"]
    }

# -----------------------------------------------------------------------------
# APPLICATION ENTRYPOINT
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    print("\n==============================================")
    print("Starting EduSaaS Unified AI & Proctoring Service")
    print("==============================================")
    print("HTTP Root          : http://0.0.0.0:8000/")
    print("Proctoring WS      : ws://0.0.0.0:8000/ws/proctor")
    print("Plagiarism Engine  : http://0.0.0.0:8000/api/plagiarism/check")
    print("Quiz API           : http://0.0.0.0:8000/api/quiz/")
    print("Skill Gap API      : http://0.0.0.0:8000/api/skill-gap/")
    print("==============================================\n")

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
    )