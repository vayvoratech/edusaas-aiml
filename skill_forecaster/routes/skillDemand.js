const express = require('express');
const router = express.Router();
const skillDemandController = require('../controllers/skillDemandController');

// GET /api/skill-demand/skills
router.get('/skills', skillDemandController.getSkills);

// POST /api/skill-demand/predict
router.post('/predict', skillDemandController.predictSingleSkill);

// POST /api/skill-demand/batch
router.post('/batch', skillDemandController.predictBatchSkills);

module.exports = router;