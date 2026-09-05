
import cv2
import threading
import time
from ultralytics import YOLO


class PhoneDetector:

    def __init__(
        self,
        model_path="yolo11s.pt",
        confidence=0.15,
        imgsz=640,
        inference_interval=0.05
    ):

        # ==================================================
        # MODEL
        # ==================================================

        self.model = YOLO(
            model_path
        )

        # COCO class:
        # 67 = cell phone
        self.PHONE_CLASS = 67

        self.confidence = confidence

        self.imgsz = imgsz

        # Minimum time between inference jobs.
        #
        # This prevents YOLO from consuming every
        # camera frame when inference is slower.
        self.inference_interval = (
            inference_interval
        )


        # ==================================================
        # FRAME BUFFER
        # ==================================================

        self.latest_frame = None


        # ==================================================
        # RESULT
        # ==================================================

        self.latest_result = {

            "status":
                "NO_PHONE",

            "phones":
                [],

            "count":
                0,

            "confidence":
                0.0,

            "timestamp":
                0.0,

            "inference_ms":
                0.0
        }


        # ==================================================
        # THREAD CONTROL
        # ==================================================

        self.running = True

        self.lock = threading.Lock()


        # ==================================================
        # TEMPORAL DETECTION
        # ==================================================

        # Number of consecutive positive detections.
        self.positive_frames = 0

        # Number of consecutive negative detections.
        self.negative_frames = 0


        # Require several positive detections before
        # considering the phone confirmed.
        self.confirm_frames = 2


        # Keep phone state alive for a short period
        # when YOLO temporarily misses it.
        self.persistence_seconds = 0.8


        self.last_positive_time = 0.0


        # ==================================================
        # THREAD
        # ==================================================

        self.thread = threading.Thread(

            target=self._detection_loop,

            daemon=True
        )

        self.thread.start()


    # ======================================================
    # SUBMIT CAMERA FRAME
    # ======================================================

    def detect(self, frame):

        """
        Submit the newest camera frame to the
        background YOLO11s worker.

        This method does NOT wait for inference.

        Returns the latest available result.
        """

        if frame is None:

            return self.get_result()


        # -----------------------------------------------
        # Store newest frame
        # -----------------------------------------------

        with self.lock:

            self.latest_frame = frame.copy()


            # Return a snapshot of latest result.
            result = {

                "status":
                    self.latest_result[
                        "status"
                    ],

                "phones":
                    list(
                        self.latest_result[
                            "phones"
                        ]
                    ),

                "count":
                    self.latest_result[
                        "count"
                    ],

                "confidence":
                    self.latest_result[
                        "confidence"
                    ],

                "timestamp":
                    self.latest_result[
                        "timestamp"
                    ],

                "inference_ms":
                    self.latest_result[
                        "inference_ms"
                    ]
            }


        return result


    # ======================================================
    # GET RESULT
    # ======================================================

    def get_result(self):

        with self.lock:

            return {

                "status":
                    self.latest_result[
                        "status"
                    ],

                "phones":
                    list(
                        self.latest_result[
                            "phones"
                        ]
                    ),

                "count":
                    self.latest_result[
                        "count"
                    ],

                "confidence":
                    self.latest_result[
                        "confidence"
                    ],

                "timestamp":
                    self.latest_result[
                        "timestamp"
                    ],

                "inference_ms":
                    self.latest_result[
                        "inference_ms"
                    ]
            }


    # ======================================================
    # YOLO BACKGROUND LOOP
    # ======================================================

    def _detection_loop(self):

        while self.running:

            # ------------------------------------------
            # Get newest frame
            # ------------------------------------------

            frame = None

            with self.lock:

                if self.latest_frame is not None:

                    frame = (
                        self.latest_frame.copy()
                    )

                    # Clear buffer.
                    #
                    # We only care about the
                    # newest available frame.
                    self.latest_frame = None


            # ------------------------------------------
            # No frame
            # ------------------------------------------

            if frame is None:

                time.sleep(0.005)

                continue


            # ------------------------------------------
            # Inference
            # ------------------------------------------

            inference_start = (
                time.perf_counter()
            )


            try:

                results = self.model.predict(

                    source=frame,

                    imgsz=self.imgsz,

                    conf=self.confidence,

                    iou=0.45,

                    max_det=5,

                    verbose=False,

                    # Do not display anything.
                    show=False
                )


                inference_ms = (

                    time.perf_counter()
                    - inference_start

                ) * 1000


                # --------------------------------------
                # Extract phone detections
                # --------------------------------------

                phones = []

                highest_confidence = 0.0


                for result in results:

                    if result.boxes is None:

                        continue


                    for box in result.boxes:

                        cls = int(
                            box.cls.item()
                        )

                        conf = float(
                            box.conf.item()
                        )


                        # ----------------------------------
                        # Cell phone
                        # ----------------------------------

                        if (
                            cls ==
                            self.PHONE_CLASS
                        ):

                            x1, y1, x2, y2 = map(

                                int,

                                box.xyxy[
                                    0
                                ].tolist()
                            )


                            # --------------------------------
                            # Ignore invalid boxes
                            # --------------------------------

                            if (
                                x2 <= x1
                                or
                                y2 <= y1
                            ):

                                continue


                            highest_confidence = max(

                                highest_confidence,

                                conf
                            )


                            phones.append({

                                "bbox": (
                                    x1,
                                    y1,
                                    x2,
                                    y2
                                ),

                                "confidence":
                                    round(
                                        conf,
                                        3
                                    ),

                                "label":
                                    "cell phone"
                            })


                now = time.time()


                # ==================================================
                # POSITIVE DETECTION
                # ==================================================

                if phones:

                    self.positive_frames += 1

                    self.negative_frames = 0

                    self.last_positive_time = now


                    # ----------------------------------------------
                    # PHONE CONFIRMED
                    # ----------------------------------------------

                    if (
                        self.positive_frames
                        >= self.confirm_frames
                    ):

                        result_data = {

                            "status":
                                "PHONE_DETECTED",

                            "phones":
                                phones,

                            "count":
                                len(phones),

                            "confidence":
                                round(
                                    highest_confidence,
                                    3
                                ),

                            "timestamp":
                                now,

                            "inference_ms":
                                round(
                                    inference_ms,
                                    2
                                )
                        }


                    # ----------------------------------------------
                    # PHONE NOT YET CONFIRMED
                    # ----------------------------------------------

                    else:

                        result_data = {

                            "status":
                                "PHONE_PENDING",

                            "phones":
                                phones,

                            "count":
                                len(phones),

                            "confidence":
                                round(
                                    highest_confidence,
                                    3
                                ),

                            "timestamp":
                                now,

                            "inference_ms":
                                round(
                                    inference_ms,
                                    2
                                )
                        }


                # ==================================================
                # NO PHONE
                # ==================================================

                else:

                    self.negative_frames += 1

                    self.positive_frames = 0


                    # ----------------------------------------------
                    # TEMPORARY MISS
                    # ----------------------------------------------

                    time_since_positive = (

                        now
                        -
                        self.last_positive_time
                    )


                    # ----------------------------------------------
                    # PHONE PERSISTENCE
                    # ----------------------------------------------

                    if (

                        self.last_positive_time > 0

                        and

                        time_since_positive
                        < self.persistence_seconds

                    ):

                        # Keep the previous detection alive.
                        #
                        # This is useful when a phone is moved
                        # quickly and YOLO misses one frame.

                        with self.lock:

                            previous_phones = list(

                                self.latest_result.get(

                                    "phones",

                                    []
                                )
                            )

                            previous_confidence = (

                                self.latest_result.get(

                                    "confidence",

                                    0.0
                                )
                            )


                        result_data = {

                            "status":
                                "PHONE_DETECTED",

                            "phones":
                                previous_phones,

                            "count":
                                len(
                                    previous_phones
                                ),

                            "confidence":
                                previous_confidence,

                            "timestamp":
                                now,

                            "inference_ms":
                                round(
                                    inference_ms,
                                    2
                                )
                        }


                    # ----------------------------------------------
                    # DEFINITELY NO PHONE
                    # ----------------------------------------------

                    else:

                        result_data = {

                            "status":
                                "NO_PHONE",

                            "phones":
                                [],

                            "count":
                                0,

                            "confidence":
                                0.0,

                            "timestamp":
                                now,

                            "inference_ms":
                                round(
                                    inference_ms,
                                    2
                                )
                        }


                # ==================================================
                # SAVE RESULT
                # ==================================================

                with self.lock:

                    self.latest_result = (
                        result_data
                    )


            except Exception as e:

                print(
                    f"YOLO11s detection error: {e}"
                )


                time.sleep(
                    0.05
                )


            # ==================================================
            # CONTROL INFERENCE RATE
            # ==================================================

            time.sleep(
                self.inference_interval
            )


    # ======================================================
    # OPTIONAL DRAW
    # ======================================================

    def draw(
        self,
        frame,
        result
    ):

        """
        Optional debugging visualization.

        IMPORTANT:
        Do NOT use this method in the real
        examination UI.

        The production examination video
        should remain clean.
        """

        if frame is None:

            return frame


        if not isinstance(
            result,
            dict
        ):

            return frame


        if (
            result.get("status")
            != "PHONE_DETECTED"
        ):

            return frame


        phones = result.get(
            "phones",
            []
        )


        for phone in phones:

            bbox = phone.get(
                "bbox"
            )


            if (
                bbox is None
                or
                len(bbox) != 4
            ):

                continue


            x1, y1, x2, y2 = bbox


            confidence = phone.get(
                "confidence",
                0.0
            )


            # ------------------------------------------
            # Debug bounding box
            # ------------------------------------------

            cv2.rectangle(

                frame,

                (x1, y1),

                (x2, y2),

                (0, 0, 255),

                2
            )


            cv2.putText(

                frame,

                f"Phone {confidence:.2f}",

                (
                    x1,
                    max(
                        y1 - 10,
                        20
                    )
                ),

                cv2.FONT_HERSHEY_SIMPLEX,

                0.6,

                (0, 0, 255),

                2
            )


        return frame


    # ======================================================
    # STOP
    # ======================================================

    def stop(self):

        self.running = False


        if self.thread.is_alive():

            self.thread.join(
                timeout=2
            )

