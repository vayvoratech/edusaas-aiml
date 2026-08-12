
import base64
import time
import head_pose
import face_mesh

import cv2
import numpy as np

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from face_presence import FacePresenceDetector
from face_mesh import FaceMeshDetector
from eye_tracking import EyeTracker
from blink_detection import BlinkDetector
from head_pose import HeadPoseDetector
from mouth_detection import MouthDetector
from phone_detection import PhoneDetector
from pathlib import Path



# ==========================================================
# FASTAPI
# ==========================================================

app = FastAPI(
    title="EduSaaS AI Proctoring Service"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==========================================================
# CONFIGURATION
# ==========================================================

VIOLATION_PERSISTENCE_SECONDS = 0.8

BROWSER_EVENT_COOLDOWN_SECONDS = 1.5


# ==========================================================
# VIOLATION TYPES
# ==========================================================

PHONE_DETECTED = "PHONE_DETECTED"
NO_FACE = "NO_FACE"
MULTIPLE_FACES = "MULTIPLE_FACES"
LOOKING_LEFT = "LOOKING_LEFT"
LOOKING_RIGHT = "LOOKING_RIGHT"
HEAD_TURNED = "HEAD_TURNED"


BROWSER_VIOLATIONS = {
    "TAB_SWITCH",
    "WINDOW_BLUR",
    "FULLSCREEN_EXIT",
    "COPY_ATTEMPT",
    "PASTE_ATTEMPT",
    "CUT_ATTEMPT",
    "RIGHT_CLICK",
    "SELECT_ALL_ATTEMPT",
    "DEVTOOLS_ATTEMPT",
    "VIEW_SOURCE_ATTEMPT",
}


# ==========================================================
# LOAD AI MODELS
# ==========================================================

print()
print("==============================================")
print("Loading EduSaaS AI Proctoring Models")
print("==============================================")

face_detector = FacePresenceDetector()

mesh_detector = FaceMeshDetector()

eye_tracker = EyeTracker()

blink_detector = BlinkDetector()

head_pose_detector = HeadPoseDetector()

mouth_detector = MouthDetector()

phone_detector = PhoneDetector()

print()
print("==============================================")
print("AI Models Ready")
print("==============================================")
print("Python    : 3.13.x")
print("MediaPipe : Ready")
print("YOLO11s   : Ready")
print("==============================================")
print()


# ==========================================================
# PROCTORING SESSION
# ==========================================================

class ProctoringSession:

    def __init__(self):

        self.violation_count = 0

        self.active_violations = set()

        self.violation_start_times = {}

        self.last_browser_event_times = {}

        self.last_action = "NORMAL"

        self.terminated = False

        self.frames_processed = 0

        self.started_at = time.time()


# ==========================================================
# LANDMARK CONVERTER
# ==========================================================

def convert_landmarks_for_detectors(landmarks):
    """
    face_mesh.py returns landmarks as:

        {
            "x": ...,
            "y": ...,
            "z": ...
        }

    EyeTracker can handle this format, but the existing
    HeadPoseDetector and MouthDetector expect:

        (x, y, z)

    Therefore, convert everything to tuples here.
    """

    converted = []

    if not landmarks:
        return converted

    for landmark in landmarks:

        # --------------------------------------------------
        # Dictionary returned by face_mesh.py
        # --------------------------------------------------

        if isinstance(landmark, dict):

            converted.append(
                (
                    float(
                        landmark.get(
                            "x",
                            0.0
                        )
                    ),

                    float(
                        landmark.get(
                            "y",
                            0.0
                        )
                    ),

                    float(
                        landmark.get(
                            "z",
                            0.0
                        )
                    )
                )
            )

            continue

        # --------------------------------------------------
        # Tuple / list
        # --------------------------------------------------

        if isinstance(
            landmark,
            (list, tuple)
        ):

            if len(landmark) >= 3:

                converted.append(
                    (
                        float(landmark[0]),
                        float(landmark[1]),
                        float(landmark[2])
                    )
                )

            elif len(landmark) >= 2:

                converted.append(
                    (
                        float(landmark[0]),
                        float(landmark[1]),
                        0.0
                    )
                )

            continue

        # --------------------------------------------------
        # Raw MediaPipe landmark object
        # --------------------------------------------------

        if (
            hasattr(landmark, "x")
            and
            hasattr(landmark, "y")
        ):

            converted.append(
                (
                    float(landmark.x),
                    float(landmark.y),

                    float(
                        landmark.z
                    )
                    if hasattr(
                        landmark,
                        "z"
                    )
                    else 0.0
                )
            )

    return converted


# ==========================================================
# JSON SAFE CONVERTER
# ==========================================================

def make_json_safe(value):

    if value is None:
        return None

    if isinstance(
        value,
        (str, int, float, bool)
    ):
        return value

    if isinstance(
        value,
        np.integer
    ):
        return int(value)

    if isinstance(
        value,
        np.floating
    ):
        return float(value)

    if isinstance(
        value,
        np.bool_
    ):
        return bool(value)

    if isinstance(
        value,
        np.ndarray
    ):
        return make_json_safe(
            value.tolist()
        )

    if isinstance(
        value,
        dict
    ):

        return {
            str(key):
            make_json_safe(item)

            for key, item
            in value.items()
        }

    if isinstance(
        value,
        (list, tuple, set)
    ):

        return [
            make_json_safe(item)
            for item in value
        ]

    # ------------------------------------------------------
    # MediaPipe landmark object
    # ------------------------------------------------------

    if (
        hasattr(value, "x")
        and
        hasattr(value, "y")
        and
        hasattr(value, "z")
    ):

        return {
            "x": float(value.x),
            "y": float(value.y),
            "z": float(value.z)
        }

    # ------------------------------------------------------
    # MediaPipe landmark list
    # ------------------------------------------------------

    if hasattr(
        value,
        "landmark"
    ):

        try:

            return [
                make_json_safe(
                    landmark
                )
                for landmark
                in value.landmark
            ]

        except Exception:
            pass

    return str(value)


# ==========================================================
# FRAME DECODER
# ==========================================================

def decode_frame(frame_data):

    try:

        if not frame_data:
            return None

        if isinstance(
            frame_data,
            str
        ):

            if "," in frame_data:

                frame_data = (
                    frame_data
                    .split(",", 1)[1]
                )

        image_bytes = base64.b64decode(
            frame_data
        )

        image_array = np.frombuffer(
            image_bytes,
            dtype=np.uint8
        )

        frame = cv2.imdecode(
            image_array,
            cv2.IMREAD_COLOR
        )

        return frame

    except Exception as error:

        print(
            f"Frame decode error: {error}"
        )

        return None


# ==========================================================
# GET CURRENT AI VIOLATIONS
# ==========================================================

def get_current_ai_violations(
    face_result,
    eye_direction,
    head_result,
    phone_result
):

    violations = set()

    # ======================================================
    # PHONE
    # ======================================================

    if isinstance(
        phone_result,
        dict
    ):

        phone_status = (
            phone_result.get(
                "status"
            )
        )

        phone_count = (
            phone_result.get(
                "count",
                0
            )
        )

        if (
            phone_status ==
            PHONE_DETECTED
            or
            phone_count > 0
        ):

            violations.add(
                PHONE_DETECTED
            )

    # ======================================================
    # FACE
    # ======================================================

    face_count = 0

    if isinstance(
        face_result,
        dict
    ):

        face_count = (
            face_result.get(
                "face_count",
                0
            )
        )

    if face_count == 0:

        violations.add(
            NO_FACE
        )

    elif face_count > 1:

        violations.add(
            MULTIPLE_FACES
        )

    # ======================================================
    # EYE DIRECTION
    # ======================================================

    if eye_direction == LOOKING_LEFT:

        violations.add(
            LOOKING_LEFT
        )

    elif eye_direction == LOOKING_RIGHT:

        violations.add(
            LOOKING_RIGHT
        )

    # ======================================================
    # HEAD POSE
    # ======================================================

    if isinstance(
        head_result,
        dict
    ):

        head_status = (
            head_result.get(
                "status"
            )
        )

        if head_status:

            status = str(
                head_status
            ).upper()

            normal_states = {
                "NORMAL",
                "CENTER",
                "CENTERED",
                "LOOKING_CENTER",
                "HEAD_NORMAL",
            }

            if status not in normal_states:

                if (
                    "TURN" in status
                    or
                    "LEFT" in status
                    or
                    "RIGHT" in status
                    or
                    "AWAY" in status
                    or
                    "UP" in status
                    or
                    "DOWN" in status
                ):

                    violations.add(
                        HEAD_TURNED
                    )

    return violations


# ==========================================================
# PROCESS AI VIOLATIONS
# ==========================================================

def process_ai_violations(
    session,
    current_violations
):

    now = time.time()

    confirmed_violation = None

    # ======================================================
    # START / CHECK PERSISTENCE
    # ======================================================

    for violation in current_violations:

        if violation in session.active_violations:
            continue

        if (
            violation
            not in
            session.violation_start_times
        ):

            session.violation_start_times[
                violation
            ] = now

            continue

        elapsed = (
            now
            -
            session.violation_start_times[
                violation
            ]
        )

        if (
            elapsed
            >=
            VIOLATION_PERSISTENCE_SECONDS
        ):

            session.active_violations.add(
                violation
            )

            session.violation_start_times.pop(
                violation,
                None
            )

            confirmed_violation = (
                violation
            )

            break

    # ======================================================
    # REMOVE ENDED VIOLATIONS
    # ======================================================

    for violation in list(
        session.active_violations
    ):

        if (
            violation
            not in
            current_violations
        ):

            session.active_violations.remove(
                violation
            )

    # ======================================================
    # REMOVE OLD TIMERS
    # ======================================================

    for violation in list(
        session.violation_start_times
    ):

        if (
            violation
            not in
            current_violations
        ):

            session.violation_start_times.pop(
                violation,
                None
            )

    if confirmed_violation is None:

        return {
            "new_violation": False,
            "violation_type": None
        }

    return {
        "new_violation": True,
        "violation_type":
            confirmed_violation
    }


# ==========================================================
# BROWSER EVENT DUPLICATE CHECK
# ==========================================================

def is_duplicate_browser_event(
    session,
    event_name
):

    now = time.time()

    if event_name in {
        "TAB_SWITCH",
        "WINDOW_BLUR"
    }:

        last_tab = (
            session
            .last_browser_event_times
            .get(
                "TAB_SWITCH",
                0
            )
        )

        last_blur = (
            session
            .last_browser_event_times
            .get(
                "WINDOW_BLUR",
                0
            )
        )

        latest = max(
            last_tab,
            last_blur
        )

        if (
            now - latest
            <
            BROWSER_EVENT_COOLDOWN_SECONDS
        ):

            return True

    last_time = (
        session
        .last_browser_event_times
        .get(
            event_name,
            0
        )
    )

    if (
        now - last_time
        <
        BROWSER_EVENT_COOLDOWN_SECONDS
    ):

        return True

    return False


# ==========================================================
# PROCESS BROWSER VIOLATION
# ==========================================================

def process_browser_violation(
    session,
    event_name,
    metadata=None
):

    event_name = str(
        event_name or ""
    ).upper()

    if (
        event_name
        not in
        BROWSER_VIOLATIONS
    ):

        return {

            "action":
                "NORMAL",

            "violation_count":
                session.violation_count,

            "new_violation":
                False,

            "violation_type":
                event_name,

            "event_source":
                "BROWSER",

            "message":
                "Unknown browser event ignored."

        }

    if is_duplicate_browser_event(
        session,
        event_name
    ):

        return {

            "action":
                "NORMAL",

            "violation_count":
                session.violation_count,

            "new_violation":
                False,

            "violation_type":
                event_name,

            "event_source":
                "BROWSER",

            "message":
                "Duplicate browser event ignored."

        }

    now = time.time()

    session.last_browser_event_times[
        event_name
    ] = now

    session.violation_count += 1

    # ======================================================
    # FIRST VIOLATION
    # ======================================================

    if session.violation_count == 1:

        session.last_action = "WARNING"

        return {

            "action":
                "WARNING",

            "violation_count":
                1,

            "new_violation":
                True,

            "violation_type":
                event_name,

            "event_source":
                "BROWSER",

            "metadata":
                metadata or {},

            "message":
                "First proctoring violation detected. "
                "Please follow the examination rules."

        }

    # ======================================================
    # SECOND VIOLATION
    # ======================================================

    session.last_action = (
        "TERMINATE_EXAM"
    )

    session.terminated = True

    return {

        "action":
            "TERMINATE_EXAM",

        "violation_count":
            session.violation_count,

        "new_violation":
            True,

        "violation_type":
            event_name,

        "event_source":
            "BROWSER",

        "metadata":
            metadata or {},

        "message":
            "Maximum proctoring violations exceeded. "
            "The examination has been terminated."

    }


# ==========================================================
# ANALYZE FRAME
# ==========================================================

def analyze_frame(
    frame,
    session
):

    session.frames_processed += 1

    # ======================================================
    # FACE PRESENCE
    # ======================================================

    try:

        face_result = (
            face_detector.detect(
                frame
            )
        )

    except Exception as error:

        print(
            f"Face detection error: {error}"
        )

        face_result = {

            "status":
                "FACE_MISSING",

            "face_count":
                0,

            "color":
                (0, 0, 255),

            "detections":
                []

        }

    # ======================================================
    # FACE MESH
    # ======================================================

    try:

        mesh_result = (
            mesh_detector.detect(
                frame
            )
        )

    except Exception as error:

        print(
            f"Face mesh error: {error}"
        )

        mesh_result = {

            "face_count":
                0,

            "landmarks":
                [],

            "blendshapes":
                [],

            "transformation_matrices":
                []

        }

    # ======================================================
    # DEFAULT RESULTS
    # ======================================================

    eye_direction = None

    blink_result = None

    head_result = {
    "status": "UNKNOWN",
    "angles": (0.0, 0.0, 0.0),
    "color": (255, 255, 255)
    }

    mouth_result = None 

    # ======================================================
    # FACE ANALYSIS
    # ======================================================

    if (
        isinstance(
            mesh_result,
            dict
        )
        and
        mesh_result.get(
            "face_count",
            0
        ) > 0
    ):

        landmarks_list = (
            mesh_result.get(
                "landmarks",
                []
            )
        )

        if landmarks_list:

            # ------------------------------------------------
            # Original landmarks from FaceMeshDetector
            # ------------------------------------------------

            raw_landmarks = (
                landmarks_list[0]
            )

            # ------------------------------------------------
            # Convert to tuple format
            # ------------------------------------------------

            landmarks = (
                convert_landmarks_for_detectors(
                    raw_landmarks
                )
            )
            print(
                f"DEBUG: raw landmarks = {len(raw_landmarks)}, "
                f"converted landmarks = {len(landmarks)}"
            )
            
            # ------------------------------------------------
            # Make sure all expected landmarks exist
            # ------------------------------------------------
            if len(landmarks) >= 292:
                try:
            
                    head_result = (
                        head_pose_detector.detect(
                            landmarks,
                            frame
                        )
                    )
                            
            
                except Exception as error:
            
                    print(
                        f"Head pose error: {error}"
                    )
                    head_result = {
                        "status": "UNKNOWN",
                        "angles": (
                            0.0,
                            0.0,
                            0.0
                        ),
                        "color": (
                            255,
                            255,
                            255
                        )
                    }
            
            else:
            
                print(
                    "Head pose skipped. "
                    f"Only {len(landmarks)} landmarks."
                )

            if len(landmarks) > 478:

                # ============================================
                # EYE TRACKING
                # ============================================

                try:

                    eye_direction = (
                        eye_tracker
                        .get_eye_direction(
                            landmarks
                        )
                    )

                except Exception as error:

                    print(
                        f"Eye tracking error: {error}"
                    )

                # ============================================
                # BLINK
                # ============================================

                try:

                    blink_result = (
                        blink_detector.detect(
                            landmarks
                        )
                    )

                except Exception as error:

                    print(
                        f"Blink detection error: {error}"
                    )

                # ============================================
                # HEAD POSE
                # ===========================================
                    
                # ============================================
                # MOUTH
                # ============================================

                try:

                    mouth_result = (
                        mouth_detector.detect(
                            landmarks
                        )
                    )

                except Exception as error:

                    print(
                        f"Mouth detection error: {error}"
                    )

            else:

                print(
                    "Face mesh returned insufficient "
                    "landmarks."
                )

    # ======================================================
    # PHONE DETECTION
    # ======================================================

    try:

        phone_result = (
            phone_detector.detect(
                frame
            )
        )

    except Exception as error:

        print(
            f"Phone detection error: {error}"
        )

        phone_result = {

            "status":
                "NO_PHONE",

            "phones":
                [],

            "count":
                0,

            "confidence":
                0.0,

            "timestamp":
                time.time()

        }

    # ======================================================
    # CURRENT AI VIOLATIONS
    # ======================================================

    current_violations = (
        get_current_ai_violations(

            face_result,

            eye_direction,

            head_result,

            phone_result

        )
    )

    # ======================================================
    # PROCESS AI VIOLATIONS
    # ======================================================

    ai_fraud = (
        process_ai_violations(

            session,

            current_violations

        )
    )

    # ======================================================
    # DEFAULT FRAUD RESULT
    # ======================================================

    fraud_result = {

        "action":
            "NORMAL",

        "violation_count":
            session.violation_count,

        "new_violation":
            False,

        "violation_type":
            None,

        "event_source":
            None,

        "message":
            "No new violation."

    }

    # ======================================================
    # NEW AI VIOLATION
    # ======================================================

    if ai_fraud[
        "new_violation"
    ]:

        violation_type = (
            ai_fraud[
                "violation_type"
            ]
        )

        session.violation_count += 1

        # ==================================================
        # FIRST VIOLATION
        # ==================================================

        if session.violation_count == 1:

            session.last_action = (
                "WARNING"
            )

            fraud_result = {

                "action":
                    "WARNING",

                "violation_count":
                    session.violation_count,

                "new_violation":
                    True,

                "violation_type":
                    violation_type,

                "event_source":
                    "AI",

                "message":
                    "First proctoring violation detected. "
                    "Please follow the examination rules."

            }

        # ==================================================
        # SECOND VIOLATION
        # ==================================================

        else:

            session.last_action = (
                "TERMINATE_EXAM"
            )

            session.terminated = True

            fraud_result = {

                "action":
                    "TERMINATE_EXAM",

                "violation_count":
                    session.violation_count,

                "new_violation":
                    True,

                "violation_type":
                    violation_type,

                "event_source":
                    "AI",

                "message":
                    "Maximum proctoring violations exceeded. "
                    "The examination has been terminated."

            }

    # ======================================================
    # CLEAN WEBSOCKET RESULT
    # ======================================================
    #
    # IMPORTANT:
    #
    # Do NOT send the complete mesh_result.
    #
    # The browser does not need 478+ landmarks.
    #
    # ======================================================

    result = {

        "type":
            "PROCTORING_RESULT",

        "timestamp":
            time.time(),

        "face": {

            "status":
                face_result.get(
                    "status"
                ),

            "face_count":
                face_result.get(
                    "face_count",
                    0
                )

        },

        "eyes": {

            "direction":
                eye_direction

        },

        "blink":
            blink_result,

        "head":
            head_result,

        "mouth":
            mouth_result,

        "phone":
            phone_result,

        "fraud":
            fraud_result

    }

    return make_json_safe(
        result
    )


# ==========================================================
# WEBSOCKET
# ==========================================================

@app.websocket(
    "/ws/proctor"
)
async def proctor_websocket(
    websocket: WebSocket
):

    await websocket.accept()

    print()
    print("==============================================")
    print("Proctoring Client Connected")
    print("==============================================")

    session = ProctoringSession()

    try:

        while True:

            message = (
                await websocket.receive_json()
            )

            if not isinstance(
                message,
                dict
            ):

                print(
                    "Invalid WebSocket message ignored."
                )

                continue

            message_type = (
                message.get(
                    "type"
                )
            )

            # ==================================================
            # START EXAM
            # ==================================================

            if (
                message_type ==
                "START_EXAM"
            ):

                print()
                print(
                    "Examination started."
                )

                await websocket.send_json({

                    "type":
                        "PROCTORING_STARTED",

                    "message":
                        "AI proctoring started.",

                    "violation_count":
                        session.violation_count

                })

                continue

            # ==================================================
            # STOP EXAM
            # ==================================================

            if (
                message_type ==
                "STOP_EXAM"
            ):

                print()
                print(
                    "Examination stopped."
                )

                await websocket.send_json({

                    "type":
                        "PROCTORING_STOPPED",

                    "message":
                        "AI proctoring stopped.",

                    "violation_count":
                        session.violation_count

                })

                break

            # ==================================================
            # BROWSER VIOLATION
            # ==================================================

            if (
                message_type ==
                "BROWSER_VIOLATION"
            ):

                if session.terminated:
                    continue

                event_name = (
                    message.get(
                        "event"
                    )
                )

                metadata = (
                    message.get(
                        "metadata",
                        {}
                    )
                )

                print()
                print(
                    "----------------------------------------------"
                )

                print(
                    "Browser violation:",
                    event_name
                )

                browser_result = (
                    process_browser_violation(

                        session,

                        event_name,

                        metadata

                    )
                )

                print(
                    "Action:",
                    browser_result[
                        "action"
                    ]
                )

                print(
                    "Violation count:",
                    session.violation_count
                )

                print(
                    "----------------------------------------------"
                )

                result = {

                    "type":
                        "PROCTORING_RESULT",

                    "timestamp":
                        time.time(),

                    "browser": {

                        "event":
                            event_name,

                        "metadata":
                            metadata

                    },

                    "fraud":
                        browser_result

                }

                await websocket.send_json(
                    make_json_safe(
                        result
                    )
                )

                # ==================================================
                # TERMINATE
                # ==================================================

                if session.terminated:

                    print()
                    print(
                        "=============================================="
                    )

                    print(
                        "EXAM TERMINATED"
                    )

                    print(
                        "Violation type:",
                        event_name
                    )

                    print(
                        "Violation count:",
                        session.violation_count
                    )

                    print(
                        "=============================================="
                    )

                    await websocket.send_json({

                        "type":
                            "EXAM_TERMINATED",

                        "reason":
                            browser_result.get(
                                "message"
                            ),

                        "violation_type":
                            event_name,

                        "violation_count":
                            session.violation_count

                    })

                    await websocket.close()

                    break

                continue

            # ==================================================
            # VIDEO FRAME
            # ==================================================

            if (
                message_type ==
                "VIDEO_FRAME"
            ):

                if session.terminated:
                    continue

                frame_data = (
                    message.get(
                        "frame"
                    )
                )

                if not frame_data:
                    continue

                frame = decode_frame(
                    frame_data
                )

                if frame is None:
                    continue

                result = analyze_frame(
                    frame,
                    session
                )

                await websocket.send_json(
                    result
                )

                # ==================================================
                # TERMINATE
                # ==================================================

                if session.terminated:

                    print()
                    print(
                        "=============================================="
                    )

                    print(
                        "EXAM TERMINATED"
                    )

                    print(
                        "Violation type:",
                        result[
                            "fraud"
                        ].get(
                            "violation_type"
                        )
                    )

                    print(
                        "Violation count:",
                        session.violation_count
                    )

                    print(
                        "=============================================="
                    )

                    await websocket.send_json({

                        "type":
                            "EXAM_TERMINATED",

                        "reason":
                            result[
                                "fraud"
                            ].get(
                                "message"
                            ),

                        "violation_type":
                            result[
                                "fraud"
                            ].get(
                                "violation_type"
                            ),

                        "violation_count":
                            session.violation_count

                    })

                    await websocket.close()

                    break

                continue

            # ==================================================
            # UNKNOWN MESSAGE
            # ==================================================

            print(
                "Unknown WebSocket message:",
                message_type
            )

    except WebSocketDisconnect:

        print()
        print(
            "Proctoring client disconnected."
        )

    except Exception as error:

        print()
        print(
            "=============================================="
        )

        print(
            "WebSocket error:",
            error
        )

        print(
            "=============================================="
        )

        try:

            await websocket.send_json({

                "type":
                    "PROCTORING_ERROR",

                "message":
                    str(error)

            })

        except Exception:
            pass

    finally:

        print(
            "Proctoring session closed."
        )


# ==========================================================
# ROOT
# ==========================================================

@app.get("/")
async def root():

    return {

        "service":
            "EduSaaS AI Proctoring",

        "status":
            "running",

        "python":
            "3.13.x",

        "websocket":
            "/ws/proctor",

        "models": {

            "face_presence":
                "MediaPipe Tasks",

            "face_mesh":
                "MediaPipe Face Landmarker",

            "eye_tracking":
                "MediaPipe",

            "blink":
                "MediaPipe",

            "head_pose":
                "MediaPipe",

            "mouth":
                "MediaPipe",

            "phone":
                "YOLO11s"

        },

        "fraud_policy": {

            "first_violation":
                "WARNING",

            "second_violation":
                "TERMINATE_EXAM"

        }

    }


# ==========================================================
# HEALTH
# ==========================================================

@app.get("/health")
async def health():

    return {

        "status":
            "healthy",

        "service":
            "ai-proctoring",

        "python":
            "3.13.x"

    }


# ==========================================================
# START SERVER
# ==========================================================

if __name__ == "__main__":

    import uvicorn

    print()
    print("==============================================")
    print("Starting EduSaaS AI Proctoring Service")
    print("==============================================")
    print("Python : 3.13.x")
    print("HTTP   : http://0.0.0.0:8000")
    print("WS     : ws://0.0.0.0:8000/ws/proctor")
    print()
    print("Fraud Policy:")
    print("1st violation -> WARNING")
    print("2nd violation -> TERMINATE_EXAM")
    print("==============================================")

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000
    )






