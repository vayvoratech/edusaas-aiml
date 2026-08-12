const axios = require("axios");
require("dotenv").config();

const SKILL_GAP_SERVICE = process.env.SKILL_GAP_SERVICE;

class SkillGapPythonService {

    async analyzeGap(data) {

        const response = await axios.post(

            `${SKILL_GAP_SERVICE}/analyze`,

            data

        );

        return response.data;

    }

}

module.exports = new SkillGapPythonService();