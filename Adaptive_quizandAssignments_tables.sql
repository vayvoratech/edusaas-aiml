CREATE TABLE difficulty_levels (
    difficulty_id SERIAL PRIMARY KEY,
    difficulty_name VARCHAR(20) UNIQUE NOT NULL,
    difficulty_order INT UNIQUE NOT NULL
);


INSERT INTO difficulty_levels
(difficulty_name,difficulty_order)
VALUES
('Easy',1),
('Medium',2),
('Hard',3);



CREATE TABLE questions (

    question_id SERIAL PRIMARY KEY,

    skill_id INT NOT NULL REFERENCES skill(skill_id),

    difficulty_id INT NOT NULL
        REFERENCES difficulty_levels(difficulty_id),

    question_text TEXT NOT NULL,

    option_a TEXT NOT NULL,

    option_b TEXT NOT NULL,

    option_c TEXT NOT NULL,

    option_d TEXT NOT NULL,

    correct_option CHAR(1) NOT NULL,

    explanation TEXT,

    marks INT DEFAULT 1,

    is_active BOOLEAN DEFAULT TRUE,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);





select * from questions;




CREATE TABLE quiz_sessions (
    session_id SERIAL PRIMARY KEY,

    student_id INT NOT NULL,

    job_role_id INT NOT NULL
        REFERENCES job_roles(job_role_id),

    start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    end_time TIMESTAMP,

    status VARCHAR(20) DEFAULT 'In Progress'
        CHECK (status IN ('In Progress', 'Completed', 'Abandoned')),

    total_questions INT DEFAULT 50,

    questions_answered INT DEFAULT 0,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);





CREATE TABLE student_answers (
    answer_id SERIAL PRIMARY KEY,

    session_id INT NOT NULL
        REFERENCES quiz_sessions(session_id)
        ON DELETE CASCADE,

    skill_id INT NOT NULL
        REFERENCES skill(skill_id),

    question_id INT NOT NULL
        REFERENCES questions(question_id),

    difficulty_id INT NOT NULL
        REFERENCES difficulty_levels(difficulty_id),

    selected_option CHAR(1) NOT NULL
        CHECK (selected_option IN ('A', 'B', 'C', 'D')),

    correct_option CHAR(1) NOT NULL
        CHECK (correct_option IN ('A', 'B', 'C', 'D')),

    is_correct BOOLEAN NOT NULL,

    marks_awarded INT DEFAULT 0,

    answered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);







CREATE TABLE student_skill_results (
    result_id SERIAL PRIMARY KEY,

    session_id INT NOT NULL
        REFERENCES quiz_sessions(session_id)
        ON DELETE CASCADE,

    skill_id INT NOT NULL
        REFERENCES skill(skill_id),

    obtained_score INT NOT NULL,

    maximum_score INT NOT NULL,

    percentage DECIMAL(5,2) NOT NULL,

    skill_level INT NOT NULL
        CHECK (skill_level BETWEEN 1 AND 5),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);






SELECT
    question_id,
    question_text,
    option_a,
    option_b,
    option_c,
    option_d
FROM questions
WHERE skill_id = 1
  AND difficulty_id = 1
ORDER BY RANDOM()
LIMIT 1;



SELECT * FROM quiz_sessions;


INSERT INTO quiz_sessions (
    student_id,
    job_role_id,
    status
)
VALUES (
    101,
    1,
    'In Progress'
);