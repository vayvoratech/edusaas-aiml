const express = require("express");

const router = express.Router();

const skillGapController = require("../controllers/skillGapController");

// -----------------------------------------------------
// Analyze Skill Gap
// -----------------------------------------------------
router.post(

    "/analyze",

    skillGapController.analyzeSkillGap

);

module.exports = router;