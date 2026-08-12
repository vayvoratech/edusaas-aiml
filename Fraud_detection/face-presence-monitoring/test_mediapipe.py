import cv2
import time

from face_presence import FacePresenceDetector
from face_mesh import FaceMeshDetector
from eye_tracking import EyeTracker
from blink_detection import BlinkDetector
from head_pose import HeadPoseDetector
from mouth_detection import MouthDetector


face_detector = FacePresenceDetector()
mesh_detector = FaceMeshDetector()
eye_tracker = EyeTracker()
blink_detector = BlinkDetector()
head_pose_detector = HeadPoseDetector()
mouth_detector = MouthDetector()

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Unable to access camera")
    exit()

frame_count = 0
start_time = time.time()

while True:

    success, frame = cap.read()

    if not success:
        break

    # Face detection
    face_result = face_detector.detect(frame)

    # Face mesh
    mesh_result = mesh_detector.detect(frame)

    if mesh_result["face_count"] > 0:

        landmarks = mesh_result["faces"][0]["landmarks"]

        # Eye tracking
        eye_tracker.get_eye_direction(landmarks)

        # Blink
        blink_detector.detect(landmarks)

        # Head pose
        head_pose_detector.detect(landmarks, frame)

        # Mouth
        mouth_detector.detect(landmarks)

    frame_count += 1

    elapsed = time.time() - start_time

    fps = frame_count / elapsed

    cv2.putText(
        frame,
        f"MediaPipe FPS: {fps:.2f}",
        (20, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.9,
        (0, 255, 0),
        2
    )

    cv2.imshow("MediaPipe FPS Test", frame)

    if cv2.waitKey(1) & 0xFF == 27:
        break

elapsed = time.time() - start_time

print()
print("================================")
print("MediaPipe Performance")
print("================================")
print(f"Frames       : {frame_count}")
print(f"Time         : {elapsed:.2f} sec")
print(f"Average FPS  : {frame_count / elapsed:.2f}")
print("================================")

cap.release()
cv2.destroyAllWindows()