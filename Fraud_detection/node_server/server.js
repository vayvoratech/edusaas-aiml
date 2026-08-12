const express = require("express");
const http = require("http");
const WebSocket = require("ws");
const path = require("path");

const app = express();

const PORT = 3000;

const PYTHON_WS_URL =
    "ws://localhost:8000/ws/proctor";


// ======================================================
// STATIC FILES
// ======================================================

app.use(
    express.static(__dirname)
);


// ======================================================
// HTTP SERVER
// ======================================================

const server =
    http.createServer(app);


// ======================================================
// BROWSER WEBSOCKET SERVER
// ======================================================

const wss =
    new WebSocket.Server({
        server: server,
        path: "/ws/proctor"
    });


// ======================================================
// BROWSER CONNECTION
// ======================================================

wss.on(
    "connection",
    function (
        browserSocket,
        request
    ) {

        console.log(
            "Browser WebSocket connected."
        );


        let pythonSocket =
            null;


        let pythonConnected =
            false;


        // ==================================================
        // CONNECT NODE → PYTHON
        // ==================================================

        console.log(
            "Connecting to Python:",
            PYTHON_WS_URL
        );


        pythonSocket =
            new WebSocket(
                PYTHON_WS_URL
            );


        // ==================================================
        // PYTHON CONNECTED
        // ==================================================

        pythonSocket.on(
            "open",
            function () {

                pythonConnected =
                    true;


                console.log(
                    "Node → Python WebSocket connected."
                );


                if (
                    browserSocket.readyState ===
                    WebSocket.OPEN
                ) {

                    browserSocket.send(

                        JSON.stringify({

                            type:
                                "NODE_CONNECTED",

                            message:
                                "Node connected to Python AI service."

                        })

                    );
                }

            }
        );


        // ==================================================
        // BROWSER → NODE → PYTHON
        // ==================================================

        browserSocket.on(
            "message",
            function (
                message,
                isBinary
            ) {

                if (
                    !pythonSocket
                ) {

                    console.warn(
                        "Python socket does not exist."
                    );

                    return;
                }


                if (
                    pythonSocket.readyState !==
                    WebSocket.OPEN
                ) {

                    console.warn(
                        "Python WebSocket is not connected."
                    );

                    return;
                }


                try {

                    /*
                     * Forward exactly what browser sent.
                     */

                    pythonSocket.send(
                        message,
                        {
                            binary: isBinary
                        }
                    );

                }
                catch (error) {

                    console.error(
                        "Browser → Python forwarding error:",
                        error
                    );
                }

            }
        );


        // ==================================================
        // PYTHON → NODE → BROWSER
        // ==================================================

        pythonSocket.on(
            "message",
            function (
                message,
                isBinary
            ) {

                if (
                    browserSocket.readyState !==
                    WebSocket.OPEN
                ) {

                    return;
                }


                try {

                    /*
                     * Forward AI result directly
                     * back to browser.
                     */

                    browserSocket.send(
                        message,
                        {
                            binary: isBinary
                        }
                    );

                }
                catch (error) {

                    console.error(
                        "Python → Browser forwarding error:",
                        error
                    );
                }

            }
        );


        // ==================================================
        // PYTHON ERROR
        // ==================================================

        pythonSocket.on(
            "error",
            function (
                error
            ) {

                console.error(
                    "Node → Python WebSocket error:",
                    error
                );


                if (
                    browserSocket.readyState ===
                    WebSocket.OPEN
                ) {

                    browserSocket.send(

                        JSON.stringify({

                            type:
                                "PYTHON_CONNECTION_ERROR",

                            message:
                                "Python AI service unavailable."

                        })

                    );
                }

            }
        );


        // ==================================================
        // PYTHON CLOSED
        // ==================================================

        pythonSocket.on(
            "close",
            function () {

                pythonConnected =
                    false;


                console.log(
                    "Node → Python WebSocket closed."
                );


                if (
                    browserSocket.readyState ===
                    WebSocket.OPEN
                ) {

                    browserSocket.send(

                        JSON.stringify({

                            type:
                                "PYTHON_DISCONNECTED",

                            message:
                                "Python AI service disconnected."

                        })

                    );
                }

            }
        );


        // ==================================================
        // BROWSER CLOSED
        // ==================================================

        browserSocket.on(
            "close",
            function () {

                console.log(
                    "Browser WebSocket disconnected."
                );


                if (
                    pythonSocket
                ) {

                    try {

                        if (
                            pythonSocket.readyState ===
                            WebSocket.OPEN
                        ) {

                            pythonSocket.send(

                                JSON.stringify({

                                    type:
                                        "STOP_EXAM"

                                })

                            );
                        }

                    }
                    catch (error) {

                        console.warn(
                            "Could not send STOP_EXAM:",
                            error
                        );
                    }


                    try {

                        pythonSocket.close();

                    }
                    catch (error) {

                        console.warn(
                            "Python socket close error:",
                            error
                        );
                    }

                }

            }
        );

    }
);


// ======================================================
// SERVER
// ======================================================

server.listen(
    PORT,
    function () {

        console.log("");
        console.log(
            "======================================"
        );

        console.log(
            "EduSaaS Node Proctoring Gateway"
        );

        console.log(
            "======================================"
        );

        console.log(
            `HTTP Server: http://localhost:${PORT}`
        );

        console.log(
            `WebSocket: ws://localhost:${PORT}/ws/proctor`
        );

        console.log(
            `Python AI: ${PYTHON_WS_URL}`
        );

        console.log(
            "======================================"
        );

    }
);