import base64
import os
import time
import traceback
from typing import Any, List, Optional
from uuid import UUID
from fastapi import HTTPException
from contextlib import asynccontextmanager

import cv2
import numpy as np
import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, status
from fastapi import APIRouter, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.wsgi import WSGIMiddleware
from fastapi.staticfiles import StaticFiles
from flask import Flask
from pydantic import BaseModel, Field

# -----------------------------------------------------------------------------
# 1. QUIZ SERVICE INTEGRATION (FLASK WSGI MOUNT)
# -----------------------------------------------------------------------------
from modules.quiz.routes.quiz import quiz_bp
from modules.quiz.routes.skill_gap import skill_gap_bp

flask_app = Flask(__name__)
flask_app.register_blueprint(quiz_bp, url_prefix="/")
flask_app.register_blueprint(skill_gap_bp, url_prefix="/")

# -----------------------------------------------------------------------------
# 2. INDIVIDUAL ML SERVICE ROUTERS IMPORT
# -----------------------------------------------------------------------------

from modules.descriptive.xlnet_model import get_similarity_score

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
# 4. BACKEND ML ENGINES & EXCEPTIONS
# -----------------------------------------------------------------------------
from modules.dropout.predict_dropout import predict_dropout
from modules.hiring.hiring_service import hiring_service
from modules.recommendation.recommend import get_recommendations
from modules.exceptions.custom_exceptions import EduAIException

# -----------------------------------------------------------------------------
# 4. CODE PLAGIARISM
# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------

from modules.plagiarism.routes.plagiarism_routes import router as plagiarism_router
from modules.plagiarism.routes.mini_project_plagiarism import router as mini_project_router

# -----------------------------------------------------------------------------
# 5.PERFORMANCE PREDICTION
# -----------------------------------------------------------------------------
from modules.performance.routers.performance_prediction import router as performance_prediction_router
# -----------------------------------------------------------------------------
# 6. SKILL DEMAND ROUTER INITIALIZATION
# -----------------------------------------------------------------------------

from modules.skill_demand.skill_demand_service import SkillDemandService
skill_demand_service = SkillDemandService()
skill_demand_router = APIRouter(tags=["Skill Demand Forecasting"])
class BatchForecastRequest(BaseModel):
    skills: List[str] = Field(..., example=["python", "docker", "kubernetes"])
    periods: int = Field(6, ge=1, le=24, example=6)

@skill_demand_router.get("/skills")
def get_skills():
    skills = skill_demand_service.get_available_skills()
    if not skills:
        raise HTTPException(status_code=500, detail="Metadata artifact missing or empty.")
    return {"skills": skills}

@skill_demand_router.get("/predict/{skill_name}")
def predict_skill(skill_name: str, periods: int = Query(6, ge=1, le=24)):
    try:
        return skill_demand_service.forecast_skill(skill_name=skill_name, periods=periods)
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@skill_demand_router.post("/predict/batch")
def predict_batch(payload: BatchForecastRequest):
    results = []
    errors = []
    for raw_skill in payload.skills:
        try:
            data = skill_demand_service.forecast_skill(skill_name=raw_skill, periods=payload.periods)
            results.append(data)
        except ValueError as ve:
            errors.append({"skill": raw_skill, "error": str(ve)})
        except Exception as e:
            errors.append({"skill": raw_skill, "error": str(e)})
    return {
        "success": True,
        "total_requested": len(payload.skills),
        "successful": len(results),
        "failed": len(errors),
        "results": results,
        "errors": errors
    }


