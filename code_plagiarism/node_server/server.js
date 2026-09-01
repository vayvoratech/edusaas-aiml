const express = require("express");
const cors = require("cors");
require("dotenv").config();

const finalSubmissionRoutes = require("./routes/finalSubmissionRoutes");

const app = express();

const PORT = process.env.PORT || 8080;


// =====================================================
// MIDDLEWARE
// =====================================================

app.use(cors());

app.use(
    express.json({
        limit: "5mb"
    })
);


// =====================================================
// HEALTH CHECK
// =====================================================

app.get("/health", (req, res) => {

    res.status(200).json({
        success: true,
        message: "Node.js server is running"
    });

});


// =====================================================
// FINAL SUBMISSION ROUTES
// =====================================================

app.use(
    "/api/submissions",
    finalSubmissionRoutes
);


// =====================================================
// 404 HANDLER
// =====================================================

app.use((req, res) => {

    res.status(404).json({
        success: false,
        message: "Route not found"
    });

});


// =====================================================
// GLOBAL ERROR HANDLER
// =====================================================

app.use((err, req, res, next) => {

    console.error("Server error:", err);

    res.status(500).json({
        success: false,
        message: "Internal server error"
    });

});


// =====================================================
// START SERVER
// =====================================================

app.listen(PORT, () => {

    console.log(
        `Node.js server running on http://localhost:${PORT}`
    );

});