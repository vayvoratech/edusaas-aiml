import time


class FraudEngine:
    """
    Fraud detection state for one examination session.

    Rules:

    FACE
        1st violation -> WARNING
        2nd violation -> TERMINATE

    PHONE
        1st violation -> WARNING + 10 second PAUSE
        2nd violation -> TERMINATE

    BLINK
        5 blinks  -> WARNING
        10 blinks -> TERMINATE

    MOUTH
        5 events  -> WARNING
        10 events -> TERMINATE

    EYE TRACKING
        5 events  -> WARNING
        10 events -> TERMINATE

    HEAD POSE
        REMOVED
    """

    # ======================================================
    # CONFIGURATION
    # ======================================================

    VIOLATION_PERSISTENCE_SECONDS = 3.0

    FACE_TERMINATE_THRESHOLD = 2
    PHONE_TERMINATE_THRESHOLD = 2

    BLINK_WARNING_THRESHOLD = 5
    BLINK_TERMINATE_THRESHOLD = 10

    MOUTH_WARNING_THRESHOLD = 5
    MOUTH_TERMINATE_THRESHOLD = 10

    EYE_WARNING_THRESHOLD = 5
    EYE_TERMINATE_THRESHOLD = 10

    def __init__(self):

        # ==================================================
        # PHONE
        # ==================================================

        self.phone_detections = 0

        self.phone_violations = 0

        self.phone_violation_start = None

        self.phone_event_counted = False

        # ==================================================
        # FACE
        # ==================================================

        self.face_violations = 0

        self.face_violation_start = None

        self.face_event_counted = False

        # ==================================================
        # BLINK
        # ==================================================

        self.blink_count = 0

        self.blink_event_active = False

        # ==================================================
        # MOUTH
        # ==================================================

        self.mouth_count = 0

        self.mouth_event_active = False

        # ==================================================
        # EYE TRACKING
        # ==================================================

        self.eye_tracking_count = 0

        self.eye_event_active = False

        # ==================================================
        # EXAM
        # ==================================================

        self.exam_terminated = False

    # ======================================================
    # COUNTS
    # ======================================================

    def _counts(self):

        return {

            "phone_detections":
                self.phone_detections,

            "phone_violations":
                self.phone_violations,

            "face_violations":
                self.face_violations,

            "blink_count":
                self.blink_count,

            "mouth_count":
                self.mouth_count,

            "eye_tracking_count":
                self.eye_tracking_count,

        }

    # ======================================================
    # NORMAL
    # ======================================================

    def _normal(
        self,
        now,
        **extra
    ):

        return {

            "action":
                "NORMAL",

            "severity":
                "LOW",

            **self._counts(),

            **extra,

            "timestamp":
                now
        }

    # ======================================================
    # WARNING
    # ======================================================

    def _warning(
        self,
        reason,
        violation_type,
        now,
        **extra
    ):

        return {

            "action":
                "WARNING",

            "severity":
                "MEDIUM",

            "reason":
                reason,

            "violation_type":
                violation_type,

            "warning":
                True,

            "pause":
                False,

            **self._counts(),

            **extra,

            "timestamp":
                now
        }

    # ======================================================
    # PAUSE
    # ======================================================

    def _pause(
        self,
        reason,
        violation_type,
        now,
        duration=10,
        **extra
    ):

        return {

            "action":
                "PAUSE_EXAM",

            "severity":
                "MEDIUM",

            "reason":
                reason,

            "violation_type":
                violation_type,

            "warning":
                True,

            "pause":
                True,

            "pause_duration":
                duration,

            **self._counts(),

            **extra,

            "timestamp":
                now
        }

    # ======================================================
    # TERMINATE
    # ======================================================

    def _terminate(
        self,
        reason,
        now,
        violation_type=None,
        **extra
    ):

        result = {

            "action":
                "TERMINATE_EXAM",

            "severity":
                "HIGH",

            "reason":
                reason,

            "warning":
                False,

            "pause":
                False,

            "pause_duration":
                0,

            **self._counts(),

            **extra,

            "timestamp":
                now
        }

        if violation_type:

            result[
                "violation_type"
            ] = violation_type

        return result

    # ======================================================
    # TERMINATION CHECK
    # ======================================================

    def _check_terminated(
        self,
        now
    ):

        if self.exam_terminated:

            return self._terminate(
                "Exam already terminated.",
                now
            )

        return None

    # ======================================================
    # PHONE
    # ======================================================

    def process(
        self,
        phone_result
    ):

        now = time.time()

        if not isinstance(
            phone_result,
            dict
        ):

            return self._normal(
                now
            )

        result = self._check_terminated(
            now
        )

        if result:

            return result

        phone_status = phone_result.get(
            "status",
            "NO_PHONE"
        )

        detected = (
            phone_status ==
            "PHONE_DETECTED"
        )

        confidence = float(
            phone_result.get(
                "confidence",
                0.0
            ) or 0.0
        )

        # --------------------------------------------------
        # NO PHONE
        # --------------------------------------------------

        if not detected:

            self.phone_violation_start = None

            self.phone_event_counted = False

            return self._normal(

                now,

                phone_detected=False,

                phone_confidence=confidence
            )

        # --------------------------------------------------
        # PHONE DETECTED
        # --------------------------------------------------

        self.phone_detections += 1

        if self.phone_violation_start is None:

            self.phone_violation_start = now

            self.phone_event_counted = False

        persistence = (
            now -
            self.phone_violation_start
        )

        if (
            persistence >=
            self.VIOLATION_PERSISTENCE_SECONDS
            and
            not self.phone_event_counted
        ):

            self.phone_event_counted = True

            self.phone_violations += 1

            # SECOND PHONE VIOLATION
            if self.phone_violations >= 2:

                self.exam_terminated = True

                return self._terminate(

                    "Mobile phone detected for the second violation.",

                    now,

                    "MOBILE_PHONE",

                    phone_detected=True,

                    phone_confidence=confidence
                )

            # FIRST PHONE VIOLATION
            return self._pause(

                "Mobile phone detected. First violation.",

                "MOBILE_PHONE",

                now,

                duration=10,

                phone_detected=True,

                phone_confidence=confidence
            )

        return self._normal(

            now,

            phone_detected=True,

            phone_confidence=confidence,

            phone_persistence=round(
                persistence,
                2
            )
        )

    # ======================================================
    # FACE
    # ======================================================

    def process_face(
        self,
        face_result
    ):

        now = time.time()

        if not isinstance(
            face_result,
            dict
        ):

            return self._normal(
                now
            )

        result = self._check_terminated(
            now
        )

        if result:

            return result

        face_status = str(
            face_result.get(
                "status",
                "FACE_MISSING"
            )
        ).upper()

        face_count = int(
            face_result.get(
                "face_count",
                0
            ) or 0
        )

        # IMPORTANT:
        #
        # face_presence.py returns:
        #
        # FACE_PRESENT
        #
        # not FACE_DETECTED.

        face_detected = (
            face_status in {
                "FACE_PRESENT",
                "FACE_DETECTED"
            }
            and
            face_count == 1
        )

        # --------------------------------------------------
        # FACE PRESENT
        # --------------------------------------------------

        if face_detected:

            self.face_violation_start = None

            self.face_event_counted = False

            return self._normal(

                now,

                face_detected=True,

                face_count=face_count
            )

        # --------------------------------------------------
        # FACE MISSING / MULTIPLE
        # --------------------------------------------------

        if self.face_violation_start is None:

            self.face_violation_start = now

            self.face_event_counted = False

        persistence = (
            now -
            self.face_violation_start
        )

        # --------------------------------------------------
        # WAIT 3 SECONDS
        # --------------------------------------------------

        if (
            persistence <
            self.VIOLATION_PERSISTENCE_SECONDS
        ):

            return self._normal(

                now,

                face_detected=False,

                face_count=face_count,

                face_persistence=round(
                    persistence,
                    2
                )
            )

        # --------------------------------------------------
        # COUNT ONLY ONCE
        # --------------------------------------------------

        if self.face_event_counted:

            return self._normal(

                now,

                face_detected=False,

                face_count=face_count,

                face_violations=
                    self.face_violations
            )

        self.face_event_counted = True

        self.face_violations += 1

        # --------------------------------------------------
        # SECOND FACE VIOLATION
        # --------------------------------------------------

        if (
            self.face_violations >=
            self.FACE_TERMINATE_THRESHOLD
        ):

            self.exam_terminated = True

            return self._terminate(

                "Face was not detected for the second violation.",

                now,

                "FACE_NOT_DETECTED",

                face_detected=False,

                face_count=face_count
            )

        # --------------------------------------------------
        # FIRST FACE VIOLATION
        # --------------------------------------------------

        return self._warning(

            "Face was not detected. First violation.",

            "FACE_NOT_DETECTED",

            now,

            face_detected=False,

            face_count=face_count
        )

    # ======================================================
    # GENERIC EVENT COUNTER
    # ======================================================

    def _process_event_counter(

        self,

        detected,

        event_name,

        count_attribute,

        active_attribute,

        warning_threshold,

        terminate_threshold,

        now
    ):

        count = getattr(
            self,
            count_attribute
        )

        active = getattr(
            self,
            active_attribute
        )

        # --------------------------------------------------
        # EVENT ENDED
        # --------------------------------------------------

        if not detected:

            setattr(
                self,
                active_attribute,
                False
            )

            return self._normal(

                now,

                violation_type=
                    event_name,

                event_count=
                    count
            )

        # --------------------------------------------------
        # SAME EVENT
        # --------------------------------------------------

        if active:

            return self._normal(

                now,

                violation_type=
                    event_name,

                event_count=
                    count
            )

        # --------------------------------------------------
        # NEW EVENT
        # --------------------------------------------------

        setattr(
            self,
            active_attribute,
            True
        )

        count += 1

        setattr(
            self,
            count_attribute,
            count
        )

        print(
            f"{event_name} EVENT: {count}"
        )

        # --------------------------------------------------
        # 10 -> TERMINATE
        # --------------------------------------------------

        if count >= terminate_threshold:

            self.exam_terminated = True

            return self._terminate(

                f"{event_name} count reached {count}.",

                now,

                event_name,

                event_count=count
            )

        # --------------------------------------------------
        # 5 -> WARNING
        # --------------------------------------------------

        if count == warning_threshold:

            return self._warning(

                f"{event_name} count reached {count}.",

                event_name,

                now,

                event_count=count
            )

        return self._normal(

            now,

            violation_type=
                event_name,

            event_count=
                count
        )

    # ======================================================
    # BLINK
    # ======================================================

    def process_blink(
        self,
        blink_result
    ):

        now = time.time()

        if not isinstance(
            blink_result,
            dict
        ):

            return self._normal(
                now
            )

        result = self._check_terminated(
            now
        )

        if result:

            return result

        blink = bool(
            blink_result.get(
                "blink_detected",

                blink_result.get(
                    "is_blink",

                    blink_result.get(
                        "blink",
                        False
                    )
                )
            )
        )

        return self._process_event_counter(

            detected=blink,

            event_name="BLINK",

            count_attribute=
                "blink_count",

            active_attribute=
                "blink_event_active",

            warning_threshold=
                self.BLINK_WARNING_THRESHOLD,

            terminate_threshold=
                self.BLINK_TERMINATE_THRESHOLD,

            now=now
        )

    # ======================================================
    # MOUTH
    # ======================================================

    def process_mouth(
        self,
        mouth_result
    ):

        now = time.time()

        if not isinstance(
            mouth_result,
            dict
        ):

            return self._normal(
                now
            )

        result = self._check_terminated(
            now
        )

        if result:

            return result

        status = str(

            mouth_result.get(

                "status",

                mouth_result.get(
                    "mouth_status",
                    "NORMAL"
                )
            )

        ).upper()

        mouth_violation = (
            status in {
                "MOUTH_OPEN",
                "OPEN_MOUTH",
                "MOUTH_ABNORMAL",
                "MOUTH_VIOLATION"
            }
        )

        return self._process_event_counter(

            detected=
                mouth_violation,

            event_name=
                "MOUTH",

            count_attribute=
                "mouth_count",

            active_attribute=
                "mouth_event_active",

            warning_threshold=
                self.MOUTH_WARNING_THRESHOLD,

            terminate_threshold=
                self.MOUTH_TERMINATE_THRESHOLD,

            now=now
        )

    # ======================================================
    # EYE TRACKING
    # ======================================================

    def process_eye_tracking(
        self,
        eye_result
    ):

        now = time.time()

        if not isinstance(
            eye_result,
            dict
        ):

            return self._normal(
                now
            )

        result = self._check_terminated(
            now
        )

        if result:

            return result

        status = str(

            eye_result.get(

                "status",

                eye_result.get(
                    "eye_status",
                    "NORMAL"
                )
            )

        ).upper()

        eye_violation = (
            status in {
                "LOOKING_LEFT",
                "LOOKING_RIGHT",
                "LOOKING_UP",
                "LOOKING_DOWN",
                "EYES_AWAY",
                "EYE_VIOLATION",
                "GAZE_AWAY"
            }
        )

        return self._process_event_counter(

            detected=
                eye_violation,

            event_name=
                "EYE_TRACKING",

            count_attribute=
                "eye_tracking_count",

            active_attribute=
                "eye_event_active",

            warning_threshold=
                self.EYE_WARNING_THRESHOLD,

            terminate_threshold=
                self.EYE_TERMINATE_THRESHOLD,

            now=now
        )

    # ======================================================
    # RESET
    # ======================================================

    def reset(self):

        self.phone_detections = 0

        self.phone_violations = 0

        self.phone_violation_start = None

        self.phone_event_counted = False

        self.face_violations = 0

        self.face_violation_start = None

        self.face_event_counted = False

        self.blink_count = 0

        self.blink_event_active = False

        self.mouth_count = 0

        self.mouth_event_active = False

        self.eye_tracking_count = 0

        self.eye_event_active = False

        self.exam_terminated = False