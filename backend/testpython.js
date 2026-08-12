const pythonService = require("./services/pythonService");

async function test() {

    const response = await pythonService.createState({

        session_id: 1,

        skill: {

            skill_id: 1,

            skill_name: "Python"

        }

    });

    console.log(response);

}

test();