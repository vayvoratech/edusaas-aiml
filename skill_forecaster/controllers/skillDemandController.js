const skillDemandService = require('../services/skillDemandService');

class SkillDemandController {
    async getSkills(req, res) {
        try {
            const skills = await skillDemandService.fetchSkillList();
            return res.status(200).json({ success: true, count: skills.length, skills });
        } catch (error) {
            return res.status(500).json({ success: false, error: error.message });
        }
    }

    async predictSingleSkill(req, res) {
        try {
            const { skill, periods = 6 } = req.body;

            if (!skill || typeof skill !== 'string') {
                return res.status(400).json({
                    success: false,
                    error: 'Field "skill" is required and must be a string.'
                });
            }

            const horizon = Math.min(Math.max(parseInt(periods, 10) || 6, 1), 24);
            const predictionData = await skillDemandService.getPrediction(skill.trim(), horizon);

            return res.status(200).json({
                success: true,
                data: predictionData
            });
        } catch (error) {
            const statusCode = error.message.includes('not recognized') ? 404 : 500;
            return res.status(statusCode).json({
                success: false,
                error: error.message
            });
        }
    }

    async predictBatchSkills(req, res) {
        try {
            const { skills, periods = 6 } = req.body;

            if (!skills || !Array.isArray(skills) || skills.length === 0) {
                return res.status(400).json({
                    success: false,
                    error: 'Field "skills" must be a non-empty array of skill strings.'
                });
            }

            const horizon = Math.min(Math.max(parseInt(periods, 10) || 6, 1), 24);

            const settled = await Promise.allSettled(
                skills.map(s => skillDemandService.getPrediction(s.trim(), horizon))
            );

            const results = settled.map((result, idx) => {
                if (result.status === 'fulfilled') {
                    return result.value;
                }
                return {
                    skill: skills[idx],
                    error: result.reason.message
                };
            });

            return res.status(200).json({
                success: true,
                periods: horizon,
                results
            });
        } catch (error) {
            return res.status(500).json({
                success: false,
                error: error.message
            });
        }
    }
}

module.exports = new SkillDemandController();