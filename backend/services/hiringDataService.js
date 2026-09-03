const pool = require("../config/db");


async function getHiringData(
    userId,
    jobId
) {

    // ----------------------------------------
    // Student Profile
    // ----------------------------------------

    const studentResult = await pool.query(
        `
        SELECT
            sp.user_id,
            sp.experience_years,
            sp.profile_score,
            sp.domain_role_id
        FROM education.student_profiles sp
        WHERE sp.user_id = $1
        `,
        [userId]
    );


    if (studentResult.rows.length === 0) {

        throw new Error(
            "Student profile not found."
        );
    }


    const student =
        studentResult.rows[0];


    // ----------------------------------------
    // Student Skills
    // ----------------------------------------

    const studentSkillsResult =
        await pool.query(
            `
            SELECT
                ss.skill_id,
                ss.skill_level
            FROM education.student_skills ss
            WHERE ss.user_id = $1
            `,
            [userId]
        );


    // ----------------------------------------
    // Job
    // ----------------------------------------

    const jobResult = await pool.query(
        `
        SELECT
            id,
            job_title,
            minimum_experience_years,
            domain_role_id
        FROM education.employer_jobs
        WHERE id = $1
        `,
        [jobId]
    );


    if (jobResult.rows.length === 0) {

        throw new Error(
            "Job not found."
        );
    }


    const job =
        jobResult.rows[0];


    // ----------------------------------------
    // Job Skills
    // ----------------------------------------

    const jobSkillsResult =
        await pool.query(
            `
            SELECT
                skill_id,
                required_level
            FROM education.job_skills
            WHERE job_id = $1
            `,
            [jobId]
        );


    // ----------------------------------------
    // Student Skill Map
    // ----------------------------------------

    const studentSkillMap =
        new Map();

    for (
        const skill
        of studentSkillsResult.rows
    ) {

        studentSkillMap.set(
            skill.skill_id,
            Number(skill.skill_level)
        );
    }


    // ----------------------------------------
    // Calculate Skill Match
    // ----------------------------------------

    let skillScore = 0;

    const jobSkills =
        jobSkillsResult.rows;


    if (jobSkills.length > 0) {

        for (
            const skill
            of jobSkills
        ) {

            const studentLevel =
                studentSkillMap.get(
                    skill.skill_id
                ) || 0;

            const requiredLevel =
                Number(
                    skill.required_level
                );


            if (
                studentLevel >=
                requiredLevel
            ) {

                skillScore += 1;

            } else if (
                studentLevel > 0 &&
                requiredLevel > 0
            ) {

                skillScore +=
                    studentLevel /
                    requiredLevel;
            }
        }


        skillScore =
            skillScore /
            jobSkills.length;
    }


    // ----------------------------------------
    // Experience Match
    // ----------------------------------------

    const studentExperience =
        Number(
            student.experience_years || 0
        );


    const requiredExperience =
        Number(
            job.minimum_experience_years || 0
        );


    let experienceMatch = 1;


    if (requiredExperience > 0) {

        experienceMatch =
            Math.min(
                studentExperience /
                requiredExperience,
                1
            );
    }


    // ----------------------------------------
    // Domain Match
    // ----------------------------------------

    const domainMatch =
        student.domain_role_id &&
        job.domain_role_id &&
        String(
            student.domain_role_id
        ) === String(
            job.domain_role_id
        )
            ? 1
            : 0;


    // ----------------------------------------
    // Final Model Input
    // ----------------------------------------

    return {

        user_id: userId,

        job_id: jobId,

        experience_years:
            studentExperience,

        required_experience_years:
            requiredExperience,

        skill_match_score:
            Number(
                skillScore.toFixed(4)
            ),

        experience_match_score:
            Number(
                experienceMatch.toFixed(4)
            ),

        domain_match:
            domainMatch,

        profile_score:
            Number(
                student.profile_score || 0
            )
    };
}


module.exports = {
    getHiringData
};