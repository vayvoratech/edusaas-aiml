const express = require("express");

const router = express.Router();

const quizController = require("../controllers/quizController");

router.post(
    "/start",
    quizController.startAssessment
);
router.post(
    "/submit-answer",
    quizController.submitAnswer
);
router.post(
    "/finish",
     quizController.finishAssessment);
module.exports = router;