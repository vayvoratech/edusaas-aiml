import base64
import time

import cv2
import numpy as np
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from face_presence import FacePresenceDetector
from face_mesh import FaceMeshDetector
from eye_tracking import EyeTracker
from blink_detection import BlinkDetector
from mouth_detection import MouthDetector
from phone_detection import PhoneDetector
from fraud_engine import FraudEngine


app = FastAPI(title="EduSaaS AI Proctoring Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BROWSER_EVENT_COOLDOWN_SECONDS = 1.5

PHONE_DETECTED = "PHONE_DETECTED"
NO_FACE = "NO_FACE"

BROWSER_VIOLATIONS = {
    "TAB_SWITCH",
    "FULLSCREEN_EXIT",
}


print()
print("==============================================")
print("Loading EduSaaS AI Proctoring Models")
print("==============================================")

face_detector = FacePresenceDetector()
mesh_detector = FaceMeshDetector()
eye_tracker = EyeTracker()
blink_detector = BlinkDetector()
mouth_detector = MouthDetector()
phone_detector = PhoneDetector()

print()
print("==============================================")
print("AI Models Ready")
print("==============================================")
print("Face       : Ready")
print("Face Mesh  : Ready")
print("Eye        : Ready")
print("Blink      : Ready")
print("Mouth      : Ready")
print("Phone      : Ready")
print("Head Pose  : REMOVED")
print("==============================================")
print()


class ProctoringSession:

    def __init__(self):
        # Any TWO accepted violations terminate the exam.
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
        return {
            str(key): make_json_safe(item)
            for key, item in value.items()
        }

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

        image_array = np.frombuffer(
            image_bytes,
            dtype=np.uint8,
        )

        return cv2.imdecode(
            image_array,
            cv2.IMREAD_COLOR,
        )

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

    return names.get(
        violation_type,
        str(violation_type),
    )


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

    # ------------------------------------------------------
    # SECOND VIOLATION -> TERMINATE
    # ------------------------------------------------------
    if count >= 2:

        session.last_action = "TERMINATE_EXAM"
        session.terminated = True

        message = (
            f"VIOLATION 2: {get_violation_name(violation_type)}. "
            "Exam terminated."
        )

        print()
        print("==============================================")
        print(message)
        print("==============================================")

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

    # ------------------------------------------------------
    # FIRST PHONE VIOLATION -> PAUSE
    # ------------------------------------------------------
    if violation_type == PHONE_DETECTED:

        session.last_action = "PAUSE_EXAM"

        message = (
            "VIOLATION 1: Phone detected. "
            "The exam is paused for 10 seconds."
        )

        print()
        print("==============================================")
        print(message)
        print("==============================================")

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

    # ------------------------------------------------------
    # FIRST NON-PHONE VIOLATION -> WARNING
    # ------------------------------------------------------
    session.last_action = "WARNING"

    message = (
        f"VIOLATION 1: {get_violation_name(violation_type)}."
    )

    print()
    print("==============================================")
    print(message)
    print("==============================================")

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

    last_time = session.last_browser_event_times.get(
        event_name,
        0.0,
    )

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
        return {
            **blink_result,
            "blink_detected": bool(
                blink_result.get("blink_detected")
            ),
        }

    if "is_blink" in blink_result:
        return {
            **blink_result,
            "blink_detected": bool(
                blink_result.get("is_blink")
            ),
        }

    if "blink" in blink_result:
        value = blink_result.get("blink")

        if isinstance(value, bool):
            return {
                **blink_result,
                "blink_detected": value,
            }

        if isinstance(value, (int, float)):
            return {
                **blink_result,
                "blink_detected": bool(value),
            }

    return {
        **blink_result,
        "blink_detected": False,
    }


def normalize_mouth_result(mouth_result):

    if not isinstance(mouth_result, dict):
        return {"status": "NORMAL"}

    status = mouth_result.get(
        "status",
        mouth_result.get("mouth_status", "NORMAL"),
    )

    return {
        **mouth_result,
        "status": str(status).upper(),
    }


def normalize_eye_result(eye_direction):

    if eye_direction is None:
        return {"status": "NORMAL"}

    direction = str(eye_direction).upper()

    if direction in {
        "LOOKING_CENTER",
        "CENTER",
        "NORMAL",
        "UNKNOWN",
    }:
        return {"status": "NORMAL"}

    return {"status": direction}


def analyze_frame(frame, session):

    session.frames_processed += 1

    # ------------------------------------------------------
    # FACE PRESENCE
    # ------------------------------------------------------
    try:
        face_result = face_detector.detect(frame)

    except Exception as error:
        print(f"Face detection error: {error}")

        face_result = {
            "status": "FACE_MISSING",
            "face_count": 0,
            "detections": [],
        }

    # ------------------------------------------------------
    # FACE MESH
    # ------------------------------------------------------
    try:
        mesh_result = mesh_detector.detect(frame)

    except Exception as error:
        print(f"Face mesh error: {error}")

        mesh_result = {
            "face_count": 0,
            "landmarks": [],
            "faces": [],
        }

    eye_direction = None
    blink_result = None
    mouth_result = None

    # ------------------------------------------------------
    # FACE LANDMARK ANALYSIS
    # ------------------------------------------------------
    if (
        isinstance(mesh_result, dict)
        and mesh_result.get("face_count", 0) > 0
    ):

        landmarks_list = mesh_result.get(
            "landmarks",
            [],
        )

        if not landmarks_list:

            faces = mesh_result.get(
                "faces",
                [],
            )

            if faces:
                landmarks_list = [
                    faces[0].get(
                        "landmarks",
                        [],
                    )
                ]

        if landmarks_list:

            raw_landmarks = landmarks_list[0]

            landmarks = convert_landmarks_for_detectors(
                raw_landmarks
            )

            # MediaPipe Face Mesh normally provides 478 landmarks.
            # Do not use > 478 because exactly 478 is valid.
            if len(landmarks) >= 478:

                try:
                    eye_direction = (
                        eye_tracker.get_eye_direction(
                            landmarks
                        )
                    )

                except Exception as error:
                    print(f"Eye tracking error: {error}")

                try:
                    blink_result = (
                        blink_detector.detect(
                            landmarks
                        )
                    )

                except Exception as error:
                    print(f"Blink detection error: {error}")

                try:
                    mouth_result = (
                        mouth_detector.detect(
                            landmarks
                        )
                    )

                except Exception as error:
                    print(f"Mouth detection error: {error}")

    # ------------------------------------------------------
    # PHONE
    # ------------------------------------------------------
    try:
        phone_result = phone_detector.detect(frame)

    except Exception as error:
        print(f"Phone detection error: {error}")

        phone_result = {
            "status": "NO_PHONE",
            "count": 0,
            "confidence": 0.0,
        }

    # ------------------------------------------------------
    # FRAUD ENGINE
    # ------------------------------------------------------
    face_fraud = session.fraud_engine.process_face(
        face_result
    )

    phone_fraud = session.fraud_engine.process(
        phone_result
    )

    blink_fraud = session.fraud_engine.process_blink(
        normalize_blink_result(blink_result)
    )

    mouth_fraud = session.fraud_engine.process_mouth(
        normalize_mouth_result(mouth_result)
    )

    eye_fraud = session.fraud_engine.process_eye_tracking(
        normalize_eye_result(eye_direction)
    )

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

        action = fraud.get(
            "action",
            "NORMAL",
        )

        if action in {
            "WARNING",
            "PAUSE_EXAM",
            "TERMINATE_EXAM",
        }:
            selected_event = (
                source,
                fraud,
            )
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

        violation_type = detector_result.get(
            "violation_type"
        )

        if not violation_type:

            if source == "FACE":
                violation_type = NO_FACE

            elif source == "PHONE":
                violation_type = PHONE_DETECTED

            else:
                violation_type = source

        fraud_result = register_violation(
            session,
            violation_type,
        )

        fraud_result["detector_result"] = detector_result

    result = {
        "type": "PROCTORING_RESULT",
        "timestamp": time.time(),

        "face": {
            "status": (
                face_result.get("status")
                if isinstance(face_result, dict)
                else None
            ),
            "face_count": (
                face_result.get("face_count", 0)
                if isinstance(face_result, dict)
                else 0
            ),
        },

        "eyes": {
            "direction": eye_direction,
        },

        "blink": blink_result,
        "mouth": mouth_result,
        "phone": phone_result,

        "fraud": fraud_result,
        "violation_count": session.violation_count,
    }

    return make_json_safe(result)


@app.websocket("/ws/proctor")
async def proctor_websocket(websocket: WebSocket):

    await websocket.accept()

    print()
    print("==============================================")
    print("Proctoring Client Connected")
    print("==============================================")

    session = ProctoringSession()

    try:

        while True:

            message = await websocket.receive_json()

            if not isinstance(message, dict):
                continue

            message_type = message.get("type")

            # --------------------------------------------------
            # START EXAM
            # --------------------------------------------------
            if message_type == "START_EXAM":

                print()
                print("Examination started.")

                await websocket.send_json({
                    "type": "PROCTORING_STARTED",
                    "message": "AI proctoring started.",
                    "violation_count": session.violation_count,
                })

                continue

            # --------------------------------------------------
            # STOP EXAM
            # --------------------------------------------------
            if message_type == "STOP_EXAM":

                print()
                print("Examination stopped.")

                await websocket.send_json({
                    "type": "PROCTORING_STOPPED",
                    "message": "AI proctoring stopped.",
                    "violation_count": session.violation_count,
                })

                break

            # --------------------------------------------------
            # BROWSER VIOLATION
            # --------------------------------------------------
            if message_type == "BROWSER_VIOLATION":

                if session.terminated:
                    continue

                event_name = message.get("event")
                metadata = message.get("metadata", {})

                print()
                print("Browser event:", event_name)

                browser_result = process_browser_violation(
                    session,
                    event_name,
                    metadata,
                )

                print(browser_result.get("message"))

                result = {
                    "type": "PROCTORING_RESULT",
                    "timestamp": time.time(),
                    "browser": {
                        "event": event_name,
                        "metadata": metadata,
                    },
                    "fraud": browser_result,
                    "violation_count":
                        session.violation_count,
                }

                result = make_json_safe(result)

                await websocket.send_json(result)

                if session.terminated:

                    print()
                    print("==============================================")
                    print("EXAM TERMINATED")
                    print(
                        "Reason:",
                        browser_result.get("message"),
                    )
                    print(
                        "Violation count:",
                        session.violation_count,
                    )
                    print("==============================================")

                    await websocket.send_json({
                        "type": "EXAM_TERMINATED",
                        "reason":
                            browser_result.get("message"),
                        "violation_type":
                            browser_result.get("violation_type"),
                        "violation_count":
                            session.violation_count,
                    })

                    await websocket.close()
                    break

                continue

            # --------------------------------------------------
            # VIDEO FRAME
            # --------------------------------------------------
            if message_type == "VIDEO_FRAME":

                if session.terminated:
                    continue

                frame_data = message.get("frame")

                if not frame_data:
                    continue

                frame = decode_frame(frame_data)

                if frame is None:
                    continue

                result = analyze_frame(
                    frame,
                    session,
                )

                await websocket.send_json(result)

                if session.terminated:

                    fraud = result.get(
                        "fraud",
                        {},
                    )

                    print()
                    print("==============================================")
                    print("EXAM TERMINATED")
                    print(
                        "Reason:",
                        fraud.get("message"),
                    )
                    print(
                        "Violation count:",
                        session.violation_count,
                    )
                    print("==============================================")

                    await websocket.send_json({
                        "type": "EXAM_TERMINATED",
                        "reason": fraud.get(
                            "message",
                            "Second violation. Exam terminated.",
                        ),
                        "violation_type":
                            fraud.get("violation_type"),
                        "violation_count":
                            session.violation_count,
                    })

                    await websocket.close()
                    break

                continue

            print(
                "Unknown message type:",
                message_type,
            )

    except WebSocketDisconnect:

        print(
            "Proctoring client disconnected."
        )

    except Exception as error:

        print()
        print("==============================================")
        print("WebSocket error:", error)
        print("==============================================")

        try:
            await websocket.send_json({
                "type": "PROCTORING_ERROR",
                "message": str(error),
            })
        except Exception:
            pass

    finally:
        print("Proctoring session closed.")


@app.get("/")
async def root():

    return {
        "service": "EduSaaS AI Proctoring",
        "status": "running",
        "websocket": "/ws/proctor",

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
            "head_pose": "REMOVED",
        },

        "event_counters": {
            "blink_warning_at": 5,
            "blink_terminate_at": 10,
            "mouth_warning_at": 5,
            "mouth_terminate_at": 10,
            "eye_warning_at": 5,
            "eye_terminate_at": 10,
        },
    }


@app.get("/health")
async def health():

    return {
        "status": "healthy",
        "service": "ai-proctoring",
        "python": "3.13.x",
    }


if __name__ == "__main__":

    import uvicorn

    print()
    print("==============================================")
    print("Starting EduSaaS AI Proctoring Service")
    print("==============================================")
    print("HTTP : http://0.0.0.0:8000")
    print("WS   : ws://0.0.0.0:8000/ws/proctor")
    print()
    print("Fraud Policy:")
    print("Any first violation -> WARNING")
    print("First phone violation -> PAUSE_EXAM (10 seconds)")
    print("Any second violation -> TERMINATE_EXAM")
    print("Blink/Mouth/Eye event count -> 5 warning, 10 terminate")
    print("Head pose -> REMOVED")
    print("==============================================")

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
    )





