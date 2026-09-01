const express = require("express");
const { runStudentCode, submitCode, startAssessment ,completeAssessment} = require("../controllers/codeController");

const router = express.Router();

router.post("/run", runStudentCode);
router.post("/submit", submitCode);
router.post("/assessment/start", startAssessment); 
router.post("/complete-assessment", completeAssessment);

module.exports = router;