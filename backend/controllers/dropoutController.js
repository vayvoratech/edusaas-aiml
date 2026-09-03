const dropoutDataService =
    require("../services/dropoutDataService");

const dropoutPythonService =
    require("../services/dropoutPythonService");


exports.predictDropout = async (
    req,
    res
) => {

    try {

        const { student_id } = req.body;


        // -----------------------------------------
        // Validate student ID
        // -----------------------------------------

        if (!student_id) {

            return res.status(400).json({

                success: false,

                message:
                    "student_id is required."

            });
        }


        // -----------------------------------------
        // Node → PostgreSQL
        // -----------------------------------------

        const studentData =
            await dropoutDataService
                .getDropoutData(
                    student_id
                );


        // -----------------------------------------
        // Node → Python → ML Model
        // -----------------------------------------

        const result =
            await dropoutPythonService
                .predictDropout(
                    studentData
                );


        // -----------------------------------------
        // Response
        // -----------------------------------------

        return res.status(200).json(
            result
        );


    } catch (error) {

        console.error(
            "Dropout Prediction Error:",
            error.message
        );


        if (
            error.message.includes(
                "No dropout data"
            )
        ) {

            return res.status(404).json({

                success: false,

                message:
                    "Dropout data not found for this student."

            });
        }


        if (
            error.message.includes(
                "unavailable"
            )
        ) {

            return res.status(503).json({

                success: false,

                message:
                    "Dropout prediction service unavailable."

            });
        }


        if (
            error.message.includes(
                "timed out"
            )
        ) {

            return res.status(504).json({

                success: false,

                message:
                    "Dropout prediction service timed out."

            });
        }


        return res.status(500).json({

            success: false,

            message:
                "Failed to generate dropout prediction.",

            error:
                error.message

        });
    }
};