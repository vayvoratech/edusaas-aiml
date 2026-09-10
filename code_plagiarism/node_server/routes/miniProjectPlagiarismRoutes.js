const express = require("express");

const {
    checkMiniProjectPlagiarismController,
    miniProjectPlagiarismHealth
} = require("../controllers/miniProjectPlagiarismController");


const router = express.Router();


// ============================================================
// POST /api/plagiarism/mini-project/check
// ============================================================

router.post(
    "/check",
    checkMiniProjectPlagiarismController
);


// ============================================================
// GET /api/plagiarism/mini-project/health
// ============================================================

router.get(
    "/health",
    miniProjectPlagiarismHealth
);


module.exports = router;