const recommendationPythonService = require(
    "../services/recommendationPythonService"
);

const recommendationDataService = require(
    "../services/recommendationDataService"
);


exports.getRecommendations = async (req, res) => {

    try {

        const {
            user_id,
            course_name
        } = req.query;


        // ---------------------------------------------
        // Validate request
        // ---------------------------------------------

        if (!user_id || !course_name) {

            return res.status(400).json({
                success: false,
                message: "user_id and course_name are required."
            });
        }


        // ---------------------------------------------
        // Get data from PostgreSQL
        // ---------------------------------------------

        const dbData =
            await recommendationDataService
                .getRecommendationData(user_id);


        // ---------------------------------------------
        // Build Python ML payload
        // ---------------------------------------------

        const payload = {

            user_id,

            course_name,

            courses: dbData.courses,

            ratings: dbData.ratings,

            user: dbData.user,

            prerequisites:
                dbData.prerequisites,

            completed_courses:
                dbData.completed_courses
        };


        // ---------------------------------------------
        // Call Python recommendation service
        // ---------------------------------------------

        const result =
            await recommendationPythonService
                .getRecommendations(payload);


        // ---------------------------------------------
        // Return successful response
        // ---------------------------------------------

        return res.status(200).json(result);

    }
    catch (err) {

        console.error(
            "Recommendation Error:",
            err.message
        );


        // ---------------------------------------------
        // User not found in database
        // ---------------------------------------------

        if (
            err.message === "User not found."
        ) {

            return res.status(404).json({
                success: false,
                message: "User not found."
            });
        }


        // ---------------------------------------------
        // Python service returned a known HTTP error
        // ---------------------------------------------

        if (err.status) {

            return res.status(
                err.status
            ).json({

                success: false,

                message: err.message
            });
        }


        // ---------------------------------------------
        // Unexpected internal error
        // ---------------------------------------------

        return res.status(500).json({

            success: false,

            message:
                "Failed to generate recommendations."
        });
    }
};