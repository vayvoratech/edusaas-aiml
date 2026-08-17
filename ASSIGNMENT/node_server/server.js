require("dotenv").config();
const express = require("express");
const { exec } = require("child_process");
const codeRoutes = require("./routes/codeRoutes");
const pool = require("./config/db");

const app = express();
app.use(express.json({ limit: "1mb" }));

// =========================================================
// Docker Warm-Up Service (Prevents First-Run Cold-Start TLE)
// =========================================================
function warmupDockerImages() {
    console.log("⚡ Warming up Docker containers...");

    // Runs a lightweight command to ensure the base Docker image is cached in memory
    const warmupCmd = 'docker run --rm python:3.10-slim python3 -c "print(\'Docker Engine Ready\')"';

    exec(warmupCmd, (error, stdout) => {
        if (error) {
            console.warn("⚠️ Docker warmup warning (Image downloading or Docker not running):", error.message);
        } else {
            console.log(`✅ ${stdout.trim()}`);
        }
    });
}

// =========================================================
// Health Check & System Routes
// =========================================================
app.get("/", (req, res) => {
    res.json({ service: "EduSaaS Code Execution API", status: "running" });
});

app.get("/health", async (req, res) => {
    try {
        await pool.query("SELECT 1");
        res.json({ status: "healthy", database: "connected" });
    } catch (err) {
        res.status(500).json({ status: "unhealthy", database: "disconnected", error: err.message });
    }
});

// API Routes
app.use("/api/code", codeRoutes);

// Server Listener
const PORT = process.env.COMPILER_PORT || 6000;
app.listen(PORT, () => {
    console.log(`EduSaaS Compiler Server running on port ${PORT}`);
    warmupDockerImages(); // Executes container warm-up on server boot
});