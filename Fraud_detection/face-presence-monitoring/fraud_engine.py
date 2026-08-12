import time


class FraudEngine:

    def __init__(self):

        # ==================================================
        # CONFIGURATION
        # ==================================================

        # Violation must remain continuously detected
        # for this many seconds before it is counted.
        self.VIOLATION_PERSISTENCE_SECONDS = 3.0

        # ==================================================
        # MOBILE / PHONE RULES
        # ==================================================

        # 1st -> WARNING + 10 second pause
        # 2nd -> WARNING + 10 second pause
        # 3rd -> TERMINATE

        self.PHONE_TERMINATE_THRESHOLD = 3

        # ==================================================
        # FACE RULES
        # ==================================================

        # 1st -> WARNING
        # 2nd -> WARNING
        # 3rd -> TERMINATE

        self.FACE_TERMINATE_THRESHOLD = 3

        # ==================================================
        # HEAD POSE RULES
        # ==================================================

        # 1st head-turn -> WARNING + PAUSE
        # 2nd head-turn -> TERMINATE

        self.HEAD_TERMINATE_THRESHOLD = 2

        # ==================================================
        # BROWSER RULES
        # ==================================================

        # TAB_SWITCH + FULLSCREEN_EXIT
        #
        # 1st -> WARNING
        # 2nd -> WARNING
        # 3rd -> WARNING
        # 4th -> TERMINATE

        self.BROWSER_TERMINATE_THRESHOLD = 4

        # ==================================================
        # PHONE STATE
        # ==================================================

        self.phone_detections = 0

        self.phone_violations = 0

        self.phone_violation_start = None

        self.phone_event_counted = False

        # ==================================================
        # FACE STATE
        # ==================================================

        self.face_violations = 0

        self.face_violation_start = None

        self.face_event_counted = False

        # ==================================================
        # HEAD POSE STATE
        # ==================================================

        # Number of actual persistent head violations.

        self.head_violations = 0

        # Time at which the current head-turn
        # event started.

        self.head_violation_start = None

        # Prevents the same continuous head-turn
        # from being counted repeatedly.

        self.head_event_counted = False

        # ==================================================
        # BROWSER STATE
        # ==================================================

        self.browser_violations = 0

        self.last_browser_violation_time = {}

        # ==================================================
        # EXAM STATE
        # ==================================================

        self.exam_terminated = False

    # ======================================================
    # MAIN PHONE PROCESSOR
    # ======================================================

    def process(self, phone_result):

        now = time.time()

        # ==================================================
        # SAFETY CHECK
        # ==================================================

        if not isinstance(phone_result, dict):

            return self._normal_response(now)

        # ==================================================
        # ALREADY TERMINATED
        # ==================================================

        if self.exam_terminated:

            return self._termination_response(
                "Exam already terminated.",
                now
            )

        # ==================================================
        # READ PHONE STATUS
        # ==================================================

        phone_status = phone_result.get(
            "status",
            "NO_PHONE"
        )

        phone_detected = (
            phone_status == "PHONE_DETECTED"
        )

        phone_confidence = phone_result.get(
            "confidence",
            0.0
        )

        # ==================================================
        # PHONE DETECTED
        # ==================================================

        if phone_detected:

            # Raw frame detection count
            self.phone_detections += 1

            # ------------------------------------------------
            # START PERSISTENCE TIMER
            # ------------------------------------------------

            if self.phone_violation_start is None:

                self.phone_violation_start = now

                self.phone_event_counted = False

            # ------------------------------------------------
            # PERSISTENCE TIME
            # ------------------------------------------------

            persistence_time = (
                now -
                self.phone_violation_start
            )

            # ------------------------------------------------
            # PERSISTENCE THRESHOLD
            # ------------------------------------------------

            if (
                persistence_time
                >= self.VIOLATION_PERSISTENCE_SECONDS
            ):

                # Count continuous event only once

                if not self.phone_event_counted:

                    self.phone_event_counted = True

                    self.phone_violations += 1

                    return self._phone_action(
                        phone_confidence,
                        now
                    )

        # ==================================================
        # PHONE NO LONGER DETECTED
        # ==================================================

        else:

            self.phone_violation_start = None

            self.phone_event_counted = False

        # ==================================================
        # NORMAL
        # ==================================================

        return {
            "action": "NORMAL",
            "severity": "LOW",

            "phone_detected":
                phone_detected,

            "phone_confidence":
                phone_confidence,

            "phone_detections":
                self.phone_detections,

            "phone_violations":
                self.phone_violations,

            "face_violations":
                self.face_violations,

            "head_violations":
                self.head_violations,

            "browser_violations":
                self.browser_violations,

            "timestamp":
                now
        }

    # ======================================================
    # PHONE ACTION
    # ======================================================

    def _phone_action(
        self,
        phone_confidence,
        now
    ):

        count = self.phone_violations

        # ==================================================
        # THIRD PHONE VIOLATION
        # ==================================================

        if (
            count
            >=
            self.PHONE_TERMINATE_THRESHOLD
        ):

            self.exam_terminated = True

            return {
                "action":
                    "TERMINATE_EXAM",

                "severity":
                    "HIGH",

                "reason":
                    "Mobile phone detected three times.",

                "warning":
                    False,

                "pause":
                    False,

                "pause_duration":
                    0,

                "phone_detected":
                    True,

                "phone_confidence":
                    phone_confidence,

                "phone_detections":
                    self.phone_detections,

                "phone_violations":
                    self.phone_violations,

                "face_violations":
                    self.face_violations,

                "head_violations":
                    self.head_violations,

                "browser_violations":
                    self.browser_violations,

                "timestamp":
                    now
            }

        # ==================================================
        # FIRST / SECOND PHONE VIOLATION
        # ==================================================

        return {
            "action":
                "PAUSE_EXAM",

            "severity":
                "MEDIUM",

            "reason":
                f"Mobile phone detected. "
                f"Warning {count}/2.",

            "warning":
                True,

            "pause":
                True,

            "pause_duration":
                10,

            "phone_detected":
                True,

            "phone_confidence":
                phone_confidence,

            "phone_detections":
                self.phone_detections,

            "phone_violations":
                self.phone_violations,

            "face_violations":
                self.face_violations,

            "head_violations":
                self.head_violations,

            "browser_violations":
                self.browser_violations,

            "timestamp":
                now
        }

    # ======================================================
    # FACE PROCESSOR
    # ======================================================

    def process_face(self, face_result):

        now = time.time()

        # ==================================================
        # SAFETY CHECK
        # ==================================================

        if not isinstance(face_result, dict):

            return self._normal_response(now)

        # ==================================================
        # ALREADY TERMINATED
        # ==================================================

        if self.exam_terminated:

            return self._termination_response(
                "Exam already terminated.",
                now
            )

        # ==================================================
        # READ FACE STATUS
        # ==================================================

        face_status = face_result.get(
            "status",
            "NO_FACE"
        )

        face_detected = (
            face_status == "FACE_DETECTED"
        )

        face_confidence = face_result.get(
            "confidence",
            0.0
        )

        # ==================================================
        # FACE PRESENT
        # ==================================================

        if face_detected:

            self.face_violation_start = None

            self.face_event_counted = False

            return {
                "action":
                    "NORMAL",

                "severity":
                    "LOW",

                "face_detected":
                    True,

                "face_confidence":
                    face_confidence,

                "face_violations":
                    self.face_violations,

                "phone_violations":
                    self.phone_violations,

                "head_violations":
                    self.head_violations,

                "browser_violations":
                    self.browser_violations,

                "timestamp":
                    now
            }

        # ==================================================
        # FACE NOT DETECTED
        # ==================================================

        if self.face_violation_start is None:

            self.face_violation_start = now

            self.face_event_counted = False

        persistence_time = (
            now -
            self.face_violation_start
        )

        # ==================================================
        # PERSISTENCE CHECK
        # ==================================================

        if (
            persistence_time
            >= self.VIOLATION_PERSISTENCE_SECONDS
        ):

            if not self.face_event_counted:

                self.face_event_counted = True

                self.face_violations += 1

                return self._face_action(
                    face_confidence,
                    now
                )

        # ==================================================
        # STILL WAITING
        # ==================================================

        return {
            "action":
                "NORMAL",

            "severity":
                "LOW",

            "face_detected":
                False,

            "face_confidence":
                face_confidence,

            "face_violations":
                self.face_violations,

            "phone_violations":
                self.phone_violations,

            "head_violations":
                self.head_violations,

            "browser_violations":
                self.browser_violations,

            "timestamp":
                now
        }

    # ======================================================
    # FACE ACTION
    # ======================================================

    def _face_action(
        self,
        face_confidence,
        now
    ):

        count = self.face_violations

        # ==================================================
        # THIRD FACE VIOLATION
        # ==================================================

        if (
            count
            >=
            self.FACE_TERMINATE_THRESHOLD
        ):

            self.exam_terminated = True

            return {
                "action":
                    "TERMINATE_EXAM",

                "severity":
                    "HIGH",

                "reason":
                    "Face was not detected three times.",

                "warning":
                    False,

                "pause":
                    False,

                "face_detected":
                    False,

                "face_confidence":
                    face_confidence,

                "face_violations":
                    self.face_violations,

                "phone_violations":
                    self.phone_violations,

                "head_violations":
                    self.head_violations,

                "browser_violations":
                    self.browser_violations,

                "timestamp":
                    now
            }

        # ==================================================
        # FIRST / SECOND FACE VIOLATION
        # ==================================================

        return {
            "action":
                "WARNING",

            "severity":
                "MEDIUM",

            "reason":
                f"Face not detected. "
                f"Warning {count}/2.",

            "warning":
                True,

            "pause":
                False,

            "face_detected":
                False,

            "face_confidence":
                face_confidence,

            "face_violations":
                self.face_violations,

            "phone_violations":
                self.phone_violations,

            "head_violations":
                self.head_violations,

            "browser_violations":
                self.browser_violations,

            "timestamp":
                now
        }

    # ======================================================
    # HEAD POSE PROCESSOR
    # ======================================================

    def process_head_pose(
        self,
        head_result
    ):

        now = time.time()

        # ==================================================
        # SAFETY CHECK
        # ==================================================

        if not isinstance(
            head_result,
            dict
        ):

            return self._normal_response(now)

        # ==================================================
        # ALREADY TERMINATED
        # ==================================================

        if self.exam_terminated:

            return self._termination_response(
                "Exam already terminated.",
                now
            )

        # ==================================================
        # READ HEAD STATUS
        # ==================================================

        head_status = head_result.get(
            "status",
            "UNKNOWN"
        )

        # ==================================================
        # NORMAL HEAD POSITION
        # ==================================================

        if head_status in (
            "LOOKING_CENTER",
            "UNKNOWN",
            "NORMAL"
        ):

            # Student returned to normal position.
            #
            # This resets the continuous event.
            #
            # The next head turn can therefore become
            # a new violation.

            self.head_violation_start = None

            self.head_event_counted = False

            return {
                "action":
                    "NORMAL",

                "severity":
                    "LOW",

                "head_status":
                    head_status,

                "head_violations":
                    self.head_violations,

                "phone_violations":
                    self.phone_violations,

                "face_violations":
                    self.face_violations,

                "browser_violations":
                    self.browser_violations,

                "timestamp":
                    now
            }

        # ==================================================
        # HEAD TURN DETECTED
        # ==================================================

        if head_status not in (
            "LOOKING_LEFT",
            "LOOKING_RIGHT",
            "LOOKING_UP",
            "LOOKING_DOWN",
            "HEAD_TURNED"
        ):

            # Unknown head status should not create
            # a violation.

            return {
                "action":
                    "NORMAL",

                "severity":
                    "LOW",

                "head_status":
                    head_status,

                "head_violations":
                    self.head_violations,

                "phone_violations":
                    self.phone_violations,

                "face_violations":
                    self.face_violations,

                "browser_violations":
                    self.browser_violations,

                "timestamp":
                    now
            }

        # ==================================================
        # START CONTINUOUS HEAD-TURN TIMER
        # ==================================================

        if self.head_violation_start is None:

            self.head_violation_start = now

            self.head_event_counted = False

            return {
                "action":
                    "NORMAL",

                "severity":
                    "LOW",

                "head_status":
                    head_status,

                "head_violations":
                    self.head_violations,

                "phone_violations":
                    self.phone_violations,

                "face_violations":
                    self.face_violations,

                "browser_violations":
                    self.browser_violations,

                "timestamp":
                    now
            }

        # ==================================================
        # CALCULATE PERSISTENCE
        # ==================================================

        persistence_time = (
            now -
            self.head_violation_start
        )

        # ==================================================
        # WAIT UNTIL 3 SECONDS
        # ==================================================

        if (
            persistence_time
            <
            self.VIOLATION_PERSISTENCE_SECONDS
        ):

            return {
                "action":
                    "NORMAL",

                "severity":
                    "LOW",

                "head_status":
                    head_status,

                "head_persistence":
                    round(
                        persistence_time,
                        2
                    ),

                "head_violations":
                    self.head_violations,

                "phone_violations":
                    self.phone_violations,

                "face_violations":
                    self.face_violations,

                "browser_violations":
                    self.browser_violations,

                "timestamp":
                    now
            }

        # ==================================================
        # SAME CONTINUOUS EVENT
        # ==================================================

        if self.head_event_counted:

            return {
                "action":
                    "NORMAL",

                "severity":
                    "LOW",

                "head_status":
                    head_status,

                "head_violations":
                    self.head_violations,

                "phone_violations":
                    self.phone_violations,

                "face_violations":
                    self.face_violations,

                "browser_violations":
                    self.browser_violations,

                "timestamp":
                    now
            }

        # ==================================================
        # COUNT ONE HEAD VIOLATION
        # ==================================================

        self.head_event_counted = True

        self.head_violations += 1

        count = self.head_violations

        # ==================================================
        # SECOND HEAD VIOLATION
        # ==================================================

        if (
            count
            >=
            self.HEAD_TERMINATE_THRESHOLD
        ):

            self.exam_terminated = True

            return {
                "action":
                    "TERMINATE_EXAM",

                "severity":
                    "HIGH",

                "reason":
                    "Maximum head-pose violations exceeded.",

                "warning":
                    False,

                "pause":
                    False,

                "pause_duration":
                    0,

                "head_status":
                    head_status,

                "head_violations":
                    self.head_violations,

                "phone_violations":
                    self.phone_violations,

                "face_violations":
                    self.face_violations,

                "browser_violations":
                    self.browser_violations,

                "timestamp":
                    now
            }

        # ==================================================
        # FIRST HEAD VIOLATION
        # ==================================================

        return {
            "action":
                "PAUSE_EXAM",

            "severity":
                "MEDIUM",

            "reason":
                f"Head turned detected. "
                f"Warning {count}/1.",

            "warning":
                True,

            "pause":
                True,

            "pause_duration":
                10,

            "head_status":
                head_status,

            "head_violations":
                self.head_violations,

            "phone_violations":
                self.phone_violations,

            "face_violations":
                self.face_violations,

            "browser_violations":
                self.browser_violations,

            "timestamp":
                now
        }

    # ======================================================
    # BROWSER VIOLATION PROCESSOR
    # ======================================================

    def process_browser_violation(
        self,
        event_name,
        metadata=None
    ):

        now = time.time()

        if metadata is None:

            metadata = {}

        # ==================================================
        # ALREADY TERMINATED
        # ==================================================

        if self.exam_terminated:

            return self._termination_response(
                "Exam already terminated.",
                now
            )

        # ==================================================
        # ONLY TAB/FULLSCREEN COUNT
        # ==================================================

        if event_name not in {
            "TAB_SWITCH",
            "FULLSCREEN_EXIT"
        }:

            return {
                "action":
                    "NORMAL",

                "severity":
                    "LOW",

                "browser_event":
                    event_name,

                "ignored":
                    True,

                "browser_violations":
                    self.browser_violations,

                "timestamp":
                    now
            }

        # ==================================================
        # DUPLICATE EVENT COOLDOWN
        # ==================================================

        last_time = (
            self.last_browser_violation_time.get(
                event_name,
                0.0
            )
        )

        if (
            now - last_time
            < 1.5
        ):

            return {
                "action":
                    "NORMAL",

                "severity":
                    "LOW",

                "browser_event":
                    event_name,

                "duplicate":
                    True,

                "browser_violations":
                    self.browser_violations,

                "timestamp":
                    now
            }

        # ==================================================
        # COUNT
        # ==================================================

        self.last_browser_violation_time[
            event_name
        ] = now

        self.browser_violations += 1

        count = self.browser_violations

        # ==================================================
        # FOURTH BROWSER VIOLATION
        # ==================================================

        if (
            count
            >=
            self.BROWSER_TERMINATE_THRESHOLD
        ):

            self.exam_terminated = True

            return {
                "action":
                    "TERMINATE_EXAM",

                "severity":
                    "HIGH",

                "reason":
                    "Maximum tab-switch/fullscreen violations exceeded.",

                "warning":
                    False,

                "pause":
                    False,

                "browser_event":
                    event_name,

                "browser_violations":
                    self.browser_violations,

                "phone_violations":
                    self.phone_violations,

                "face_violations":
                    self.face_violations,

                "head_violations":
                    self.head_violations,

                "metadata":
                    metadata,

                "timestamp":
                    now
            }

        # ==================================================
        # FIRST / SECOND / THIRD
        # ==================================================

        return {
            "action":
                "WARNING",

            "severity":
                "MEDIUM",

            "reason":
                f"{event_name} detected. "
                f"Warning {count}/3.",

            "warning":
                True,

            "pause":
                False,

            "browser_event":
                event_name,

            "browser_violations":
                self.browser_violations,

            "phone_violations":
                self.phone_violations,

            "face_violations":
                self.face_violations,

            "head_violations":
                self.head_violations,

            "metadata":
                metadata,

            "timestamp":
                now
        }

    # ======================================================
    # NORMAL RESPONSE
    # ======================================================

    def _normal_response(
        self,
        now
    ):

        return {
            "action":
                "NORMAL",

            "severity":
                "LOW",

            "phone_detected":
                False,

            "phone_confidence":
                0.0,

            "face_detected":
                True,

            "phone_detections":
                self.phone_detections,

            "phone_violations":
                self.phone_violations,

            "face_violations":
                self.face_violations,

            "head_violations":
                self.head_violations,

            "browser_violations":
                self.browser_violations,

            "timestamp":
                now
        }

    # ======================================================
    # TERMINATION RESPONSE
    # ======================================================

    def _termination_response(
        self,
        reason,
        now
    ):

        return {
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

            "phone_violations":
                self.phone_violations,

            "face_violations":
                self.face_violations,

            "head_violations":
                self.head_violations,

            "browser_violations":
                self.browser_violations,

            "timestamp":
                now
        }

    # ======================================================
    # RESET ENGINE
    # ======================================================

    def reset(self):

        self.phone_detections = 0

        self.phone_violations = 0

        self.phone_violation_start = None

        self.phone_event_counted = False

        self.face_violations = 0

        self.face_violation_start = None

        self.face_event_counted = False

        self.head_violations = 0

        self.head_violation_start = None

        self.head_event_counted = False

        self.browser_violations = 0

        self.last_browser_violation_time = {}

        self.exam_terminated = False