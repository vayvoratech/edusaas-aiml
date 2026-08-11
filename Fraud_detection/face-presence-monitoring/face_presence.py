from pathlib import Path

import cv2
import mediapipe as mp


class FacePresenceDetector:
    """
    MediaPipe Face Detector using the modern Tasks API.

    Returns the same structure expected by the existing FraudEngine:
    {
        "status": "FACE_MISSING" | "FACE_PRESENT" | "MULTIPLE_FACES",
        "face_count": int,
        "color": tuple,
        "detections": [
            {
                "bbox": (x, y, width, height),
                "confidence": float
            }
        ]
    }
    """

    def __init__(
        self,
        model_path=None,
        min_detection_confidence=0.6
    ):
        # ---------------------------------------------------------
        # Locate model relative to this file
        # ---------------------------------------------------------
        if model_path is None:
            project_root = Path(__file__).resolve().parent
            model_path = (
                project_root
                / "models"
                / "blaze_face_short_range.tflite"
            )

        self.model_path = Path(model_path)

        print(f"Loading MediaPipe face detector:")
        print(f"Model: {self.model_path}")

        if not self.model_path.exists():
            raise FileNotFoundError(
                "\nMediaPipe face detector model not found:\n"
                f"{self.model_path}\n\n"
                "Expected project structure:\n"
                "face-presence-monitoring/\n"
                "├── main.py\n"
                "├── face_presence.py\n"
                "└── models/\n"
                "    └── blaze_face_short_range.tflite\n"
            )

        # ---------------------------------------------------------
        # MediaPipe Tasks API
        # ---------------------------------------------------------
        BaseOptions = mp.tasks.BaseOptions
        FaceDetector = mp.tasks.vision.FaceDetector
        FaceDetectorOptions = mp.tasks.vision.FaceDetectorOptions
        RunningMode = mp.tasks.vision.RunningMode

        # ---------------------------------------------------------
        # Detector configuration
        # ---------------------------------------------------------
        options = FaceDetectorOptions(
            base_options=BaseOptions(
                model_asset_path=str(self.model_path)
            ),
            running_mode=RunningMode.IMAGE,
            min_detection_confidence=min_detection_confidence
        )

        # ---------------------------------------------------------
        # Create detector
        # ---------------------------------------------------------
        self.detector = FaceDetector.create_from_options(options)

        print("MediaPipe Face Detector loaded successfully.")

    # =============================================================
    # FACE DETECTION
    # =============================================================

    def detect(self, frame):

        if frame is None:
            return self._face_missing_result()

        # ---------------------------------------------------------
        # OpenCV BGR -> RGB
        # ---------------------------------------------------------
        rgb_frame = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2RGB
        )

        # ---------------------------------------------------------
        # Convert OpenCV image to MediaPipe Image
        # ---------------------------------------------------------
        mp_image = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=rgb_frame
        )

        # ---------------------------------------------------------
        # Run MediaPipe detector
        # ---------------------------------------------------------
        results = self.detector.detect(mp_image)

        detections = []

        if results.detections:

            frame_height, frame_width = frame.shape[:2]

            for detection in results.detections:

                # -------------------------------------------------
                # Bounding box
                # -------------------------------------------------
                bbox = detection.bounding_box

                x = int(bbox.origin_x)
                y = int(bbox.origin_y)

                width = int(bbox.width)
                height = int(bbox.height)

                # -------------------------------------------------
                # Keep bounding box inside image
                # -------------------------------------------------
                x = max(0, x)
                y = max(0, y)

                width = min(
                    width,
                    frame_width - x
                )

                height = min(
                    height,
                    frame_height - y
                )

                # -------------------------------------------------
                # Confidence
                # -------------------------------------------------
                confidence = 0.0

                if detection.categories:

                    confidence = float(
                        detection.categories[0].score
                    )

                detections.append({
                    "bbox": (
                        x,
                        y,
                        width,
                        height
                    ),
                    "confidence": confidence
                })

        # ---------------------------------------------------------
        # Number of detected faces
        # ---------------------------------------------------------
        face_count = len(detections)

        # ---------------------------------------------------------
        # Determine status
        # ---------------------------------------------------------

        if face_count == 0:

            return {
                "status": "FACE_MISSING",
                "face_count": 0,
                "color": (0, 0, 255),
                "detections": []
            }

        elif face_count == 1:

            return {
                "status": "FACE_PRESENT",
                "face_count": 1,
                "color": (0, 255, 0),
                "detections": detections
            }

        else:

            return {
                "status": "MULTIPLE_FACES",
                "face_count": face_count,
                "color": (0, 165, 255),
                "detections": detections
            }

    # =============================================================
    # FACE MISSING RESULT
    # =============================================================

    def _face_missing_result(self):

        return {
            "status": "FACE_MISSING",
            "face_count": 0,
            "color": (0, 0, 255),
            "detections": []
        }

    # =============================================================
    # RELEASE RESOURCES
    # =============================================================

    def close(self):

        if self.detector is not None:

            self.detector.close()

            self.detector = None

            print("MediaPipe Face Detector closed.")



'''import cv2
import mediapipe as mp


class FacePresenceDetector:

    def __init__(self):

        self.mp_face_detection = mp.solutions.face_detection

        self.detector = self.mp_face_detection.FaceDetection(
            model_selection=0,
            min_detection_confidence=0.6
        )

    def detect(self, frame):

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        results = self.detector.process(rgb)

        face_count = 0
        detections = []

        if results.detections:

            face_count = len(results.detections)

            h, w, _ = frame.shape

            for detection in results.detections:

                bbox = detection.location_data.relative_bounding_box

                x = int(bbox.xmin * w)
                y = int(bbox.ymin * h)
                bw = int(bbox.width * w)
                bh = int(bbox.height * h)

                confidence = float(detection.score[0])

                detections.append({
                    "bbox": (x, y, bw, bh),
                    "confidence": confidence
                })

        if face_count == 0:
            status = "FACE_MISSING"
            color = (0, 0, 255)

        elif face_count == 1:
            status = "FACE_PRESENT"
            color = (0, 255, 0)

        else:
            status = "MULTIPLE_FACES"
            color = (0, 165, 255)

        return {
            "status": status,
            "face_count": face_count,
            "color": color,
            "detections": detections
        }

'''











'''import cv2
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
cv2.destroyAllWindows()'''