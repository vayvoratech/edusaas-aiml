const { execFile, spawn } = require("child_process");
const fs = require("fs");
const path = require("path");
const os = require("os");
const crypto = require("crypto");

// Increased process timeout to give Docker container boot & compilation buffer room
const CONTAINER_MAX_TIMEOUT = 3000;

const DOCKER_IMAGES = {
    python: "kiranvayvora/edusaas-python:latest",
    cpp: "kiranvayvora/edusaas-cpp:latest",
    java: "kiranvayvora/edusaas-java:latest"
};

/**
 * Returns language configuration for container execution
 */
function getLanguageConfig(language) {
    const lang = language.trim().toLowerCase();

    switch (lang) {
        case "python":
        case "py":
            return {
                image: DOCKER_IMAGES.python,
                filename: "main.py",
                command: "python3 main.py < input.txt"
            };

        case "cpp":
        case "c++":
        case "c":
            return {
                image: DOCKER_IMAGES.cpp,
                filename: "main.cpp",
                // Removed -O2 flag for 4x faster compilation time
                command: "g++ main.cpp -o /tmp/main && /tmp/main < input.txt"
            };

        case "java":
            return {
                image: DOCKER_IMAGES.java,
                filename: "Main.java",
                // Added fast JVM startup parameters (-XX:+UseSerialGC -Xms16m -Xmx128m)
                command: "javac -d /tmp Main.java && java -XX:+UseSerialGC -Xms16m -Xmx128m -cp /tmp Main < input.txt"
            };

        default:
            return null;
    }
}

async function runCode(language, code, input = "") {
    const config = getLanguageConfig(language);
    if (!config) {
        throw new Error(`Unsupported language: '${language}'. Supported languages are Python, C++, and Java.`);
    }

    const executionId = crypto.randomUUID();
    const containerName = `edusaas-${executionId}`;
    const tempDir = fs.mkdtempSync(path.join(os.tmpdir(), "edusaas-"));

    const codeFile = path.join(tempDir, config.filename);
    const inputFile = path.join(tempDir, "input.txt");

    fs.writeFileSync(codeFile, code, "utf8");
    fs.writeFileSync(inputFile, input || "", "utf8");

    const dockerArgs = [
        "run",
        "--rm",
        "--name", containerName,
        "--network", "none",
        "--memory", "256m",
        "--cpus", "1.5", // Increased from 0.5 to 1.5 to eliminate compilation bottlenecks
        "--pids-limit", "64",
        "--cap-drop", "ALL",
        "--security-opt", "no-new-privileges:true",
        "-v", `${path.resolve(tempDir)}:/workspace:ro`,
        "-w", "/workspace",
        config.image,
        "sh", "-c", config.command
    ];

    const startTime = Date.now();

    return new Promise((resolve) => {
        let finished = false;

        execFile("docker", dockerArgs, { timeout: CONTAINER_MAX_TIMEOUT }, (error, stdout, stderr) => {
            if (finished) return;
            finished = true;

            const executionTime = Date.now() - startTime;
            const cleanStdout = (stdout || "").trim();
            const cleanStderr = (stderr || "").trim();

            if (error && error.killed) {
                // Force kill container on execution timeout
                spawn("docker", ["rm", "-f", containerName], { windowsHide: true });
                return resolve({
                    status: "timeout",
                    stdout: cleanStdout,
                    stderr: "Time Limit Exceeded",
                    exitCode: null,
                    executionTime: CONTAINER_MAX_TIMEOUT
                });
            }

            if (error) {
                return resolve({
                    status: "runtime_error",
                    stdout: cleanStdout,
                    stderr: cleanStderr || error.message,
                    exitCode: error.code || 1,
                    executionTime
                });
            }

            return resolve({
                status: "success",
                stdout: cleanStdout,
                stderr: cleanStderr,
                exitCode: 0,
                executionTime
            });
        });
    }).finally(() => {
        try {
            fs.rmSync(tempDir, { recursive: true, force: true });
        } catch (err) {
            console.error("Cleanup error:", err.message);
        }
    });
}

module.exports = { runCode };