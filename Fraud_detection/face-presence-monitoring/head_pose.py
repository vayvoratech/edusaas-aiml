import cv2
import numpy as np


class HeadPoseDetector:

    def __init__(
        self,
        yaw_threshold=12.0,
        pitch_threshold=10.0
    ):

        self.yaw_threshold = yaw_threshold
        self.pitch_threshold = pitch_threshold

    # =========================================================
    # CONVERT ONE LANDMARK TO X,Y
    # =========================================================

    def _get_xy(self, landmark):

        # MediaPipe converted dictionary
        if isinstance(landmark, dict):

            return (
                float(landmark["x"]),
                float(landmark["y"])
            )

        # Tuple/list: (x, y) or (x, y, z)
        if isinstance(
            landmark,
            (list, tuple, np.ndarray)
        ):

            if len(landmark) >= 2:

                return (
                    float(landmark[0]),
                    float(landmark[1])
                )

        raise ValueError(
            f"Invalid landmark: {landmark}"
        )

    # =========================================================
    # NORMALIZE LANDMARK INPUT
    # =========================================================

    def _normalize_landmarks(self, landmarks):

        print(
            "HEAD POSE INPUT TYPE:",
            type(landmarks)
        )

        # -----------------------------------------------------
        # Case 1:
        #
        # {
        #     "landmarks": [...]
        # }
        # -----------------------------------------------------

        if isinstance(landmarks, dict):

            landmarks = landmarks.get(
                "landmarks",
                []
            )

        # -----------------------------------------------------
        # Empty
        # -----------------------------------------------------

        if not landmarks:

            return []

        # -----------------------------------------------------
        # Case 2:
        #
        # [
        #     [
        #         landmark,
        #         landmark,
        #         ...
        #     ]
        # ]
        #
        # Multiple faces
        # -----------------------------------------------------

        if isinstance(
            landmarks[0],
            (list, tuple)
        ):

            first = landmarks[0]

            # Determine whether this is:
            #
            # [x, y, z]
            #
            # or:
            #
            # [[x,y,z], [x,y,z], ...]

            if (
                len(first) >= 2
                and isinstance(
                    first[0],
                    (int, float, np.number)
                )
            ):

                # Already one landmark
                return list(landmarks)

            # Nested face list
            return list(first)

        # -----------------------------------------------------
        # [
        #     {"x": ..., "y": ..., "z": ...},
        #     ...
        # ]
        # -----------------------------------------------------

        return list(landmarks)

    # =========================================================
    # DETECT HEAD POSE
    # =========================================================

    def detect(
        self,
        landmarks,
        frame
    ):

        if frame is None:

            return self._unknown_result()

        h, w = frame.shape[:2]

        # =====================================================
        # NORMALIZE
        # =====================================================

        landmarks = self._normalize_landmarks(
            landmarks
        )

        print(
            "HEAD POSE FINAL LANDMARK COUNT:",
            len(landmarks)
        )

        # =====================================================
        # REQUIRED LANDMARKS
        # =====================================================

        required_indices = [
            1,
            152,
            33,
            263,
            61,
            291
        ]

        # -----------------------------------------------------
        # IMPORTANT:
        # We need landmark index 291.
        # Therefore at least 292 landmarks.
        # -----------------------------------------------------

        if len(landmarks) <= 291:

            print(
                "HEAD POSE ERROR:",
                "Expected at least 292 landmarks,",
                "received:",
                len(landmarks)
            )

            if landmarks:

                print(
                    "FIRST LANDMARK:",
                    landmarks[0]
                )

            return self._unknown_result()

        try:

            # =================================================
            # GET REQUIRED LANDMARKS
            # =================================================

            nose_x, nose_y = self._get_xy(
                landmarks[1]
            )

            chin_x, chin_y = self._get_xy(
                landmarks[152]
            )

            left_eye_x, left_eye_y = self._get_xy(
                landmarks[33]
            )

            right_eye_x, right_eye_y = self._get_xy(
                landmarks[263]
            )

            left_mouth_x, left_mouth_y = self._get_xy(
                landmarks[61]
            )

            right_mouth_x, right_mouth_y = self._get_xy(
                landmarks[291]
            )

            # =================================================
            # NORMALIZED → PIXELS
            # =================================================

            image_points = np.array(
                [
                    [
                        nose_x * w,
                        nose_y * h
                    ],
                    [
                        chin_x * w,
                        chin_y * h
                    ],
                    [
                        left_eye_x * w,
                        left_eye_y * h
                    ],
                    [
                        right_eye_x * w,
                        right_eye_y * h
                    ],
                    [
                        left_mouth_x * w,
                        left_mouth_y * h
                    ],
                    [
                        right_mouth_x * w,
                        right_mouth_y * h
                    ]
                ],
                dtype=np.float64
            )

            # =================================================
            # 3D FACE MODEL
            # =================================================

            model_points = np.array(
                [
                    (0.0, 0.0, 0.0),
                    (0.0, -63.6, -12.5),
                    (-43.3, 32.7, -26.0),
                    (43.3, 32.7, -26.0),
                    (-28.9, -28.9, -24.1),
                    (28.9, -28.9, -24.1)
                ],
                dtype=np.float64
            )

            # =================================================
            # CAMERA MATRIX
            # =================================================

            focal_length = float(w)

            camera_matrix = np.array(
                [
                    [
                        focal_length,
                        0.0,
                        w / 2.0
                    ],
                    [
                        0.0,
                        focal_length,
                        h / 2.0
                    ],
                    [
                        0.0,
                        0.0,
                        1.0
                    ]
                ],
                dtype=np.float64
            )

            dist_coeffs = np.zeros(
                (4, 1),
                dtype=np.float64
            )

            # =================================================
            # SOLVE PNP
            # =================================================

            success, rotation_vector, translation_vector = (
                cv2.solvePnP(
                    model_points,
                    image_points,
                    camera_matrix,
                    dist_coeffs,
                    flags=cv2.SOLVEPNP_ITERATIVE
                )
            )

            if not success:

                return self._unknown_result()

            # =================================================
            # ROTATION
            # =================================================

            rotation_matrix, _ = cv2.Rodrigues(
                rotation_vector
            )

            angles, _, _, _, _, _ = (
                cv2.RQDecomp3x3(
                    rotation_matrix
                )
            )

            pitch = float(
                angles[0]
            )

            yaw = float(
                angles[1]
            )

            roll = float(
                angles[2]
            )

            # =================================================
            # CLASSIFY
            # =================================================

            if yaw < -self.yaw_threshold:

                status = "LOOKING_LEFT"

                color = (
                    255,
                    0,
                    0
                )

            elif yaw > self.yaw_threshold:

                status = "LOOKING_RIGHT"

                color = (
                    0,
                    0,
                    255
                )

            elif pitch < -self.pitch_threshold:

                status = "LOOKING_DOWN"

                color = (
                    0,
                    255,
                    255
                )

            elif pitch > self.pitch_threshold:

                status = "LOOKING_UP"

                color = (
                    255,
                    255,
                    0
                )

            else:

                status = "LOOKING_CENTER"

                color = (
                    0,
                    255,
                    0
                )

            return {

                "status": status,

                "angles": (
                    round(pitch, 2),
                    round(yaw, 2),
                    round(roll, 2)
                ),

                "color": color

            }

        except Exception as error:

            print(
                "HEAD POSE EXCEPTION:",
                error
            )

            return self._unknown_result()

    # =========================================================
    # UNKNOWN
    # =========================================================

    def _unknown_result(self):

        return {

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

    # =========================================================
    # DRAW
    # =========================================================

    def draw(
        self,
        frame,
        result
    ):

        if frame is None:

            return frame

        pitch, yaw, roll = result.get(
            "angles",
            (0.0, 0.0, 0.0)
        )

        status = result.get(
            "status",
            "UNKNOWN"
        )

        color = result.get(
            "color",
            (255, 255, 255)
        )

        cv2.putText(
            frame,
            f"Head : {status}",
            (20, 230),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            color,
            2
        )

        cv2.putText(
            frame,
            f"P:{pitch:.1f}  Y:{yaw:.1f}  R:{roll:.1f}",
            (20, 260),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            color,
            2
        )

        return frame