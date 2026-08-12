const skillGapService = require("./services/skillGapPythonService");

async function test() {

    const result = await skillGapService.analyzeGap({

        student_skills: [

            {
                skill_id: 1,
                skill_name: "Python",
                skill_level: 3
            },

            {
                skill_id: 2,
                skill_name: "SQL",
                skill_level: 2
            }

        ],

        required_skills: [

            {
                skill_id: 1,
                skill_name: "Python",
                required_level: 5
            },

            {
                skill_id: 2,
                skill_name: "SQL",
                required_level: 3
            }

        ]

    });

    console.log(JSON.stringify(result, null, 2));

}

test();