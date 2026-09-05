
import cv2
import math
import time


class BlinkDetector:

    def __init__(self):

       

        self.LEFT = {

            "left": 33,

            "right": 133,

            "top1": 159,

            "top2": 160,

            "bottom1": 145,

            "bottom2": 144
        }


        # ==================================================
        # RIGHT EYE LANDMARKS
        # ==================================================

        self.RIGHT = {

            "left": 362,

            "right": 263,

            "top1": 386,

            "top2": 385,

            "bottom1": 374,

            "bottom2": 380
        }


        # ==================================================
        # EAR THRESHOLDS
        # ==================================================

        # Below this = eyes probably closed

        self.close_threshold = 0.21


        # Above this = eyes probably open

        self.open_threshold = 0.24


        # ==================================================
        # EAR SMOOTHING
        # ==================================================

        self.previous_ear = None

        self.smoothing = 0.70


        # ==================================================
        # STATE
        # ==================================================

        self.eye_state = "EYES_OPEN"

        self.previous_state = "EYES_OPEN"


        # ==================================================
        # BLINK COUNT
        # ==================================================

        self.total_blinks = 0


        # ==================================================
        # BLINK TIMING
        # ==================================================

        self.blink_start_time = None

        self.last_blink_time = 0.0

        self.blink_duration = 0.0


        # ==================================================
        # FRAME STABILITY
        # ==================================================

        self.closed_frames = 0

        self.open_frames = 0


        self.required_closed_frames = 2

        self.required_open_frames = 2


    # ======================================================
    # DISTANCE
    # ======================================================

    def distance(
        self,
        p1,
        p2
    ):

        return math.sqrt(

            (
                p1[0] -
                p2[0]
            ) ** 2

            +

            (
                p1[1] -
                p2[1]
            ) ** 2
        )


    # ======================================================
    # EYE ASPECT RATIO
    # ======================================================

    def eye_ratio(
        self,
        eye,
        landmarks
    ):

        try:

            horizontal = self.distance(

                landmarks[
                    eye["left"]
                ],

                landmarks[
                    eye["right"]
                ]
            )


            vertical1 = self.distance(

                landmarks[
                    eye["top1"]
                ],

                landmarks[
                    eye["bottom1"]
                ]
            )


            vertical2 = self.distance(

                landmarks[
                    eye["top2"]
                ],

                landmarks[
                    eye["bottom2"]
                ]
            )


            vertical = (

                vertical1 +
                vertical2

            ) / 2.0


            ratio = (

                vertical /
                (
                    horizontal +
                    1e-6
                )
            )


            return ratio


        except Exception:

            return None


    # ======================================================
    # CALCULATE EAR
    # ======================================================

    def calculate_ear(
        self,
        landmarks
    ):

        if landmarks is None:

            return None


        try:

            left_ratio = (
                self.eye_ratio(
                    self.LEFT,
                    landmarks
                )
            )


            right_ratio = (
                self.eye_ratio(
                    self.RIGHT,
                    landmarks
                )
            )


            if (
                left_ratio is None
                or
                right_ratio is None
            ):

                return None


            ear = (

                left_ratio +
                right_ratio

            ) / 2.0


            return ear


        except Exception:

            return None


    # ======================================================
    # SMOOTH EAR
    # ======================================================

    def smooth_ear(
        self,
        ear
    ):

        if self.previous_ear is None:

            self.previous_ear = ear

            return ear


        smoothed = (

            self.smoothing *
            self.previous_ear

            +

            (1.0 - self.smoothing) *
            ear
        )


        self.previous_ear = smoothed


        return smoothed


    # ======================================================
    # DETECT BLINK
    # ======================================================

    def detect(
        self,
        landmarks
    ):

        # ==================================================
        # CALCULATE EAR
        # ==================================================

        ear = self.calculate_ear(
            landmarks
        )


        if ear is None:

            return {

                "status":
                    "UNKNOWN",

                "ear":
                    0.0,

                "blink":
                    False,

                "blink_count":
                    self.total_blinks,

                "blink_duration":
                    0.0,

                "color":
                    (255, 255, 255)
            }


        # ==================================================
        # SMOOTH EAR
        # ==================================================

        ear = self.smooth_ear(
            ear
        )


        # ==================================================
        # POSSIBLY CLOSED
        # ==================================================

        if ear < self.close_threshold:

            self.closed_frames += 1

            self.open_frames = 0


        # ==================================================
        # POSSIBLY OPEN
        # ==================================================

        elif ear > self.open_threshold:

            self.open_frames += 1

            self.closed_frames = 0


        # ==================================================
        # BETWEEN THRESHOLDS
        # ==================================================

        else:

            # Keep the previous state.

            self.closed_frames = 0

            self.open_frames = 0


        # ==================================================
        # CONFIRM EYES CLOSED
        # ==================================================

        if (

            self.closed_frames
            >= self.required_closed_frames

            and

            self.eye_state
            != "EYES_CLOSED"

        ):

            self.eye_state = (
                "EYES_CLOSED"
            )


            self.blink_start_time = (
                time.time()
            )


        # ==================================================
        # CONFIRM EYES OPEN
        # ==================================================

        if (

            self.open_frames
            >= self.required_open_frames

            and

            self.eye_state
            == "EYES_CLOSED"

        ):

            self.eye_state = (
                "EYES_OPEN"
            )


            # ----------------------------------------------
            # Calculate blink duration
            # ----------------------------------------------

            if (
                self.blink_start_time
                is not None
            ):

                self.blink_duration = (

                    time.time()
                    -
                    self.blink_start_time
                )


            else:

                self.blink_duration = 0.0


            # ----------------------------------------------
            # Count blink
            # ----------------------------------------------

            self.total_blinks += 1


            self.last_blink_time = (
                time.time()
            )


            self.blink_start_time = None


        # ==================================================
        # BLINK EVENT
        # ==================================================

        blink_event = (

            self.total_blinks
            >
            getattr(
                self,
                "_reported_blink_count",
                0
            )
        )


        self._reported_blink_count = (
            self.total_blinks
        )


        # ==================================================
        # STATUS
        # ==================================================

        if self.eye_state == "EYES_CLOSED":

            status = "EYES_CLOSED"

            color = (
                0,
                0,
                255
            )


        elif self.eye_state == "EYES_OPEN":

            status = "EYES_OPEN"

            color = (
                0,
                255,
                0
            )


        else:

            status = "UNKNOWN"

            color = (
                255,
                255,
                255
            )


        # ==================================================
        # RETURN
        # ==================================================

        return {

            "status":
                status,

            "ear":
                round(
                    ear,
                    3
                ),

            "blink":
                blink_event,

            "blink_count":
                self.total_blinks,

            "blink_duration":
                round(
                    self.blink_duration,
                    3
                ),

            "color":
                color
        }


    # ======================================================
    # DRAW
    # ======================================================

    def draw(
        self,
        frame,
        result
    ):

        if not isinstance(
            result,
            dict
        ):

            return frame


        status = result.get(
            "status",
            "UNKNOWN"
        )


        ear = result.get(
            "ear",
            0.0
        )


        blink_count = result.get(
            "blink_count",
            0
        )


        color = result.get(

            "color",

            (
                255,
                255,
                255
            )
        )


        # ==================================================
        # STATUS
        # ==================================================

        cv2.putText(

            frame,

            f"Blink : {status}",

            (
                20,
                160
            ),

            cv2.FONT_HERSHEY_SIMPLEX,

            0.8,

            color,

            2
        )


        # ==================================================
        # EAR
        # ==================================================

        cv2.putText(

            frame,

            f"EAR : {ear:.3f}",

            (
                20,
                190
            ),

            cv2.FONT_HERSHEY_SIMPLEX,

            0.7,

            color,

            2
        )


        # ==================================================
        # BLINK COUNT
        # ==================================================

        cv2.putText(

            frame,

            f"Blinks : {blink_count}",

            (
                20,
                220
            ),

            cv2.FONT_HERSHEY_SIMPLEX,

            0.7,

            color,

            2
        )


        return frame
