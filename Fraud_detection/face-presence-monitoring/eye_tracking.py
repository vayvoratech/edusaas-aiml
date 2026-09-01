import math


class EyeTracker:

    def __init__(self):

        # Left eye corners
        self.LEFT_EYE_OUTER = 33
        self.LEFT_EYE_INNER = 133

        # Right eye corners
        self.RIGHT_EYE_INNER = 362
        self.RIGHT_EYE_OUTER = 263

        # Iris center landmarks
        self.LEFT_IRIS = 468
        self.RIGHT_IRIS = 473


        # ==================================================
        # THRESHOLDS
        # ==================================================

        # These are intentionally less aggressive.
        #
        # < 0.40  -> left
        # > 0.60  -> right
        # otherwise center

        self.LEFT_THRESHOLD = 0.40

        self.RIGHT_THRESHOLD = 0.60


        # ==================================================
        # SMOOTHING
        # ==================================================

        self.previous_ratio = 0.50

        self.smoothing = 0.65


        # ==================================================
        # DIRECTION STABILITY
        # ==================================================

        self.current_direction = "LOOKING_CENTER"

        self.pending_direction = None

        self.pending_count = 0

        # Number of consecutive frames required
        # before changing direction.

        self.required_frames = 3


    # ======================================================
    # SAFE LANDMARK ACCESS
    # ======================================================

    def _get_point(
        self,
        landmarks,
        index
    ):

        try:

            point = landmarks[index]

            if isinstance(
                point,
                dict
            ):

                x = float(
                    point.get("x", 0)
                )

                y = float(
                    point.get("y", 0)
                )

            else:

                x = float(
                    point[0]
                )

                y = float(
                    point[1]
                )

            return x, y

        except Exception:

            return None


    # ======================================================
    # DISTANCE
    # ======================================================

    def _distance(
        self,
        p1,
        p2
    ):

        if (
            p1 is None
            or
            p2 is None
        ):

            return 0.0

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
    # EYE RATIO
    # ======================================================

    def _eye_ratio(
        self,
        outer,
        inner,
        iris
    ):

        if (
            outer is None
            or
            inner is None
            or
            iris is None
        ):

            return None


        # ----------------------------------------------
        # Eye horizontal direction
        # ----------------------------------------------

        eye_width = self._distance(
            outer,
            inner
        )


        if eye_width < 1e-6:

            return None


        # ----------------------------------------------
        # Normalize iris position
        # ----------------------------------------------

        ratio = (

            (
                iris[0] -
                outer[0]
            )

            /

            (
                inner[0] -
                outer[0]
            )
        )


        # ----------------------------------------------
        # Clamp
        # ----------------------------------------------

        ratio = max(
            0.0,
            min(
                1.0,
                ratio
            )
        )


        return ratio


    # ======================================================
    # GET EYE DIRECTION
    # ======================================================

    def get_eye_direction(
        self,
        landmarks
    ):

        # ==================================================
        # CHECK LANDMARK COUNT
        # ==================================================

        if landmarks is None:

            return "UNKNOWN"


        if len(landmarks) <= 473:

            # Iris landmarks aren't available.
            return "UNKNOWN"


        # ==================================================
        # GET LANDMARKS
        # ==================================================

        left_outer = self._get_point(
            landmarks,
            self.LEFT_EYE_OUTER
        )

        left_inner = self._get_point(
            landmarks,
            self.LEFT_EYE_INNER
        )

        left_iris = self._get_point(
            landmarks,
            self.LEFT_IRIS
        )


        right_inner = self._get_point(
            landmarks,
            self.RIGHT_EYE_INNER
        )

        right_outer = self._get_point(
            landmarks,
            self.RIGHT_EYE_OUTER
        )

        right_iris = self._get_point(
            landmarks,
            self.RIGHT_IRIS
        )


        # ==================================================
        # CALCULATE RATIOS
        # ==================================================

        left_ratio = self._eye_ratio(

            left_outer,

            left_inner,

            left_iris
        )


        right_ratio = self._eye_ratio(

            right_inner,

            right_outer,

            right_iris
        )


        if (
            left_ratio is None
            or
            right_ratio is None
        ):

            return "UNKNOWN"


        # ==================================================
        # AVERAGE
        # ==================================================

        ratio = (

            left_ratio +
            right_ratio

        ) / 2.0


        # ==================================================
        # SMOOTHING
        # ==================================================

        ratio = (

            self.smoothing *
            self.previous_ratio

            +

            (1.0 - self.smoothing) *
            ratio
        )


        self.previous_ratio = ratio


        # ==================================================
        # CLASSIFY
        # ==================================================

        if ratio < self.LEFT_THRESHOLD:

            new_direction = (
                "LOOKING_LEFT"
            )

        elif ratio > self.RIGHT_THRESHOLD:

            new_direction = (
                "LOOKING_RIGHT"
            )

        else:

            new_direction = (
                "LOOKING_CENTER"
            )


        # ==================================================
        # STABILITY FILTER
        # ==================================================

        if (
            new_direction ==
            self.current_direction
        ):

            # Already stable.

            self.pending_direction = None

            self.pending_count = 0

            return self.current_direction


        # ----------------------------------------------
        # New direction
        # ----------------------------------------------

        if (
            new_direction ==
            self.pending_direction
        ):

            self.pending_count += 1

        else:

            self.pending_direction = (
                new_direction
            )

            self.pending_count = 1


        # ----------------------------------------------
        # Confirm direction
        # ----------------------------------------------

        if (
            self.pending_count
            >= self.required_frames
        ):

            self.current_direction = (
                new_direction
            )

            self.pending_direction = None

            self.pending_count = 0


        return self.current_direction


    # ======================================================
    # GET RAW RATIO
    # ======================================================

    def get_eye_ratio(
        self,
        landmarks
    ):

        """
        Useful for debugging/calibration.
        """

        if (
            landmarks is None
            or
            len(landmarks) <= 473
        ):

            return None


        left_outer = self._get_point(
            landmarks,
            self.LEFT_EYE_OUTER
        )

        left_inner = self._get_point(
            landmarks,
            self.LEFT_EYE_INNER
        )

        left_iris = self._get_point(
            landmarks,
            self.LEFT_IRIS
        )


        right_inner = self._get_point(
            landmarks,
            self.RIGHT_EYE_INNER
        )

        right_outer = self._get_point(
            landmarks,
            self.RIGHT_EYE_OUTER
        )

        right_iris = self._get_point(
            landmarks,
            self.RIGHT_IRIS
        )


        left_ratio = self._eye_ratio(

            left_outer,
            left_inner,
            left_iris
        )


        right_ratio = self._eye_ratio(

            right_inner,
            right_outer,
            right_iris
        )


        if (
            left_ratio is None
            or
            right_ratio is None
        ):

            return None


        return (

            left_ratio +
            right_ratio

        ) / 2.0


    # ======================================================
    # DRAW
    # ======================================================

    def draw(
        self,
        frame,
        direction
    ):

        """
        Debug visualization only.

        Do NOT use this in the production
        examination video.
        """

        import cv2


        if direction == "LOOKING_LEFT":

            color = (
                255,
                0,
                0
            )

        elif direction == "LOOKING_RIGHT":

            color = (
                0,
                0,
                255
            )

        elif direction == "LOOKING_CENTER":

            color = (
                0,
                255,
                0
            )

        else:

            color = (
                255,
                255,
                255
            )


        cv2.putText(

            frame,

            f"Eyes : {direction}",

            (
                20,
                120
            ),

            cv2.FONT_HERSHEY_SIMPLEX,

            0.8,

            color,

            2
        )


        return frame