# -----------------------------------------------------------------------------
# APPLICATION FACTORY & SETUP
# -----------------------------------------------------------------------------
app = FastAPI(
    title="EduSaaS Unified AI & Proctoring Service",
    version="2.0.0",
    description="Unified single-gateway engine for Proctoring, Plagiarism, Quiz, Skill Gap, Dropout, Hiring, and Recommendations."
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_DEMAND_OUTPUT_DIR = os.path.join(BASE_DIR, "modules", "skill_demand", "outputs")

os.makedirs(SKILL_DEMAND_OUTPUT_DIR, exist_ok=True)
app.mount("/outputs", StaticFiles(directory=SKILL_DEMAND_OUTPUT_DIR), name="outputs")

# Mount Modular Routers
app.mount("/api/quiz", WSGIMiddleware(flask_app))
app.mount("/api/skill-gap", WSGIMiddleware(flask_app))
app.include_router(plagiarism_router, prefix="/api/plagiarism", tags=["Plagiarism Detection"])
app.include_router(mini_project_router,prefix="/api/plagiarism/mini-project", tags=["Mini Project Plagiarism"])
app.include_router(skill_demand_router, tags=["Skill Demand Forecasting"])
app.include_router(performance_prediction_router, tags=["Performance Prediction"])

# =============================================================================
# SECTION A: DROPOUT PREDICTION SCHEMAS & ENDPOINTS
# =============================================================================

class DropoutInput(BaseModel):
    student_id: UUID
    sessions_last_30_days: int = Field(..., ge=0)
    avg_session_minutes: float = Field(..., ge=0)
    videos_watched: int = Field(..., ge=0)
    assignments_attempted: int = Field(..., ge=0)
    discussion_interactions: int = Field(..., ge=0)
    logins_last_30_days: int = Field(..., ge=0)
    days_since_last_login: int = Field(..., ge=0)
    completion_percentage: float = Field(..., ge=0, le=100)
    quiz_average: float = Field(..., ge=0, le=100)
    assignment_completion_rate: float = Field(..., ge=0, le=100)


@app.get("/api/dropout/", tags=["Dropout Prediction"])
def dropout_home():
    return {
        "success": True,
        "message": "Dropout Prediction API is Running",
        "data": {
            "service": "dropout"
        }
    }


@app.get("/api/dropout/health", tags=["Dropout Prediction"])
def dropout_health():
    return {
        "success": True,
        "message": "Dropout Prediction Service Healthy",
        "data": {
            "status": "healthy",
            "models_loaded": True
        }
    }


@app.post("/api/dropout/predict", tags=["Dropout Prediction"])
def dropout_prediction(data: DropoutInput):
    try:
        prediction_input = data.model_dump(
            exclude={"student_id"}
        )

        result = predict_dropout(prediction_input)

        return {
            "success": True,
            "message": "Dropout prediction completed successfully.",
            "data": {
                "student_id": str(data.student_id),
                **result
            }
        }
    except Exception as e:
        raise EduAIException(str(e))
    
# =============================================================================
# SECTION B: PREDICTIVE HIRING SCHEMAS & ENDPOINTS
# =============================================================================

class HiringRequest(BaseModel):
    experience_years: float = Field(0, ge=0)
    required_experience_years: float = Field(0, ge=0)
    skill_match_score: float = Field(..., ge=0, le=1)
    experience_match_score: float = Field(..., ge=0, le=1)
    domain_match: int = Field(..., ge=0, le=1)
    profile_score: float = Field(..., ge=0, le=100)


@app.get("/api/hiring/", tags=["Predictive Hiring"])
def hiring_home():
    return {
        "success": True,
        "message": "Predictive Hiring API is Running"
    }


@app.get("/api/hiring/health", tags=["Predictive Hiring"])
def hiring_health():
    return {
        "success": True,
        "message": "Predictive Hiring Service Healthy",
        "model": "Random Forest",
        "version": "1.0.0"
    }


@app.post("/api/hiring/predict", tags=["Predictive Hiring"])
def predict_hiring_endpoint(request: HiringRequest):
    try:
        result = hiring_service.predict(
            request.model_dump()
        )

        return {
            "success": True,
            "message": "Hiring prediction completed successfully.",
            "data": result
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# =============================================================================
# SECTION C: COURSE RECOMMENDATION SCHEMAS & ENDPOINTS
# =============================================================================

class RecommendationRequest(BaseModel):
    user_id: UUID
    course_name: str
    courses: List[dict[str, Any]] = Field(default_factory=list)
    ratings: List[dict[str, Any]] = Field(default_factory=list)
    user: Optional[dict[str, Any]] = None
    prerequisites: List[dict[str, Any]] = Field(default_factory=list)
    completed_courses: List[dict[str, Any]] = Field(default_factory=list)


@app.get("/api/recommendation/", tags=["Recommendation System"])
def recommendation_home():
    return {
        "success": True,
        "message": "Recommendation API Running",
        "data": None
    }


@app.get("/api/recommendation/health", tags=["Recommendation System"])
def recommendation_health():
    return {
        "success": True,
        "message": "Recommendation Service Healthy",
        "data": {
            "status": "healthy"
        }
    }


@app.post("/api/recommendation/recommend", tags=["Recommendation System"])
def recommendation_api(request: RecommendationRequest):
    try:
        result = get_recommendations(
            user_id=request.user_id,
            course_name=request.course_name,
            courses=request.courses,
            user=request.user,
            prerequisites=request.prerequisites,
            completed_courses=request.completed_courses
        )

        return {
            "success": True,
            "message": "Recommendations generated successfully.",
            "data": result
        }
    except Exception as e:
        raise EduAIException(str(e))
    
    
    
# =============================================================================
# SECTION D: DESCRIPTIVE ANSWER EVALUATION (XLNET)
# =============================================================================

class EvaluationRequest(BaseModel):
    question_text: str = Field(..., description="The question text")
    student_answer_text: str = Field(..., description="The student answer")
    reference_answer_text: str = Field(..., description="The expected benchmark answer")


@app.get("/api/evaluation/", tags=["Descriptive Answer Evaluation"])
def evaluation_home():
    return {
        "success": True,
        "service": "Descriptive Answer Evaluation",
        "status": "running"
    }


@app.post("/api/evaluation/evaluate", tags=["Descriptive Answer Evaluation"])
def evaluate_descriptive_answer(payload: EvaluationRequest):
    try:
        q_text = payload.question_text.strip()
        ans_text = payload.student_answer_text.strip()
        ref_text = payload.reference_answer_text.strip()

        if not q_text or not ans_text or not ref_text:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="question_text, student_answer_text, and reference_answer_text must not be empty."
            )

        similarity_score = get_similarity_score(q_text, ans_text, ref_text)

        # Apply score adjustments
        if similarity_score >= 75:
            similarity_score += 20
        elif 70 <= similarity_score < 75:
            similarity_score += 18
        elif 60 <= similarity_score < 65:
            similarity_score += 16
        else:
            similarity_score -= 10

        return {
            "success": True,
            "score": similarity_score
        }
    except HTTPException:
        raise
    except Exception as e:
        print("\n========================================")
        print("XLNet Evaluation Error")
        print("========================================")
        print(str(e))
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
        
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
            "evaluation_api": "/api/evaluation/evaluate",
            "quiz_api": "/api/quiz/*",
            "skill_gap_api": "/api/skill-gap/*",
            "dropout_api": "/api/dropout/predict",
            "hiring_api": "/api/hiring/predict",
            "skill_demand_skills": "/skills",
            "skill_demand_predict": "/predict/{skill_name}",
            "skill_demand_batch": "/predict/batch",
            "performance_prediction_api": "/predict/performance",
            "recommendation_api": "/api/recommendation/recommend"
        },
        "models": {
            "face_presence": "MediaPipe",
            "face_mesh": "MediaPipe",
            "eye_tracking": "MediaPipe",
            "blink": "MediaPipe",
            "mouth": "MediaPipe",
            "phone": "YOLO11s",
            "dropout": "RandomForest",
            "hiring": "RandomForest",
            "performance_prediction": "XGBoost (Fallback: RandomForest)",
            "recommendation": "Hybrid SVD + ContentSimilarity",
            "head_pose": "REMOVED"
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
        "components": ["proctoring", "plagiarism", "quiz", "skill-gap","dropout",
            "hiring",
            "recommendation","evaluation","performance_prediction","skill_demand"]
    }

# -----------------------------------------------------------------------------
# APPLICATION ENTRYPOINT
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    print("\n==============================================")
    print("Starting EduSaaS Unified AI & Proctoring Service")
    print("==============================================")
    print(f"HTTP Root          : http://0.0.0.0:{port}/")
    print(f"Proctoring WS      : ws://0.0.0.0:{port}/ws/proctor")
    print(f"Plagiarism Engine  : http://0.0.0.0:{port}/api/plagiarism/check")
    print(f"Evaluation Engine  : http://0.0.0.0:{port}/api/evaluation/evaluate")
    print(f"Quiz API           : http://0.0.0.0:{port}/api/quiz/")
    print(f"Skill Gap API      : http://0.0.0.0:{port}/api/skill-gap/")
    print(f"Dropout API        : http://0.0.0.0:{port}/api/dropout/")
    print(f"Hiring API         : http://0.0.0.0:{port}/api/hiring/")
    print(f"Recommendation API : http://0.0.0.0:{port}/api/recommendation/")
    print(f"Skill Demand Engine: http://0.0.0.0:{port}/skills")
    print(f"Performance Engine : http://0.0.0.0:{port}/predict/performance")
    print("==============================================\n")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
    )