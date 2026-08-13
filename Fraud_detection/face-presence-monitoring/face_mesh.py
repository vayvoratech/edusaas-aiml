from pathlib import Path

import cv2
import mediapipe as mp


class FaceMeshDetector:

    def __init__(
        self,
        model_path=None,
        min_face_detection_confidence=0.5,
        min_face_presence_confidence=0.5,
        min_tracking_confidence=0.5,
    ):

        # =====================================================
        # LOCATE MODEL
        # =====================================================

        if model_path is None:

            project_root = Path(
                __file__
            ).resolve().parent

            model_path = (
                project_root
                / "models"
                / "face_landmarker.task"
            )

        self.model_path = Path(
            model_path
        )

        print(
            "Loading MediaPipe Face Landmarker:"
        )

        print(
            f"Model: {self.model_path}"
        )

        if not self.model_path.exists():

            raise FileNotFoundError(
                "\nMediaPipe face landmarker model not found:\n"
                f"{self.model_path}\n\n"
                "Expected structure:\n"
                "face-presence-monitoring/\n"
                "├── main.py\n"
                "├── face_mesh.py\n"
                "└── models/\n"
                "    └── face_landmarker.task\n"
            )

        # =====================================================
        # MEDIAPIPE TASKS API
        # =====================================================

        BaseOptions = mp.tasks.BaseOptions

        FaceLandmarker = (
            mp.tasks.vision.FaceLandmarker
        )

        FaceLandmarkerOptions = (
            mp.tasks.vision.FaceLandmarkerOptions
        )

        RunningMode = (
            mp.tasks.vision.RunningMode
        )

        # =====================================================
        # CONFIGURATION
        # =====================================================

        options = FaceLandmarkerOptions(

            base_options=BaseOptions(
                model_asset_path=str(
                    self.model_path
                )
            ),

            running_mode=RunningMode.IMAGE,

            # Maximum number of faces
            num_faces=5,

            min_face_detection_confidence=(
                min_face_detection_confidence
            ),

            min_face_presence_confidence=(
                min_face_presence_confidence
            ),

            min_tracking_confidence=(
                min_tracking_confidence
            ),

            output_face_blendshapes=True,

            output_facial_transformation_matrixes=True,
        )

        # =====================================================
        # CREATE DETECTOR
        # =====================================================

        self.detector = (
            FaceLandmarker.create_from_options(
                options
            )
        )

        print(
            "MediaPipe Face Landmarker "
            "loaded successfully."
        )

    # =========================================================
    # DETECT FACE LANDMARKS
    # =========================================================

    def detect(self, frame):

        # -----------------------------------------------------
        # Invalid frame
        # -----------------------------------------------------

        if frame is None:

            return {
                "face_count": 0,
                "landmarks": [],
                "blendshapes": [],
                "transformation_matrices": [],
            }

        # -----------------------------------------------------
        # BGR -> RGB
        # -----------------------------------------------------

        rgb_frame = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2RGB
        )

        # -----------------------------------------------------
        # Convert to MediaPipe Image
        # -----------------------------------------------------

        mp_image = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=rgb_frame
        )

        # -----------------------------------------------------
        # Run Face Landmarker
        # -----------------------------------------------------

        results = self.detector.detect(
            mp_image
        )

        # -----------------------------------------------------
        # Face count
        # -----------------------------------------------------

        face_count = len(
            results.face_landmarks
        )

        # -----------------------------------------------------
        # Store landmarks
        # -----------------------------------------------------

        all_landmarks = []

        for face_landmarks in (
            results.face_landmarks
        ):

            face_points = []

            for landmark in face_landmarks:

                face_points.append({

                    "x": float(
                        landmark.x
                    ),

                    "y": float(
                        landmark.y
                    ),

                    "z": float(
                        landmark.z
                    )

                })

            all_landmarks.append(
                face_points
            )

        # =====================================================
        # DEBUG LANDMARK COUNT
        # =====================================================

        if face_count > 0:

            print(
                f"Face detected: {face_count}"
            )

            for index, face in enumerate(
                all_landmarks
            ):

                print(
                    f"Face {index + 1} "
                    f"landmarks: {len(face)}"
                )

        # =====================================================
        # BLENDSHAPES
        # =====================================================

        all_blendshapes = []

        if results.face_blendshapes:

            for face_blendshapes in (
                results.face_blendshapes
            ):

                blendshape_data = []

                for blendshape in (
                    face_blendshapes
                ):

                    blendshape_data.append({

                        "name":
                            blendshape.category_name,

                        "score":
                            float(
                                blendshape.score
                            )

                    })

                all_blendshapes.append(
                    blendshape_data
                )

        # =====================================================
        # TRANSFORMATION MATRICES
        # =====================================================

        transformation_matrices = []

        if (
            results.facial_transformation_matrixes
        ):

            for matrix in (
                results.facial_transformation_matrixes
            ):

                transformation_matrices.append(
                    matrix.tolist()
                )

        # =====================================================
        # RETURN
        # =====================================================

        return {

            "face_count":
                face_count,

            "landmarks":
                all_landmarks,

            "blendshapes":
                all_blendshapes,

            "transformation_matrices":
                transformation_matrices

        }

    # =========================================================
    # DRAW LANDMARKS
    # =========================================================

    def draw_landmarks(
        self,
        frame,
        detection_result
    ):

        if frame is None:

            return frame

        face_landmarks_list = (
            detection_result.get(
                "landmarks",
                []
            )
        )

        height, width = (
            frame.shape[:2]
        )

        for face_landmarks in (
            face_landmarks_list
        ):

            for landmark in (
                face_landmarks
            ):

                x = int(
                    landmark["x"] * width
                )

                y = int(
                    landmark["y"] * height
                )

                # -------------------------------------------------
                # Keep point inside image
                # -------------------------------------------------

                if (
                    0 <= x < width
                    and
                    0 <= y < height
                ):

                    cv2.circle(
                        frame,
                        (x, y),
                        1,
                        (0, 255, 0),
                        -1
                    )

        return frame

    # =========================================================
    # RELEASE
    # =========================================================

    def close(self):

        if self.detector is not None:

            self.detector.close()

            self.detector = None

            print(
                "MediaPipe Face Landmarker closed."
            )





