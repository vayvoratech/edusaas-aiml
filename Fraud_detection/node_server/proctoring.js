class Proctoring {

    constructor(options = {}) {

        this.wsUrl =
            options.wsUrl ||
            "ws://localhost:8000/ws/proctor";

        this.frameRate =
            options.frameRate || 5;

        this.cameraWidth =
            options.cameraWidth || 640;

        this.cameraHeight =
            options.cameraHeight || 480;

        this.jpegQuality =
            options.jpegQuality || 0.65;

        this.running = false;
        this.connected = false;
        this.terminated = false;

        this.websocket = null;
        this.stream = null;

        /*
         * IMPORTANT:
         * Use the video element already present
         * in proctoring_test.html.
         */
        this.video = null;

        this.canvas = null;
        this.context = null;

        this.frameInterval = null;

        // ==================================================
        // FRAUD STATE
        // ==================================================

        this.lastAction = "NORMAL";
        this.lastSeverity = "LOW";

        this.violationCount = 0;

        // ==================================================
        // PAUSE STATE
        // ==================================================

        this.examPaused = false;

        this.pauseTimer = null;

        this.pauseOverlay = null;

        this.pauseCountdownElement = null;

        this.pauseMessageElement = null;

        // ==================================================
        // BROWSER MONITORING
        // ==================================================

        this.browserMonitoring = false;

        this.browserEventCooldown = 1500;

        this.lastBrowserEventTime = {};

        this.boundEvents = [];

        // ==================================================
        // CALLBACKS
        // ==================================================

        this.onConnected =
            options.onConnected ||
            function () {};

        this.onDisconnected =
            options.onDisconnected ||
            function () {};

        this.onResult =
            options.onResult ||
            function () {};

        this.onWarning =
            options.onWarning ||
            function () {};

        this.onPause =
            options.onPause ||
            function () {};

        this.onTerminate =
            options.onTerminate ||
            function () {};

        this.onError =
            options.onError ||
            function () {};
    }


    // ======================================================
    // START
    // ======================================================

    async start() {

        if (this.running) {

            console.warn(
                "Proctoring is already running."
            );

            return;
        }

        try {

            this.terminated = false;
            this.examPaused = false;

            // ----------------------------------------------
            // FIND EXISTING VIDEO ELEMENT
            // ----------------------------------------------

            this.video =
                document.getElementById(
                    "cameraVideo"
                );

            if (!this.video) {

                throw new Error(
                    "Video element not found. " +
                    'Add <video id="cameraVideo" autoplay muted playsinline></video> to proctoring_test.html.'
                );
            }

            console.log(
                "Camera video element found."
            );

            // ----------------------------------------------
            // CAMERA
            // ----------------------------------------------

            this.stream =
                await navigator
                    .mediaDevices
                    .getUserMedia({

                        video: {

                            width: {
                                ideal:
                                    this.cameraWidth
                            },

                            height: {
                                ideal:
                                    this.cameraHeight
                            },

                            facingMode:
                                "user"

                        },

                        audio: false
                    });

            // ----------------------------------------------
            // CONNECT CAMERA TO EXISTING VIDEO
            // ----------------------------------------------

            this.video.srcObject =
                this.stream;

            this.video.autoplay =
                true;

            this.video.muted =
                true;

            this.video.playsInline =
                true;

            await this.video.play();

            console.log(
                "Camera started successfully."
            );

            // ----------------------------------------------
            // CANVAS
            // ----------------------------------------------

            this.canvas =
                document.createElement(
                    "canvas"
                );

            this.canvas.width =
                this.cameraWidth;

            this.canvas.height =
                this.cameraHeight;

            this.context =
                this.canvas.getContext(
                    "2d"
                );

            if (!this.context) {

                throw new Error(
                    "Could not create canvas context."
                );
            }

            // ----------------------------------------------
            // WEBSOCKET
            // ----------------------------------------------

            await this.connectWebSocket();

            // ----------------------------------------------
            // RUNNING
            // ----------------------------------------------

            this.running =
                true;

            // ----------------------------------------------
            // BROWSER EVENTS
            // ----------------------------------------------

            this.enableBrowserMonitoring();

            // ----------------------------------------------
            // FRAME LOOP
            // ----------------------------------------------

            this.startFrameSending();

            console.log(
                "AI Proctoring started."
            );

        }
        catch (error) {

            console.error(
                "Proctoring start error:",
                error
            );

            await this.cleanup();

            this.onError(
                error
            );

            throw error;
        }
    }


    // ======================================================
    // WEBSOCKET
    // ======================================================

    connectWebSocket() {

        return new Promise(
            (resolve, reject) => {

                let settled = false;

                try {

                    console.log(
                        "Connecting to:",
                        this.wsUrl
                    );

                    this.websocket =
                        new WebSocket(
                            this.wsUrl
                        );


                    // --------------------------------------
                    // OPEN
                    // --------------------------------------

                    this.websocket.onopen =
                        () => {

                            console.log(
                                "Python AI WebSocket connected."
                            );

                            this.connected =
                                true;

                            this.websocket.send(

                                JSON.stringify({

                                    type:
                                        "START_EXAM"

                                })

                            );

                            this.onConnected();

                            if (!settled) {

                                settled =
                                    true;

                                resolve();
                            }
                        };


                    // --------------------------------------
                    // MESSAGE
                    // --------------------------------------

                    this.websocket.onmessage =
                        async (
                            event
                        ) => {

                            await this.handleMessage(
                                event.data
                            );
                        };


                    // --------------------------------------
                    // ERROR
                    // --------------------------------------

                    this.websocket.onerror =
                        (
                            error
                        ) => {

                            console.error(
                                "WebSocket error:",
                                error
                            );

                            this.onError(
                                error
                            );

                            if (!settled) {

                                settled =
                                    true;

                                reject(
                                    new Error(
                                        "Unable to connect to Python AI WebSocket at " +
                                        this.wsUrl
                                    )
                                );
                            }
                        };


                    // --------------------------------------
                    // CLOSE
                    // --------------------------------------

                    this.websocket.onclose =
                        (
                            event
                        ) => {

                            console.log(
                                "Python AI WebSocket disconnected.",
                                event.code,
                                event.reason
                            );

                            this.connected =
                                false;

                            this.running =
                                false;

                            this.cancelPause();

                            this.onDisconnected();
                        };

                }
                catch (error) {

                    if (!settled) {

                        settled =
                            true;

                        reject(
                            error
                        );
                    }
                }

            }
        );
    }


    // ======================================================
    // HANDLE MESSAGE
    // ======================================================

    async handleMessage(
        rawData
    ) {

        let data =
            null;

        try {

            if (
                typeof rawData ===
                "string"
            ) {

                data =
                    JSON.parse(
                        rawData
                    );

            }

            else if (
                rawData instanceof Blob
            ) {

                const text =
                    await rawData.text();

                data =
                    JSON.parse(
                        text
                    );

            }

            else if (
                rawData instanceof ArrayBuffer
            ) {

                const text =
                    new TextDecoder().decode(
                        rawData
                    );

                data =
                    JSON.parse(
                        text
                    );

            }

            else {

                data =
                    rawData;
            }

        }
        catch (error) {

            console.error(
                "Could not parse AI result:",
                error
            );

            return;
        }


        if (!data) {

            return;
        }


        console.log(
            "AI MESSAGE:",
            data
        );


        // ==================================================
        // DIRECT TERMINATION
        // ==================================================

        if (
            data.type ===
            "EXAM_TERMINATED"
        ) {

            this.terminated =
                true;

            this.running =
                false;

            this.cancelPause();

            this.onTerminate(
                data
            );

            return;
        }


        // ==================================================
        // PROCTORING RESULT
        // ==================================================

        if (
            data.type ===
            "PROCTORING_RESULT"
        ) {

            this.processResult(
                data
            );

            this.onResult(
                data
            );

            return;
        }


        // ==================================================
        // FRAUD OBJECT WITHOUT TYPE
        // ==================================================

        if (
            data.fraud
        ) {

            this.processResult(
                data
            );

            this.onResult(
                data
            );
        }
    }


    // ======================================================
    // PROCESS AI RESULT
    // ======================================================

    processResult(
        data
    ) {

        const fraud =
            data &&
            typeof data.fraud ===
                "object" &&
            data.fraud !== null

                ? data.fraud

                : (
                    data &&
                    typeof data ===
                        "object"

                        ? data

                        : {}
                );


        const action =
            fraud.action ||
            "NORMAL";


        const severity =
            fraud.severity ||
            "LOW";


        this.lastAction =
            action;


        this.lastSeverity =
            severity;


        if (
            fraud.violation_count !==
            undefined
        ) {

            this.violationCount =
                Number(
                    fraud.violation_count
                ) || 0;
        }


        // ==================================================
        // NORMAL
        // ==================================================

        if (
            action ===
            "NORMAL"
        ) {

            return;
        }


        // ==================================================
        // FIRST VIOLATION
        // ==================================================

        if (
            action ===
            "WARNING"
        ) {

            this.onWarning(
                data
            );


            const pauseRequested =
                fraud.pause_exam !==
                false;


            if (
                pauseRequested
            ) {

                this.pauseExam(

                    Number(
                        fraud.pause_duration
                    ) || 10,

                    fraud.violation_type ||
                    "PROCTORING_VIOLATION",

                    fraud.message ||
                    "Proctoring violation detected."

                );
            }


            return;
        }


        // ==================================================
        // PAUSE
        // ==================================================

        if (
            action ===
            "PAUSE_EXAM"
        ) {

            this.onPause(
                data
            );


            this.pauseExam(

                Number(
                    fraud.pause_duration
                ) || 10,

                fraud.violation_type ||
                "PROCTORING_VIOLATION",

                fraud.message ||
                "Examination paused due to a proctoring violation."

            );


            return;
        }


        // ==================================================
        // SECOND VIOLATION
        // ==================================================

        if (
            action ===
            "TERMINATE_EXAM"
        ) {

            this.terminated =
                true;

            this.running =
                false;

            this.cancelPause();

            this.onTerminate(
                data
            );


            return;
        }
    }


    // ======================================================
    // CREATE PAUSE OVERLAY
    // ======================================================

    createPauseOverlay() {

        if (
            this.pauseOverlay
        ) {

            return;
        }


        const overlay =
            document.createElement(
                "div"
            );


        overlay.id =
            "edusaasProctorPauseOverlay";


        overlay.innerHTML = `

            <div
                id="edusaasProctorPauseCard"
            >

                <div
                    id="edusaasProctorPauseTitle"
                >
                    EXAM PAUSED
                </div>


                <div
                    id="edusaasProctorPauseCountdown"
                >
                    10
                </div>


                <div
                    id="edusaasProctorPauseMessage"
                >
                    Please follow the examination rules.
                </div>

            </div>

        `;


        const style =
            document.createElement(
                "style"
            );


        style.id =
            "edusaasProctorPauseStyle";


        style.textContent = `

            #edusaasProctorPauseOverlay {

                position: fixed;

                inset: 0;

                width: 100vw;

                height: 100vh;

                display: none;

                align-items: center;

                justify-content: center;

                z-index: 2147483647;

                background:
                    rgba(
                        0,
                        0,
                        0,
                        0.72
                    );

                backdrop-filter:
                    blur(16px);

                -webkit-backdrop-filter:
                    blur(16px);

                color:
                    #ffffff;

                text-align:
                    center;

                user-select:
                    none;

                -webkit-user-select:
                    none;

                pointer-events:
                    all;

                cursor:
                    not-allowed;
            }


            #edusaasProctorPauseOverlay.active {

                display:
                    flex;
            }


            #edusaasProctorPauseCard {

                width:
                    min(
                        90vw,
                        700px
                    );

                text-align:
                    center;

                font-family:
                    Arial,
                    Helvetica,
                    sans-serif;
            }


            #edusaasProctorPauseTitle {

                font-size:
                    36px;

                font-weight:
                    700;

                letter-spacing:
                    2px;

                margin-bottom:
                    10px;
            }


            #edusaasProctorPauseCountdown {

                font-size:
                    clamp(
                        100px,
                        18vw,
                        190px
                    );

                line-height:
                    1;

                font-weight:
                    800;

                margin:
                    15px 0 25px;
            }


            #edusaasProctorPauseMessage {

                font-size:
                    18px;

                line-height:
                    1.5;

                opacity:
                    0.95;
            }

        `;


        if (
            !document.getElementById(
                "edusaasProctorPauseStyle"
            )
        ) {

            document.head.appendChild(
                style
            );
        }


        document.body.appendChild(
            overlay
        );


        this.pauseOverlay =
            overlay;


        this.pauseCountdownElement =
            document.getElementById(
                "edusaasProctorPauseCountdown"
            );


        this.pauseMessageElement =
            document.getElementById(
                "edusaasProctorPauseMessage"
            );
    }


    // ======================================================
    // PAUSE EXAM
    // ======================================================

    pauseExam(

        duration = 10,

        violationType = null,

        message = null

    ) {

        if (
            !this.running
        ) {

            return;
        }


        if (
            this.terminated
        ) {

            return;
        }


        if (
            this.examPaused
        ) {

            return;
        }


        this.createPauseOverlay();


        this.examPaused =
            true;


        const seconds =
            Math.max(
                1,
                Number(
                    duration
                ) || 10
            );


        if (
            this.pauseMessageElement
        ) {

            this.pauseMessageElement.textContent =

                message ||

                (
                    violationType

                        ? `Violation detected: ${violationType}`

                        : "Please follow the examination rules."
                );
        }


        this.pauseOverlay.classList.add(
            "active"
        );


        let remaining =
            seconds;


        if (
            this.pauseCountdownElement
        ) {

            this.pauseCountdownElement.textContent =
                remaining;
        }


        this.onPause({

            type:
                "EXAM_PAUSED",

            violation_type:
                violationType,

            pause_duration:
                seconds,

            countdown:
                remaining,

            message:
                message ||
                "Examination paused."

        });


        if (
            this.pauseTimer
        ) {

            clearInterval(
                this.pauseTimer
            );
        }


        this.pauseTimer =
            setInterval(
                () => {

                    if (
                        !this.examPaused
                    ) {

                        clearInterval(
                            this.pauseTimer
                        );

                        this.pauseTimer =
                            null;

                        return;
                    }


                    remaining--;


                    if (
                        this.pauseCountdownElement
                    ) {

                        this.pauseCountdownElement.textContent =
                            Math.max(
                                0,
                                remaining
                            );
                    }


                    if (
                        remaining <= 0
                    ) {

                        clearInterval(
                            this.pauseTimer
                        );

                        this.pauseTimer =
                            null;

                        this.resumeExam();
                    }

                },
                1000
            );
    }


    // ======================================================
    // RESUME
    // ======================================================

    resumeExam() {

        if (
            !this.examPaused
        ) {

            return;
        }


        this.examPaused =
            false;


        if (
            this.pauseTimer
        ) {

            clearInterval(
                this.pauseTimer
            );

            this.pauseTimer =
                null;
        }


        if (
            this.pauseOverlay
        ) {

            this.pauseOverlay.classList.remove(
                "active"
            );
        }


        this.onPause({

            type:
                "EXAM_RESUMED"

        });


        console.log(
            "Examination resumed."
        );
    }


    // ======================================================
    // CANCEL PAUSE
    // ======================================================

    cancelPause() {

        this.examPaused =
            false;


        if (
            this.pauseTimer
        ) {

            clearInterval(
                this.pauseTimer
            );

            this.pauseTimer =
                null;
        }


        if (
            this.pauseOverlay
        ) {

            this.pauseOverlay.classList.remove(
                "active"
            );
        }
    }


    // ======================================================
    // FRAME SENDING
    // ======================================================

    startFrameSending() {

        if (
            this.frameInterval
        ) {

            clearInterval(
                this.frameInterval
            );
        }


        const interval =
            1000 /
            this.frameRate;


        this.frameInterval =
            setInterval(
                () => {

                    if (
                        !this.running
                    ) {

                        return;
                    }


                    if (
                        !this.connected
                    ) {

                        return;
                    }


                    if (
                        this.terminated
                    ) {

                        return;
                    }


                    this.sendFrame();

                },
                interval
            );
    }


    // ======================================================
    // SEND FRAME
    // ======================================================

    sendFrame() {

        if (
            !this.websocket ||
            this.websocket.readyState !==
                WebSocket.OPEN
        ) {

            return;
        }


        if (
            !this.video ||
            !this.canvas ||
            !this.context
        ) {

            return;
        }


        if (
            this.video.readyState <
            HTMLMediaElement.HAVE_CURRENT_DATA
        ) {

            return;
        }


        try {

            this.context.drawImage(

                this.video,

                0,
                0,

                this.canvas.width,
                this.canvas.height

            );


            const imageData =
                this.canvas.toDataURL(
                    "image/jpeg",
                    this.jpegQuality
                );


            this.websocket.send(

                JSON.stringify({

                    type:
                        "VIDEO_FRAME",

                    frame:
                        imageData

                })

            );

        }
        catch (error) {

            console.error(
                "Frame sending error:",
                error
            );
        }
    }


    // ======================================================
    // BROWSER MONITORING
    // ======================================================

    enableBrowserMonitoring() {

        if (
            this.browserMonitoring
        ) {

            return;
        }


        this.browserMonitoring =
            true;


        // ----------------------------------------------
        // TAB SWITCH
        // ----------------------------------------------

        this.addBrowserEvent(

            document,

            "visibilitychange",

            () => {

                if (
                    !document.hidden
                ) {

                    return;
                }


                this.reportBrowserViolation(

                    "TAB_SWITCH",

                    {
                        reason:
                            "document_hidden"
                    }

                );
            }

        );


        // ----------------------------------------------
        // WINDOW BLUR
        // ----------------------------------------------

        this.addBrowserEvent(

            window,

            "blur",

            () => {

                this.reportBrowserViolation(

                    "WINDOW_BLUR",

                    {
                        reason:
                            "window_blur"
                    }

                );
            }

        );


        // ----------------------------------------------
        // COPY
        // ----------------------------------------------

        this.addBrowserEvent(

            document,

            "copy",

            event => {

                if (
                    !this.running
                ) {

                    return;
                }


                event.preventDefault();


                this.reportBrowserViolation(
                    "COPY_ATTEMPT"
                );
            }

        );


        // ----------------------------------------------
        // PASTE
        // ----------------------------------------------

        this.addBrowserEvent(

            document,

            "paste",

            event => {

                if (
                    !this.running
                ) {

                    return;
                }


                event.preventDefault();


                this.reportBrowserViolation(
                    "PASTE_ATTEMPT"
                );
            }

        );


        // ----------------------------------------------
        // CUT
        // ----------------------------------------------

        this.addBrowserEvent(

            document,

            "cut",

            event => {

                if (
                    !this.running
                ) {

                    return;
                }


                event.preventDefault();


                this.reportBrowserViolation(
                    "CUT_ATTEMPT"
                );
            }

        );


        // ----------------------------------------------
        // RIGHT CLICK
        // ----------------------------------------------

        this.addBrowserEvent(

            document,

            "contextmenu",

            event => {

                if (
                    !this.running
                ) {

                    return;
                }


                event.preventDefault();


                this.reportBrowserViolation(
                    "RIGHT_CLICK"
                );
            }

        );


        // ----------------------------------------------
        // FULLSCREEN EXIT
        // ----------------------------------------------

        this.addBrowserEvent(

            document,

            "fullscreenchange",

            () => {

                if (
                    !this.running
                ) {

                    return;
                }


                if (
                    !document.fullscreenElement
                ) {

                    this.reportBrowserViolation(
                        "FULLSCREEN_EXIT"
                    );
                }
            }

        );
    }


    // ======================================================
    // ADD BROWSER EVENT
    // ======================================================

    addBrowserEvent(
        target,
        eventName,
        handler
    ) {

        target.addEventListener(
            eventName,
            handler
        );


        this.boundEvents.push({

            target:
                target,

            eventName:
                eventName,

            handler:
                handler

        });
    }


    // ======================================================
    // REPORT BROWSER VIOLATION
    // ======================================================

    reportBrowserViolation(

        eventName,

        metadata = {}

    ) {

        if (
            !this.running
        ) {

            return;
        }


        if (
            this.terminated
        ) {

            return;
        }


        const now =
            Date.now();


        const relatedEvent =
            eventName ===
                "TAB_SWITCH" ||

            eventName ===
                "WINDOW_BLUR";


        const lastTime =
            this.lastBrowserEventTime[
                eventName
            ] || 0;


        const relatedLastTime =
            relatedEvent

                ? Math.max(

                    this.lastBrowserEventTime[
                        "TAB_SWITCH"
                    ] || 0,

                    this.lastBrowserEventTime[
                        "WINDOW_BLUR"
                    ] || 0

                )

                : lastTime;


        if (
            now -
            relatedLastTime
            <
            this.browserEventCooldown
        ) {

            return;
        }


        this.lastBrowserEventTime[
            eventName
        ] =
            now;


        console.warn(

            "Browser violation:",

            eventName

        );


        if (
            !this.websocket ||
            this.websocket.readyState !==
                WebSocket.OPEN
        ) {

            return;
        }


        try {

            this.websocket.send(

                JSON.stringify({

                    type:
                        "BROWSER_VIOLATION",

                    event:
                        eventName,

                    metadata:
                        metadata

                })

            );

        }
        catch (error) {

            console.error(
                "Browser violation send error:",
                error
            );
        }
    }


    // ======================================================
    // STOP
    // ======================================================

    async stop() {

        if (
            !this.running &&
            !this.websocket &&
            !this.stream
        ) {

            return;
        }


        console.log(
            "Stopping proctoring..."
        );


        this.running =
            false;


        this.cancelPause();


        // ----------------------------------------------
        // FRAME LOOP
        // ----------------------------------------------

        if (
            this.frameInterval
        ) {

            clearInterval(
                this.frameInterval
            );

            this.frameInterval =
                null;
        }


        // ----------------------------------------------
        // BROWSER EVENTS
        // ----------------------------------------------

        this.disableBrowserMonitoring();


        // ----------------------------------------------
        // SERVER
        // ----------------------------------------------

        if (
            this.websocket &&
            this.websocket.readyState ===
                WebSocket.OPEN
        ) {

            try {

                this.websocket.send(

                    JSON.stringify({

                        type:
                            "STOP_EXAM"

                    })

                );

            }
            catch (error) {

                console.warn(
                    "Could not send STOP_EXAM:",
                    error
                );
            }
        }


        // ----------------------------------------------
        // WEBSOCKET
        // ----------------------------------------------

        if (
            this.websocket
        ) {

            try {

                this.websocket.close();

            }
            catch (error) {

                console.warn(
                    "WebSocket close error:",
                    error
                );
            }

            this.websocket =
                null;
        }


        this.connected =
            false;


        // ----------------------------------------------
        // CAMERA
        // ----------------------------------------------

        if (
            this.stream
        ) {

            this.stream
                .getTracks()
                .forEach(
                    track => {

                        track.stop();

                    }
                );

            this.stream =
                null;
        }


        if (
            this.video
        ) {

            this.video.srcObject =
                null;
        }


        this.video =
            null;


        console.log(
            "Proctoring stopped."
        );
    }


    // ======================================================
    // CLEANUP
    // ======================================================

    async cleanup() {

        this.running =
            false;

        this.cancelPause();

        if (
            this.frameInterval
        ) {

            clearInterval(
                this.frameInterval
            );

            this.frameInterval =
                null;
        }


        this.disableBrowserMonitoring();


        if (
            this.websocket
        ) {

            try {

                if (
                    this.websocket.readyState ===
                    WebSocket.OPEN
                ) {

                    this.websocket.close();
                }

            }
            catch (error) {

                console.warn(
                    "WebSocket cleanup error:",
                    error
                );
            }

            this.websocket =
                null;
        }


        this.connected =
            false;


        if (
            this.stream
        ) {

            this.stream
                .getTracks()
                .forEach(
                    track => {
                        track.stop();
                    }
                );

            this.stream =
                null;
        }


        if (
            this.video
        ) {

            this.video.srcObject =
                null;
        }


        this.video =
            null;
    }


    // ======================================================
    // DISABLE BROWSER MONITORING
    // ======================================================

    disableBrowserMonitoring() {

        this.boundEvents.forEach(
            item => {

                try {

                    item.target.removeEventListener(

                        item.eventName,

                        item.handler

                    );

                }
                catch (error) {

                    console.warn(
                        "Could not remove browser event:",
                        error
                    );
                }

            }
        );


        this.boundEvents =
            [];


        this.browserMonitoring =
            false;
    }


    // ======================================================
    // STATUS
    // ======================================================

    isExamPaused() {

        return this.examPaused;
    }
}


// ==========================================================
// GLOBAL EXPORT
// ==========================================================

window.Proctoring =
    Proctoring;