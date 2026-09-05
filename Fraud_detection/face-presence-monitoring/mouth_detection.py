# import cv2
# import math


# class MouthDetector:

#     def __init__(self):

#         # Mouth landmarks
#         self.LEFT = 78
#         self.RIGHT = 308

#         self.UPPER = 13
#         self.LOWER = 14

#         # Threshold (adjust if needed)
#         self.threshold = 0.12

#     def distance(self, p1, p2):

#         return math.sqrt(
#             (p1[0] - p2[0]) ** 2 +
#             (p1[1] - p2[1]) ** 2
#         )

#     def detect(self, landmarks):

#         horizontal = self.distance(
#             landmarks[self.LEFT],
#             landmarks[self.RIGHT]
#         )

#         vertical = self.distance(
#             landmarks[self.UPPER],
#             landmarks[self.LOWER]
#         )

#         mar = vertical / (horizontal + 1e-6)

#         if mar > self.threshold:

#             status = "MOUTH_OPEN"
#             color = (0, 0, 255)

#         else:

#             status = "MOUTH_CLOSED"
#             color = (0, 255, 0)

#         return {
#             "status": status,
#             "mar": round(mar, 3),
#             "color": color
#         }

#     def draw(self, frame, result):

#         cv2.putText(
#             frame,
#             f"Mouth : {result['status']}",
#             (20, 300),
#             cv2.FONT_HERSHEY_SIMPLEX,
#             0.8,
#             result["color"],
#             2
#         )

#         cv2.putText(
#             frame,
#             f"MAR : {result['mar']}",
#             (20, 330),
#             cv2.FONT_HERSHEY_SIMPLEX,
#             0.7,
#             result["color"],
#             2
#         )

#         return frame


import cv2
import math


class MouthDetector:

    def __init__(self):
        # MediaPipe inner lip landmarks
        self.LEFT = 78
        self.RIGHT = 308
        self.UPPER = 13
        self.LOWER = 14

        # Adjusted threshold (0.22 - 0.25 is safer for normal resting mouths)
        self.threshold = 0.22

        # To track consecutive frames and avoid instant penalties
        self.consecutive_open_frames = 0
        # Alert only if open for e.g., 30 consecutive frames (~1 second at 30fps)
        self.frame_alert_limit = 30

    def distance(self, p1, p2):
        return math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)

    def detect(self, landmarks):
        horizontal = self.distance(landmarks[self.LEFT], landmarks[self.RIGHT])
        vertical = self.distance(landmarks[self.UPPER], landmarks[self.LOWER])

        mar = vertical / (horizontal + 1e-6)

        if mar > self.threshold:
            self.consecutive_open_frames += 1
        else:
            self.consecutive_open_frames = 0  # Reset if they close their mouth

        # Only trigger violation if mouth is open continuously
        if self.consecutive_open_frames >= self.frame_alert_limit:
            status = "VIOLATION_SPEAKING"
            color = (0, 0, 255)
        elif self.consecutive_open_frames > 0:
            status = "MOUTH_OPENING"
            color = (0, 165, 255)  # Orange warning
        else:
            status = "MOUTH_CLOSED"
            color = (0, 255, 0)

        return {
            "status": status,
            "mar": round(mar, 3),
            "color": color,
            "open_frames": self.consecutive_open_frames,
        }

    def draw(self, frame, result):
        cv2.putText(
            frame,
            f"Status : {result['status']}",
            (20, 300),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            result["color"],
            2,
        )
        cv2.putText(
            frame,
            f"MAR : {result['mar']}",
            (20, 330),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            result["color"],
            2,
        )
        return frame