'''
import base64
import time
import cv2
import numpy as np

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware


# ==========================================================
# AI DETECTORS
# ==========================================================

from face_presence import FacePresenceDetector
from face_mesh import FaceMeshDetector
from eye_tracking import EyeTracker
from blink_detection import BlinkDetector
from head_pose import HeadPoseDetector
from mouth_detection import MouthDetector
from phone_detection import PhoneDetector


# ==========================================================
# FASTAPI
# ==========================================================

app = FastAPI(
    title="EduSaaS AI Proctoring Service"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==========================================================
# CONFIGURATION
# ==========================================================

VIOLATION_PERSISTENCE_SECONDS = 3.0

BROWSER_EVENT_COOLDOWN_SECONDS = 1.5


# ==========================================================
# AI VIOLATIONS
# ==========================================================

PHONE = "PHONE_DETECTED"

NO_FACE = "NO_FACE"

MULTIPLE_FACES = "MULTIPLE_FACES"

LOOKING_LEFT = "LOOKING_LEFT"

LOOKING_RIGHT = "LOOKING_RIGHT"

HEAD_TURNED = "HEAD_TURNED"


# ==========================================================
# BROWSER VIOLATIONS
# ==========================================================

BROWSER_VIOLATIONS = {

    # Only these browser events create fraud violations.
    # Copy/paste/right-click/devtools/etc. are ignored by
    # the fraud engine for now, as requested.
    "TAB_SWITCH",

    "FULLSCREEN_EXIT"

}


# ==========================================================
# JSON SAFE CONVERTER
# ==========================================================
#
# MediaPipe returns protobuf objects such as:
#
# NormalizedLandmarkList
#
# These cannot be sent directly through:
#
# websocket.send_json()
#
# So everything is converted into standard:
#
# dict
# list
# int
# float
# bool
# None
#
# ==========================================================

def make_json_safe(obj):

    # ------------------------------------------------------
    # None
    # ------------------------------------------------------

    if obj is None:

        return None


    # ------------------------------------------------------
    # Basic JSON types
    # ------------------------------------------------------

    if isinstance(
        obj,
        (str, int, float, bool)
    ):

        return obj


    # ------------------------------------------------------
    # NumPy types
    # ------------------------------------------------------

    if isinstance(
        obj,
        np.integer
    ):

        return int(obj)


    if isinstance(
        obj,
        np.floating
    ):

        return float(obj)


    if isinstance(
        obj,
        np.bool_
    ):

        return bool(obj)


    # ------------------------------------------------------
    # NumPy arrays
    # ------------------------------------------------------

    if isinstance(
        obj,
        np.ndarray
    ):

        return [
            make_json_safe(x)
            for x in obj.tolist()
        ]


    # ------------------------------------------------------
    # Dictionary
    # ------------------------------------------------------

    if isinstance(
        obj,
        dict
    ):

        return {

            str(key):
                make_json_safe(value)

            for key, value in obj.items()

        }


    # ------------------------------------------------------
    # List / Tuple / Set
    # ------------------------------------------------------

    if isinstance(
        obj,
        (list, tuple, set)
    ):

        return [

            make_json_safe(x)

            for x in obj

        ]


    # ======================================================
    # MEDIAPIPE NORMALIZED LANDMARK
    # ======================================================
    #
    # Example:
    #
    # NormalizedLandmark(
    #     x=0.4,
    #     y=0.5,
    #     z=-0.1
    # )
    #
    # ======================================================

    if (
        hasattr(obj, "x")
        and
        hasattr(obj, "y")
        and
        hasattr(obj, "z")
    ):

        result = {

            "x":
                float(obj.x),

            "y":
                float(obj.y),

            "z":
                float(obj.z)

        }


        # --------------------------------------------------
        # Optional MediaPipe fields
        # --------------------------------------------------

        if hasattr(
            obj,
            "visibility"
        ):

            try:

                result[
                    "visibility"
                ] = float(
                    obj.visibility
                )

            except Exception:

                pass


        if hasattr(
            obj,
            "presence"
        ):

            try:

                result[
                    "presence"
                ] = float(
                    obj.presence
                )

            except Exception:

                pass


        return result


    # ======================================================
    # MEDIAPIPE NORMALIZED LANDMARK LIST
    # ======================================================

    if hasattr(
        obj,
        "landmark"
    ):

        try:

            return [

                make_json_safe(
                    landmark
                )

                for landmark
                in obj.landmark

            ]

        except Exception:

            pass


    # ======================================================
    # OBJECT WITH __dict__
    # ======================================================

    if hasattr(
        obj,
        "__dict__"
    ):

        try:

            return make_json_safe(
                vars(obj)
            )

        except Exception:

            pass


    # ======================================================
    # FALLBACK
    # ======================================================

    return str(obj)


# ==========================================================
# INITIALIZE MODELS
# ==========================================================

print()
print("==============================================")
print("EduSaaS AI Proctoring Service")
print("==============================================")
print()

print("Loading AI models...")


face_detector = FacePresenceDetector()

mesh_detector = FaceMeshDetector()

eye_tracker = EyeTracker()

blink_detector = BlinkDetector()

head_pose_detector = HeadPoseDetector()

mouth_detector = MouthDetector()

phone_detector = PhoneDetector()


print()
print("==============================================")
print("AI Models Ready")
print("==============================================")
print("MediaPipe : Ready")
print("YOLO11s   : Ready")
print("==============================================")
print()


# ==========================================================
# PROCTORING SESSION
# ==========================================================

class ProctoringSession:

    def __init__(self):

        # ======================================================
        # OVERALL VIOLATION COUNTERS
        # ======================================================

        # Browser violations:
        #   1 -> WARNING
        #   2 -> WARNING
        #   3 -> WARNING
        #   4 -> TERMINATE_EXAM
        self.browser_violation_count = 0

        # Keep this for compatibility with the existing
        # response/frontend fields.
        self.violation_count = 0

        # Mobile violations:
        #   1 -> PAUSE_EXAM + WARNING (10 sec)
        #   2 -> PAUSE_EXAM + WARNING (10 sec)
        #   3 -> TERMINATE_EXAM
        self.phone_violation_count = 0

        # Face-missing violations:
        #   1 -> WARNING
        #   2 -> WARNING
        #   3 -> TERMINATE_EXAM
        self.face_violation_count = 0

        # ======================================================
        # ACTIVE / PERSISTENCE STATE
        # ======================================================

        self.active_violations = set()
        self.violation_start_times = {}

        # Prevents one continuous phone/face violation from
        # being counted repeatedly on every camera frame.
        self.violation_event_counted = set()

        # ======================================================
        # BROWSER EVENT STATE
        # ======================================================

        self.last_browser_event_times = {}

        # ======================================================
        # EXAM STATE
        # ======================================================

        self.last_action = "NORMAL"
        self.terminated = False
        self.frames_processed = 0
        self.started_at = time.time()


# ==========================================================
# DECODE FRAME
# ==========================================================

def decode_frame(frame_data):

    try:

        if isinstance(
            frame_data,
            str
        ):

            if "," in frame_data:

                frame_data = (
                    frame_data
                    .split(",", 1)[1]
                )


        image_bytes = base64.b64decode(
            frame_data
        )


        np_array = np.frombuffer(
            image_bytes,
            dtype=np.uint8
        )


        frame = cv2.imdecode(
            np_array,
            cv2.IMREAD_COLOR
        )


        return frame


    except Exception as e:

        print(
            f"Frame decode error: {e}"
        )

        return None


# ==========================================================
# GET CURRENT AI VIOLATIONS
# ==========================================================

def get_current_violations(
    face_result,
    mesh_result,
    eye_direction,
    head_result,
    phone_result
):

    violations = set()

    # ======================================================
    # PHONE
    # ======================================================

    if isinstance(phone_result, dict):

        phone_status = phone_result.get(
            "status"
        )

        phone_count = phone_result.get(
            "count",
            0
        )

        if (
            phone_status == PHONE
            or phone_count > 0
        ):
            violations.add(PHONE)


    # ======================================================
    # FACE
    # ======================================================

    face_count = 0

    if isinstance(face_result, dict):

        face_count = face_result.get(
            "face_count",
            0
        )

    # Only "face not detected" is a fraud violation.
    #
    # Multiple faces are NOT counted here because the requested
    # policy only specifies the missing-face rule.
    if face_count == 0:

        violations.add(NO_FACE)


    # ======================================================
    # IMPORTANT:
    #
    # HEAD POSE
    # EYE TRACKING
    # BLINK DETECTION
    #
    # DO NOT ADD THEM TO violations.
    #
    # They can still run for information/telemetry, but they
    # must never increase the fraud violation counter.
    # ======================================================

    return violations


# ==========================================================
# PROCESS CAMERA VIOLATIONS
# ==========================================================

def process_camera_violations(
    session,
    current_violations
):

    now = time.time()

    confirmed_violation = None

    # ======================================================
    # START / CHECK PERSISTENCE FOR NEW AI VIOLATIONS
    # ======================================================

    for violation in current_violations:

        # Already confirmed and active. Do not count it again
        # until the violation disappears and later reappears.
        if violation in session.active_violations:
            continue

        # Start persistence timer.
        if violation not in session.violation_start_times:

            session.violation_start_times[
                violation
            ] = now

            continue

        elapsed = (
            now
            -
            session.violation_start_times[
                violation
            ]
        )

        # Violation must persist continuously for the configured
        # duration before becoming a real violation.
        if elapsed >= VIOLATION_PERSISTENCE_SECONDS:

            session.active_violations.add(
                violation
            )

            del session.violation_start_times[
                violation
            ]

            confirmed_violation = violation

            break


    # ======================================================
    # REMOVE VIOLATIONS THAT ARE NO LONGER PRESENT
    # ======================================================

    for violation in list(
        session.active_violations
    ):

        if violation not in current_violations:

            session.active_violations.remove(
                violation
            )

            # The next appearance of this violation is a new
            # incident and can therefore be counted again.
            session.violation_event_counted.discard(
                violation
            )


    # ======================================================
    # REMOVE EXPIRED PERSISTENCE TIMERS
    # ======================================================

    for violation in list(
        session.violation_start_times
    ):

        if violation not in current_violations:

            del session.violation_start_times[
                violation
            ]


    if confirmed_violation is None:

        return {
            "new_violation": False,
            "violation_type": None
        }


    return {
        "new_violation": True,
        "violation_type": confirmed_violation
    }


# ==========================================================
# BROWSER EVENT DUPLICATE CHECK
# ==========================================================

def browser_event_is_duplicate(
    session,
    event_name
):

    now = time.time()


    # ======================================================
    # TAB SWITCH + WINDOW BLUR
    # ======================================================

    if event_name in {
        "TAB_SWITCH",
        "WINDOW_BLUR"
    }:

        last_tab = (
            session
            .last_browser_event_times
            .get(
                "TAB_SWITCH",
                0
            )
        )


        last_blur = (
            session
            .last_browser_event_times
            .get(
                "WINDOW_BLUR",
                0
            )
        )


        latest = max(
            last_tab,
            last_blur
        )


        if (
            now - latest
            <
            BROWSER_EVENT_COOLDOWN_SECONDS
        ):

            return True


    # ======================================================
    # SAME EVENT
    # ======================================================

    last_time = (
        session
        .last_browser_event_times
        .get(
            event_name,
            0
        )
    )


    if (
        now - last_time
        <
        BROWSER_EVENT_COOLDOWN_SECONDS
    ):

        return True


    return False


# ==========================================================
# PROCESS BROWSER VIOLATION
# ==========================================================

def process_browser_violation(
    session,
    event_name,
    metadata=None
):

    event_name = str(
        event_name or ""
    ).upper()

    metadata = (
        metadata
        if isinstance(metadata, dict)
        else {}
    )


    # ======================================================
    # ALREADY TERMINATED
    # ======================================================

    if session.terminated:

        return {
            "action": "TERMINATE_EXAM",
            "violation_count": session.violation_count,
            "new_violation": False,
            "violation_type": event_name,
            "event_source": "BROWSER",
            "metadata": metadata,
            "message": "Exam already terminated."
        }


    # ======================================================
    # ONLY TAB SWITCH + FULLSCREEN EXIT COUNT
    # ======================================================

    if event_name not in BROWSER_VIOLATIONS:

        return {
            "action": "NORMAL",
            "violation_count": session.violation_count,
            "new_violation": False,
            "violation_type": event_name,
            "event_source": "BROWSER",
            "metadata": metadata,
            "message": "Browser event ignored."
        }


    # ======================================================
    # DUPLICATE EVENT CHECK
    # ======================================================

    if browser_event_is_duplicate(
        session,
        event_name
    ):

        return {
            "action": "NORMAL",
            "violation_count": session.violation_count,
            "new_violation": False,
            "violation_type": event_name,
            "event_source": "BROWSER",
            "metadata": metadata,
            "message": "Duplicate browser event ignored."
        }


    now = time.time()

    session.last_browser_event_times[
        event_name
    ] = now


    # ======================================================
    # COUNT BROWSER VIOLATION
    # ======================================================

    session.browser_violation_count += 1

    # Keep compatibility with existing code/frontend.
    session.violation_count = (
        session.browser_violation_count
        +
        session.phone_violation_count
        +
        session.face_violation_count
    )

    count = session.browser_violation_count


    # ======================================================
    # FOURTH BROWSER VIOLATION -> TERMINATE
    # ======================================================

    if count >= 4:

        session.last_action = (
            "TERMINATE_EXAM"
        )

        session.terminated = True

        return {

            "action":
                "TERMINATE_EXAM",

            "violation_count":
                session.violation_count,

            "browser_violation_count":
                count,

            "new_violation":
                True,

            "violation_type":
                event_name,

            "event_source":
                "BROWSER",

            "metadata":
                metadata,

            "message":
                "Fourth tab-switch/fullscreen violation "
                "detected. Exam terminated."

        }


    # ======================================================
    # FIRST / SECOND / THIRD -> WARNING
    # ======================================================

    session.last_action = "WARNING"

    return {

        "action":
            "WARNING",

        "violation_count":
            session.violation_count,

        "browser_violation_count":
            count,

        "new_violation":
            True,

        "violation_type":
            event_name,

        "event_source":
            "BROWSER",

        "metadata":
            metadata,

        "message":
            f"Browser violation {count}/3 detected. "
            "Student has been warned."

    }


# ==========================================================
# ANALYZE CAMERA FRAME
# ==========================================================

def analyze_frame(
    frame,
    session
):

    session.frames_processed += 1


    # ======================================================
    # FACE
    # ======================================================

    try:

        face_result = (
            face_detector.detect(
                frame
            )
        )

    except Exception as e:

        print(
            f"Face detection error: {e}"
        )


        face_result = {

            "status":
                "ERROR",

            "face_count":
                0,

            "detections":
                []

        }


    # ======================================================
    # FACE MESH
    # ======================================================

    try:

        mesh_result = (
            mesh_detector.detect(
                frame
            )
        )

    except Exception as e:

        print(
            f"Face mesh error: {e}"
        )


        mesh_result = {

            "face_count":
                0,

            "faces":
                []

        }


    # ======================================================
    # DEFAULT VALUES
    # ======================================================

    eye_direction = None

    blink_result = None

    head_result = None

    mouth_result = None


    # ======================================================
    # FACE ANALYSIS
    # ======================================================

    if (
        isinstance(
            mesh_result,
            dict
        )
        and
        mesh_result.get(
            "face_count",
            0
        ) > 0
    ):

        faces = mesh_result.get(
            "faces",
            []
        )


        if faces:

            landmarks = (
                faces[0].get(
                    "landmarks"
                )
            )


            if landmarks:

                # ------------------------------------------
                # EYE
                # ------------------------------------------

                try:

                    eye_direction = (
                        eye_tracker
                        .get_eye_direction(
                            landmarks
                        )
                    )

                except Exception as e:

                    print(
                        f"Eye tracking error: {e}"
                    )


                # ------------------------------------------
                # BLINK
                # ------------------------------------------

                try:

                    blink_result = (
                        blink_detector.detect(
                            landmarks
                        )
                    )

                except Exception as e:

                    print(
                        f"Blink detection error: {e}"
                    )


                # ------------------------------------------
                # HEAD
                # ------------------------------------------

                try:

                    head_result = (
                        head_pose_detector.detect(
                            landmarks,
                            frame
                        )
                    )

                except Exception as e:

                    print(
                        f"Head pose error: {e}"
                    )


                # ------------------------------------------
                # MOUTH
                # ------------------------------------------

                try:

                    mouth_result = (
                        mouth_detector.detect(
                            landmarks
                        )
                    )

                except Exception as e:

                    print(
                        f"Mouth detection error: {e}"
                    )


    # ======================================================
    # PHONE
    # ======================================================

    try:

        phone_result = (
            phone_detector.detect(
                frame
            )
        )

    except Exception as e:

        print(
            f"Phone detection error: {e}"
        )


        phone_result = {

            "status":
                "NO_PHONE",

            "phones":
                [],

            "count":
                0,

            "confidence":
                0.0,

            "timestamp":
                time.time()

        }


    # ======================================================
    # CURRENT VIOLATIONS
    # ======================================================

    current_violations = (
        get_current_violations(

            face_result,

            mesh_result,

            eye_direction,

            head_result,

            phone_result

        )
    )


    # ======================================================
    # PROCESS CAMERA VIOLATION
    # ======================================================

    camera_fraud = (
        process_camera_violations(

            session,

            current_violations

        )
    )


    # ======================================================
    # DEFAULT FRAUD
    # ======================================================

    fraud_result = {

        "action":
            "NORMAL",

        "violation_count":
            session.violation_count,

        "phone_violation_count":
            session.phone_violation_count,

        "face_violation_count":
            session.face_violation_count,

        "browser_violation_count":
            session.browser_violation_count,

        "new_violation":
            False,

        "violation_type":
            None,

        "event_source":
            None,

        "pause_duration":
            0,

        "message":
            "No new violation."

    }


    # ======================================================
    # NEW CAMERA VIOLATION
    # ======================================================

    if camera_fraud[
        "new_violation"
    ]:

        violation_type = (
            camera_fraud[
                "violation_type"
            ]
        )


        # ==================================================
        # MOBILE PHONE
        # ==================================================

        if violation_type == PHONE:

            session.phone_violation_count += 1

            count = session.phone_violation_count

            session.violation_count = (
                session.browser_violation_count
                +
                session.phone_violation_count
                +
                session.face_violation_count
            )


            # ----------------------------------------------
            # THIRD PHONE VIOLATION -> TERMINATE
            # ----------------------------------------------

            if count >= 3:

                session.last_action = (
                    "TERMINATE_EXAM"
                )

                session.terminated = True

                fraud_result = {

                    "action":
                        "TERMINATE_EXAM",

                    "violation_count":
                        session.violation_count,

                    "phone_violation_count":
                        count,

                    "face_violation_count":
                        session.face_violation_count,

                    "browser_violation_count":
                        session.browser_violation_count,

                    "new_violation":
                        True,

                    "violation_type":
                        PHONE,

                    "event_source":
                        "AI",

                    "warning":
                        False,

                    "pause":
                        False,

                    "pause_duration":
                        0,

                    "message":
                        "Mobile phone detected three times. "
                        "Exam terminated."

                }


            # ----------------------------------------------
            # FIRST / SECOND PHONE -> WARNING + 10 SEC PAUSE
            # ----------------------------------------------

            else:

                session.last_action = (
                    "PAUSE_EXAM"
                )

                fraud_result = {

                    "action":
                        "PAUSE_EXAM",

                    "violation_count":
                        session.violation_count,

                    "phone_violation_count":
                        count,

                    "face_violation_count":
                        session.face_violation_count,

                    "browser_violation_count":
                        session.browser_violation_count,

                    "new_violation":
                        True,

                    "violation_type":
                        PHONE,

                    "event_source":
                        "AI",

                    "warning":
                        True,

                    "pause":
                        True,

                    "pause_duration":
                        10,

                    "message":
                        f"Mobile phone detected. "
                        f"Warning {count}/2. "
                        f"Exam paused for 10 seconds."

                }


        # ==================================================
        # FACE NOT DETECTED
        # ==================================================

        elif violation_type == NO_FACE:

            session.face_violation_count += 1

            count = session.face_violation_count

            session.violation_count = (
                session.browser_violation_count
                +
                session.phone_violation_count
                +
                session.face_violation_count
            )


            # ----------------------------------------------
            # THIRD FACE VIOLATION -> TERMINATE
            # ----------------------------------------------

            if count >= 3:

                session.last_action = (
                    "TERMINATE_EXAM"
                )

                session.terminated = True

                fraud_result = {

                    "action":
                        "TERMINATE_EXAM",

                    "violation_count":
                        session.violation_count,

                    "phone_violation_count":
                        session.phone_violation_count,

                    "face_violation_count":
                        count,

                    "browser_violation_count":
                        session.browser_violation_count,

                    "new_violation":
                        True,

                    "violation_type":
                        NO_FACE,

                    "event_source":
                        "AI",

                    "warning":
                        False,

                    "pause":
                        False,

                    "pause_duration":
                        0,

                    "message":
                        "Face not detected three times. "
                        "Exam terminated."

                }


            # ----------------------------------------------
            # FIRST / SECOND FACE -> WARNING
            # ----------------------------------------------

            else:

                session.last_action = (
                    "WARNING"
                )

                fraud_result = {

                    "action":
                        "WARNING",

                    "violation_count":
                        session.violation_count,

                    "phone_violation_count":
                        session.phone_violation_count,

                    "face_violation_count":
                        count,

                    "browser_violation_count":
                        session.browser_violation_count,

                    "new_violation":
                        True,

                    "violation_type":
                        NO_FACE,

                    "event_source":
                        "AI",

                    "warning":
                        True,

                    "pause":
                        False,

                    "pause_duration":
                        0,

                    "message":
                        f"Face not detected. "
                        f"Warning {count}/2."

                }


        # ==================================================
        # SAFETY FALLBACK
        # ==================================================

        else:

            fraud_result = {

                "action":
                    "NORMAL",

                "violation_count":
                    session.violation_count,

                "new_violation":
                    False,

                "violation_type":
                    None,

                "event_source":
                    "AI",

                "message":
                    "Unsupported AI violation ignored."

            }


    # ======================================================
    # IMPORTANT
    # ======================================================
    #
    # Do NOT send the raw MediaPipe protobuf object.
    #
    # Convert the entire response first.
    #
    # ======================================================

    result = {

        "type":
            "PROCTORING_RESULT",

        "timestamp":
            time.time(),

        "face":
            face_result,

        "face_mesh":
            mesh_result,

        "eyes": {

            "direction":
                eye_direction

        },

        "blink":
            blink_result,

        "head":
            head_result,

        "mouth":
            mouth_result,

        "phone":
            phone_result,

        "fraud":
            fraud_result

    }


    # ======================================================
    # JSON SAFE RESULT
    # ======================================================

    return make_json_safe(
        result
    )


# ==========================================================
# WEBSOCKET
# ==========================================================

@app.websocket(
    "/ws/proctor"
)
async def proctor_websocket(
    websocket: WebSocket
):

    await websocket.accept()


    print()
    print(
        "=============================================="
    )
    print(
        "Proctoring Client Connected"
    )
    print(
        "=============================================="
    )


    session = ProctoringSession()


    try:

        while True:

            message = (
                await websocket.receive_json()
            )


            if not isinstance(
                message,
                dict
            ):

                continue


            message_type = (
                message.get(
                    "type"
                )
            )


            # ==================================================
            # START EXAM
            # ==================================================

            if (
                message_type ==
                "START_EXAM"
            ):

                print(
                    "Examination started."
                )


                await websocket.send_json({

                    "type":
                        "PROCTORING_STARTED",

                    "message":
                        "AI proctoring started.",

                    "violation_count":
                        0

                })


                continue


            # ==================================================
            # STOP EXAM
            # ==================================================

            if (
                message_type ==
                "STOP_EXAM"
            ):

                print(
                    "Examination stopped."
                )


                await websocket.send_json({

                    "type":
                        "PROCTORING_STOPPED",

                    "message":
                        "AI proctoring stopped.",

                    "violation_count":
                        session.violation_count

                })


                break


            # ==================================================
            # BROWSER VIOLATION
            # ==================================================

            if (
                message_type ==
                "BROWSER_VIOLATION"
            ):

                if session.terminated:

                    continue


                event_name = (
                    message.get(
                        "event"
                    )
                )


                metadata = (
                    message.get(
                        "metadata",
                        {}
                    )
                )


                print()
                print(
                    "BROWSER EVENT:",
                    event_name
                )


                browser_fraud = (
                    process_browser_violation(

                        session,

                        event_name,

                        metadata

                    )
                )


                result = {

                    "type":
                        "PROCTORING_RESULT",

                    "timestamp":
                        time.time(),

                    "browser": {

                        "event":
                            event_name,

                        "metadata":
                            metadata

                    },

                    "fraud":
                        browser_fraud

                }


                # ------------------------------------------
                # JSON SAFE
                # ------------------------------------------

                result = make_json_safe(
                    result
                )


                await websocket.send_json(
                    result
                )


                # ------------------------------------------
                # TERMINATE
                # ------------------------------------------

                if session.terminated:

                    print()
                    print(
                        "=============================================="
                    )

                    print(
                        "EXAM TERMINATED"
                    )

                    print(
                        "Reason:",
                        event_name
                    )

                    print(
                        "Violation count:",
                        session.violation_count
                    )

                    print(
                        "=============================================="
                    )


                    await websocket.send_json({

                        "type":
                            "EXAM_TERMINATED",

                        "reason":
                            browser_fraud.get(
                                "message",
                                "Second violation."
                            ),

                        "violation_type":
                            event_name,

                        "violation_count":
                            session.violation_count

                    })


                    await websocket.close()

                    break


                continue


            # ==================================================
            # VIDEO FRAME
            # ==================================================

            if (
                message_type ==
                "VIDEO_FRAME"
            ):

                if session.terminated:

                    continue


                frame_data = (
                    message.get(
                        "frame"
                    )
                )


                if not frame_data:

                    continue


                frame = decode_frame(
                    frame_data
                )


                if frame is None:

                    continue


                result = analyze_frame(
                    frame,
                    session
                )


                # ------------------------------------------------
                # Result is already JSON safe
                # ------------------------------------------------

                await websocket.send_json(
                    result
                )


                # =================================================
                # TERMINATE
                # =================================================

                if session.terminated:

                    print()
                    print(
                        "=============================================="
                    )

                    print(
                        "EXAM TERMINATED"
                    )

                    print(
                        "Violation count:",
                        session.violation_count
                    )

                    print(
                        "=============================================="
                    )


                    await websocket.send_json({

                        "type":
                            "EXAM_TERMINATED",

                        "reason":
                            result[
                                "fraud"
                            ].get(
                                "message",
                                "Second violation."
                            ),

                        "violation_type":
                            result[
                                "fraud"
                            ].get(
                                "violation_type"
                            ),

                        "violation_count":
                            session.violation_count

                    })


                    await websocket.close()

                    break


                continue


            # ==================================================
            # UNKNOWN MESSAGE
            # ==================================================

            print(
                "Unknown message type:",
                message_type
            )


    except WebSocketDisconnect:

        print(
            "Proctoring client disconnected."
        )


    except Exception as e:

        print()
        print(
            "=============================================="
        )
        print(
            "WebSocket error:",
            e
        )
        print(
            "=============================================="
        )


        try:

            await websocket.send_json({

                "type":
                    "PROCTORING_ERROR",

                "message":
                    str(e)

            })

        except Exception:

            pass


    finally:

        print(
            "Proctoring session closed."
        )


# ==========================================================
# ROOT
# ==========================================================

@app.get("/")
async def root():

    return {

        "service":
            "EduSaaS AI Proctoring",

        "status":
            "running",

        "websocket":
            "/ws/proctor",

        "models": {

            "face":
                "MediaPipe",

            "face_mesh":
                "MediaPipe",

            "eye_tracking":
                "MediaPipe",

            "blink":
                "MediaPipe",

            "head_pose":
                "MediaPipe",

            "mouth":
                "MediaPipe",

            "phone":
                "YOLO11s"

        },

        "fraud_policy": {

            "mobile": {
                "first": "WARNING + PAUSE_EXAM_10_SECONDS",
                "second": "WARNING + PAUSE_EXAM_10_SECONDS",
                "third": "TERMINATE_EXAM"
            },

            "face_not_detected": {
                "first": "WARNING",
                "second": "WARNING",
                "third": "TERMINATE_EXAM"
            },

            "tab_switch": {
                "first": "WARNING",
                "second": "WARNING",
                "third": "WARNING",
                "fourth": "TERMINATE_EXAM"
            },

            "fullscreen_exit": {
                "first": "WARNING",
                "second": "WARNING",
                "third": "WARNING",
                "fourth": "TERMINATE_EXAM"
            },

            "ignored": [
                "HEAD_POSE",
                "EYE_TRACKING",
                "BLINK_DETECTION"
            ],

            "violation_persistence_seconds":
                VIOLATION_PERSISTENCE_SECONDS,

            "mobile_pause_seconds":
                10

        }

    }


# ==========================================================
# HEALTH
# ==========================================================

@app.get("/health")
async def health():

    return {

        "status":
            "healthy",

        "service":
            "ai-proctoring"

    }


# ==========================================================
# RUN
# ==========================================================

if __name__ == "__main__":

    import uvicorn


    print()
    print(
        "=============================================="
    )

    print(
        "Starting EduSaaS AI Proctoring Service"
    )

    print(
        "=============================================="
    )

    print(
        "HTTP:"
    )

    print(
        "http://0.0.0.0:8000"
    )

    print()

    print(
        "WebSocket:"
    )

    print(
        "ws://0.0.0.0:8000/ws/proctor"
    )

    print()

    print(
        "Fraud Policy:"
    )

    print(
        "Mobile: 1st -> WARNING + 10s PAUSE"
    )

    print(
        "Mobile: 2nd -> WARNING + 10s PAUSE"
    )

    print(
        "Mobile: 3rd -> TERMINATE_EXAM"
    )

    print(
        "Face missing: 1st/2nd -> WARNING"
    )

    print(
        "Face missing: 3rd -> TERMINATE_EXAM"
    )

    print(
        "Tab/Fullscreen: 1st/2nd/3rd -> WARNING"
    )

    print(
        "Tab/Fullscreen: 4th -> TERMINATE_EXAM"
    )

    print(
        "Head pose / eye tracking / blink -> IGNORED"
    )

    print(
        "=============================================="
    )


    uvicorn.run(

        app,

        host="0.0.0.0",

        port=8000

    )
'''
