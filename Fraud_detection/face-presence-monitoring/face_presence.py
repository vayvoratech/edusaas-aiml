from pathlib import Path

import cv2
import mediapipe as mp


class FacePresenceDetector:

    def __init__(
        self,
        model_path=None,
        min_detection_confidence=0.6
    ):

        if model_path is None:

            project_root = (
                Path(__file__).resolve().parent
            )

            model_path = (
                project_root
                / "models"
                / "blaze_face_short_range.tflite"
            )

        self.model_path = Path(
            model_path
        )

        print(
            "Loading MediaPipe face detector:"
        )

        print(
            f"Model: {self.model_path}"
        )

        if not self.model_path.exists():

            raise FileNotFoundError(

                "\nMediaPipe face detector "
                "model not found:\n"

                f"{self.model_path}\n\n"

                "Expected:\n"

                "models/"
                "blaze_face_short_range.tflite"
            )

        BaseOptions = (
            mp.tasks.BaseOptions
        )

        FaceDetector = (
            mp.tasks.vision.FaceDetector
        )

        FaceDetectorOptions = (
            mp.tasks.vision.FaceDetectorOptions
        )

        RunningMode = (
            mp.tasks.vision.RunningMode
        )

        options = FaceDetectorOptions(

            base_options=BaseOptions(

                model_asset_path=
                    str(self.model_path)
            ),

            running_mode=
                RunningMode.IMAGE,

            min_detection_confidence=
                min_detection_confidence
        )

        self.detector = (
            FaceDetector.create_from_options(
                options
            )
        )

        print(
            "MediaPipe Face Detector "
            "loaded successfully."
        )

    
    # DETECT
    # ==================================================

    def detect(
        self,
        frame
    ):

        if frame is None:

            return self._face_missing_result()

        rgb_frame = cv2.cvtColor(

            frame,

            cv2.COLOR_BGR2RGB
        )

        mp_image = mp.Image(

            image_format=
                mp.ImageFormat.SRGB,

            data=
                rgb_frame
        )

        results = (
            self.detector.detect(
                mp_image
            )
        )

        detections = []

        if results.detections:

            frame_height, frame_width = (
                frame.shape[:2]
            )

            for detection in (
                results.detections
            ):

                bbox = (
                    detection.bounding_box
                )

                x = int(
                    bbox.origin_x
                )

                y = int(
                    bbox.origin_y
                )

                width = int(
                    bbox.width
                )

                height = int(
                    bbox.height
                )

                x = max(
                    0,
                    x
                )

                y = max(
                    0,
                    y
                )

                width = min(

                    width,

                    frame_width - x
                )

                height = min(

                    height,

                    frame_height - y
                )

                confidence = 0.0

                if detection.categories:

                    confidence = float(

                        detection.categories[
                            0
                        ].score
                    )

                detections.append({

                    "bbox": (
                        x,
                        y,
                        width,
                        height
                    ),

                    "confidence":
                        confidence
                })

        face_count = len(
            detections
        )

        # ==================================================
        # NO FACE
        # ==================================================

        if face_count == 0:

            return {

                "status":
                    "FACE_MISSING",

                "face_count":
                    0,

                "color":
                    (0, 0, 255),

                "detections":
                    []
            }

        # ==================================================
        # ONE FACE
        # ==================================================

        if face_count == 1:

            return {

                "status":
                    "FACE_PRESENT",

                "face_count":
                    1,

                "color":
                    (0, 255, 0),

                "detections":
                    detections
            }

        # ==================================================
        # MULTIPLE FACES
        # ==================================================

        return {

            "status":
                "MULTIPLE_FACES",

            "face_count":
                face_count,

            "color":
                (0, 165, 255),

            "detections":
                detections
        }

    # ==================================================
    # MISSING
    # ==================================================

    def _face_missing_result(self):

        return {

            "status":
                "FACE_MISSING",

            "face_count":
                0,

            "color":
                (0, 0, 255),

            "detections":
                []
        }

    # ==================================================
    # CLOSE
    # ==================================================

    def close(self):

        if self.detector is not None:

            self.detector.close()

            self.detector = None

            print(
                "MediaPipe Face Detector closed."
            )