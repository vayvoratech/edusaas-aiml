const axios = require('axios');

const FASTAPI_URL = process.env.FASTAPI_URL || 'http://localhost:8000';

class SkillDemandService {
    async fetchSkillList() {
        try {
            const response = await axios.get(`${FASTAPI_URL}/skills`, { timeout: 4000 });
            return response.data.skills || [];
        } catch (error) {
            console.error('[SkillDemandService] Fetch skills error:', error.message);
            throw new Error(error.response?.data?.detail || 'Failed to connect to FastAPI ML engine.');
        }
    }

    async getPrediction(skill, periods = 6) {
        try {
            const response = await axios.get(`${FASTAPI_URL}/predict/${encodeURIComponent(skill)}`, {
                params: { periods },
                timeout: 10000
            });
            return response.data;
        } catch (error) {
            console.error(`[SkillDemandService] Prediction error for ${skill}:`, error.message);
            throw new Error(error.response?.data?.detail || 'FastAPI Prediction Engine failed.');
        }
    }
}

module.exports = new SkillDemandService();