
CREATE EXTENSION IF NOT EXISTS pgcrypto;



DROP TABLE education.quiz_sessions CASCADE;
drop table education.domain_roles cascade;
drop table education.skills cascade;
drop table education.domain_required_skills;
drop table education.difficulty_levels;
drop table education.student_answers;
drop table education.questions;
drop table education.student_skill_results;



CREATE TABLE education.domain_roles
(
    domain_role_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    domain_name VARCHAR(100) NOT NULL UNIQUE,

    category VARCHAR(50),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


INSERT INTO education.domain_roles
(domain_name, category)
VALUES

('AI Engineer',
 'Artificial Intelligence'),

('Machine Learning Engineer',
 'Artificial Intelligence'),

('Data Scientist',
 'Data'),

('Data Analyst',
 'Data'),

('Data Engineer',
 'Data'),

('Generative AI Engineer',
 'Artificial Intelligence'),

('MLOps Engineer',
 'Artificial Intelligence'),

('Backend Developer',
 'Software Development'),

('Full Stack Developer',
 'Software Development'),

('Frontend Developer',
 'Software Development'),

('Cloud Engineer',
 'Cloud Computing'),

('DevOps Engineer',
 'Cloud Computing'),

('Cybersecurity Analyst',
 'Cybersecurity'),

('Software Development Engineer',
 'Software Development'),

('Mobile Application Developer',
 'Software Development'),

('UI/UX Designer',
 'Design'),

('Business Intelligence Developer',
 'Data'),

('Blockchain Developer',
 'Blockchain'),

('IoT Engineer',
 'Internet of Things'),

('Robotics and Computer Vision Engineer',
 'Artificial Intelligence'),
 
('Software Test Engineer',
 'Software Testing');


select * from education.domain_roles;
 

CREATE TABLE education.skills (
    skill_id SERIAL PRIMARY KEY,
    skill_name VARCHAR(100) NOT NULL UNIQUE,
    category VARCHAR(50),
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);






INSERT INTO education.skills(skill_name, category, description) VALUES

('Python', 'Programming', 'Programming language for AI, ML, Data Science, and software development.'),
('Java', 'Programming', 'Object-oriented programming language for enterprise applications.'),
('SQL', 'Database', 'Language for querying and managing relational databases.'),
('Machine Learning', 'Artificial Intelligence', 'Algorithms that enable systems to learn from data.'),
('Deep Learning', 'Artificial Intelligence', 'Neural network-based machine learning techniques.'),
('Git', 'Version Control', 'Distributed version control system for source code management.'),

('Feature Engineering', 'Artificial Intelligence', 'Creating and selecting features for machine learning models.'),
('MLOps', 'Artificial Intelligence', 'Practices for deploying and maintaining ML models.'),

('Statistics', 'Data Science', 'Statistical methods for data analysis and inference.'),
('Data Visualization', 'Data Science', 'Presenting data using charts, graphs, and dashboards.'),

('Excel', 'Data Analysis', 'Spreadsheet software for data analysis and reporting.'),
('Power BI', 'Data Visualization', 'Business intelligence and visualization platform.'),

('Apache Spark', 'Big Data', 'Distributed data processing framework.'),
('ETL', 'Data Engineering', 'Extract, Transform, and Load data pipelines.'),
('Cloud Computing', 'Cloud', 'Delivery of computing services over the internet.'),

('Prompt Engineering', 'Generative AI', 'Designing prompts for large language models.'),
('LLMs', 'Generative AI', 'Large Language Models such as GPT and Llama.'),
('RAG', 'Generative AI', 'Retrieval-Augmented Generation technique.'),
('Vector Databases', 'Generative AI', 'Databases optimized for vector embeddings.'),

('Docker', 'DevOps', 'Containerization platform.'),
('Kubernetes', 'DevOps', 'Container orchestration platform.'),
('MLflow', 'MLOps', 'Machine learning lifecycle management platform.'),
('CI/CD', 'DevOps', 'Continuous Integration and Continuous Deployment.'),

('Spring Boot', 'Backend Development', 'Java framework for building backend applications.'),
('REST APIs', 'Backend Development', 'Architectural style for web services.'),

('HTML', 'Frontend Development', 'Markup language for web pages.'),
('CSS', 'Frontend Development', 'Stylesheet language for web pages.'),
('JavaScript', 'Frontend Development', 'Programming language for interactive web applications.'),
('React', 'Frontend Development', 'JavaScript library for building user interfaces.'),
('Node.js', 'Backend Development', 'JavaScript runtime for backend development.'),

('UI/UX', 'Design', 'User Interface and User Experience design.'),

('AWS', 'Cloud', 'Amazon Web Services cloud platform.'),
('Linux', 'Operating System', 'Open-source operating system.'),
('Networking', 'Networking', 'Computer network concepts and protocols.'),
('Jenkins', 'DevOps', 'Automation server for CI/CD pipelines.'),

('Network Security', 'Cybersecurity', 'Protecting computer networks from threats.'),
('Ethical Hacking', 'Cybersecurity', 'Authorized penetration testing and security assessment.'),
('SIEM', 'Cybersecurity', 'Security Information and Event Management.'),
('Incident Response', 'Cybersecurity', 'Responding to cybersecurity incidents.'),

('Data Structures', 'Programming', 'Efficient organization of data in memory.'),
('Algorithms', 'Programming', 'Step-by-step procedures for solving problems.'),
('OOP', 'Programming', 'Object-Oriented Programming concepts.'),

('Flutter', 'Mobile Development', 'Cross-platform mobile app development framework.'),
('Dart', 'Mobile Development', 'Programming language used with Flutter.'),
('Firebase', 'Mobile Development', 'Backend platform for mobile and web applications.'),

('Figma', 'Design', 'Collaborative UI/UX design tool.'),
('Wireframing', 'Design', 'Creating layout blueprints for applications.'),
('Prototyping', 'Design', 'Building interactive design mockups.'),
('UX Research', 'Design', 'Researching user behavior and experience.'),
('Design Principles', 'Design', 'Fundamental concepts of visual and interaction design.'),

('Tableau', 'Data Visualization', 'Business intelligence and visualization software.'),
('Data Warehousing', 'Data Engineering', 'Centralized repository for analytical data.'),

('Solidity', 'Blockchain', 'Programming language for Ethereum smart contracts.'),
('Ethereum', 'Blockchain', 'Blockchain platform for decentralized applications.'),
('Smart Contracts', 'Blockchain', 'Self-executing contracts on blockchain.'),
('Web3', 'Blockchain', 'Decentralized web technologies.'),

('Embedded C', 'IoT', 'Programming language for embedded systems.'),
('Arduino', 'IoT', 'Microcontroller platform for electronics projects.'),
('Raspberry Pi', 'IoT', 'Single-board computer for IoT applications.'),
('IoT Protocols', 'IoT', 'Communication protocols for IoT devices.'),

('OpenCV', 'Computer Vision', 'Library for image and video processing.'),
('ROS', 'Robotics', 'Robot Operating System framework.'),
('Computer Vision', 'Computer Vision', 'AI techniques for understanding images and videos.'),

('Manual Testing', 'Software Testing', 'Testing software manually without automation.'),
('API Testing', 'Software Testing', 'Testing application programming interfaces.'),
('Selenium', 'Software Testing', 'Automation testing framework for web applications.'),
('Bug Tracking (Jira)', 'Software Testing', 'Tracking and managing software defects using Jira.');


select * from education.skills;




DROP TABLE education.domain_required_skills;
CREATE TABLE education.domain_required_skills (
    domain_required_skill_id SERIAL PRIMARY KEY,

    domain_role_id UUID NOT NULL,

    skill_id INT NOT NULL,

    required_level SMALLINT NOT NULL
        CHECK (required_level BETWEEN 0 AND 5),

    CONSTRAINT fk_domain_role
        FOREIGN KEY (domain_role_id)
        REFERENCES education.domain_roles(domain_role_id)
        ON DELETE CASCADE,

    CONSTRAINT fk_skill
        FOREIGN KEY (skill_id)
        REFERENCES education.skills(skill_id)
        ON DELETE CASCADE,

    UNIQUE (domain_role_id, skill_id)
);




INSERT INTO education.domain_required_skills
(domain_role_id, skill_id, required_level)

SELECT
    dr.domain_role_id,
    s.skill_id,
    v.required_level
FROM (
    VALUES
    -- AI Engineer
    ('AI Engineer','Python',5),
    ('AI Engineer','Machine Learning',5),
    ('AI Engineer','Deep Learning',5),
    ('AI Engineer','SQL',3),
    ('AI Engineer','Git',3),

    -- Machine Learning Engineer
    ('Machine Learning Engineer','Python',5),
    ('Machine Learning Engineer','Machine Learning',5),
    ('Machine Learning Engineer','Feature Engineering',4),
    ('Machine Learning Engineer','SQL',4),
    ('Machine Learning Engineer','MLOps',3),

    -- Data Scientist
    ('Data Scientist','Python',5),
    ('Data Scientist','SQL',5),
    ('Data Scientist','Statistics',5),
    ('Data Scientist','Machine Learning',4),
    ('Data Scientist','Data Visualization',4),

    -- Data Analyst
    ('Data Analyst','SQL',5),
    ('Data Analyst','Excel',5),
    ('Data Analyst','Power BI',4),
    ('Data Analyst','Python',3),
    ('Data Analyst','Statistics',3),

    -- Data Engineer
    ('Data Engineer','SQL',5),
    ('Data Engineer','Python',4),
    ('Data Engineer','Apache Spark',4),
    ('Data Engineer','ETL',5),
    ('Data Engineer','Cloud Computing',3),

    -- Generative AI Engineer
    ('Generative AI Engineer','Python',5),
    ('Generative AI Engineer','Prompt Engineering',5),
    ('Generative AI Engineer','LLMs',5),
    ('Generative AI Engineer','RAG',4),
    ('Generative AI Engineer','Vector Databases',4),

    -- MLOps Engineer
    ('MLOps Engineer','Docker',5),
    ('MLOps Engineer','Kubernetes',5),
    ('MLOps Engineer','MLflow',4),
    ('MLOps Engineer','Python',4),
    ('MLOps Engineer','CI/CD',4),

    -- Backend Developer
    ('Backend Developer','Java',5),
    ('Backend Developer','SQL',5),
    ('Backend Developer','Spring Boot',5),
    ('Backend Developer','REST APIs',4),
    ('Backend Developer','Git',3),

    -- Full Stack Developer
    ('Full Stack Developer','HTML',5),
    ('Full Stack Developer','CSS',5),
    ('Full Stack Developer','JavaScript',5),
    ('Full Stack Developer','React',4),
    ('Full Stack Developer','Node.js',4),

    -- Frontend Developer
    ('Frontend Developer','HTML',5),
    ('Frontend Developer','CSS',5),
    ('Frontend Developer','JavaScript',5),
    ('Frontend Developer','React',4),
    ('Frontend Developer','UI/UX',3),

    -- Cloud Engineer
    ('Cloud Engineer','AWS',5),
    ('Cloud Engineer','Linux',5),
    ('Cloud Engineer','Docker',4),
    ('Cloud Engineer','Kubernetes',4),
    ('Cloud Engineer','Networking',4),

    -- DevOps Engineer
    ('DevOps Engineer','Docker',5),
    ('DevOps Engineer','Kubernetes',5),
    ('DevOps Engineer','Jenkins',5),
    ('DevOps Engineer','Linux',4),
    ('DevOps Engineer','Git',4),

    -- Cybersecurity Analyst
    ('Cybersecurity Analyst','Network Security',5),
    ('Cybersecurity Analyst','Linux',4),
    ('Cybersecurity Analyst','Ethical Hacking',5),
    ('Cybersecurity Analyst','SIEM',4),
    ('Cybersecurity Analyst','Incident Response',4),

    -- Software Development Engineer (SDE)
    ('Software Development Engineer','Java',5),
    ('Software Development Engineer','Data Structures',5),
    ('Software Development Engineer','Algorithms',5),
    ('Software Development Engineer','OOP',5),
    ('Software Development Engineer','SQL',4),

    -- Mobile Application Developer
    ('Mobile Application Developer','Flutter',5),
    ('Mobile Application Developer','Dart',5),
    ('Mobile Application Developer','Firebase',4),
    ('Mobile Application Developer','REST APIs',3),
    ('Mobile Application Developer','Git',3),

    -- UI/UX Designer
    ('UI/UX Designer','Figma',5),
    ('UI/UX Designer','Wireframing',5),
    ('UI/UX Designer','Prototyping',4),
    ('UI/UX Designer','UX Research',4),
    ('UI/UX Designer','Design Principles',5),

    -- Business Intelligence Developer
    ('Business Intelligence Developer','SQL',5),
    ('Business Intelligence Developer','Power BI',5),
    ('Business Intelligence Developer','Tableau',4),
    ('Business Intelligence Developer','Excel',4),
    ('Business Intelligence Developer','Data Warehousing',4),

    -- Blockchain Developer
    ('Blockchain Developer','Solidity',5),
    ('Blockchain Developer','Ethereum',5),
    ('Blockchain Developer','Smart Contracts',5),
    ('Blockchain Developer','Web3',4),
    ('Blockchain Developer','JavaScript',3),

    -- IoT Engineer
    ('IoT Engineer','Embedded C',5),
    ('IoT Engineer','Arduino',5),
    ('IoT Engineer','Raspberry Pi',4),
    ('IoT Engineer','IoT Protocols',4),
    ('IoT Engineer','Python',3),

    -- Robotics and Computer Vision Engineer
    ('Robotics and Computer Vision Engineer','Python',5),
    ('Robotics and Computer Vision Engineer','OpenCV',5),
    ('Robotics and Computer Vision Engineer','ROS',4),
    ('Robotics and Computer Vision Engineer','Deep Learning',4),
    ('Robotics and Computer Vision Engineer','Computer Vision',5),

    -- Software Test Engineer
    ('Software Test Engineer','Manual Testing',5),
    ('Software Test Engineer','SQL',4),
    ('Software Test Engineer','API Testing',4),
    ('Software Test Engineer','Selenium',4),
    ('Software Test Engineer','Bug Tracking (Jira)',3)

) AS v(domain_name, skill_name, required_level)

JOIN education.domain_roles dr
    ON dr.domain_name = v.domain_name

JOIN education.skills s
    ON s.skill_name = v.skill_name;



select * from education.domain_required_skills;





CREATE TABLE education.difficulty_levels (
    difficulty_id SERIAL PRIMARY KEY,
    difficulty_name VARCHAR(20) UNIQUE NOT NULL,
    difficulty_order INT UNIQUE NOT NULL
);


INSERT INTO education.difficulty_levels
(difficulty_name,difficulty_order)
VALUES
('Easy',1),
('Medium',2),
('Hard',3);




CREATE TABLE education.users
(
    user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    name VARCHAR(255) NOT NULL,

    email VARCHAR(255) UNIQUE NOT NULL,

    role_id UUID NOT NULL
        REFERENCES education.domain_roles(domain_role_id),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);








select * from education.users;





CREATE TABLE education.questions (
    question_id SERIAL PRIMARY KEY,
    skill_id INT NOT NULL REFERENCES education.skills(skill_id),
    difficulty_id INT NOT NULL REFERENCES education.difficulty_levels(difficulty_id),
    question_text TEXT NOT NULL,
    option_a TEXT NOT NULL,
    option_b TEXT NOT NULL,
    option_c TEXT NOT NULL,
    option_d TEXT NOT NULL,
    correct_option CHAR(1) NOT NULL CHECK (correct_option IN ('A', 'B', 'C', 'D')),
    marks INT DEFAULT 1,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
select * from education.questions;





CREATE TABLE education.quiz_sessions
(
    session_id SERIAL PRIMARY KEY,

    user_id UUID NOT NULL
        REFERENCES education.users(user_id)
        ON DELETE CASCADE,

    domain_role_id UUID NOT NULL
        REFERENCES education.domain_roles(domain_role_id)
        ON DELETE RESTRICT,

    start_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    end_time TIMESTAMP,

    status VARCHAR(20) NOT NULL DEFAULT 'In Progress',

    total_questions INT NOT NULL DEFAULT 50,

    questions_answered INT NOT NULL DEFAULT 0
);


CREATE INDEX idx_quiz_sessions_user
ON education.quiz_sessions(user_id);

CREATE INDEX idx_quiz_sessions_domain_role
ON education.quiz_sessions(domain_role_id);

CREATE INDEX idx_quiz_sessions_status
ON education.quiz_sessions(status);


drop table education.student_answers;
CREATE TABLE education.student_answers (
    answer_id SERIAL PRIMARY KEY,

    session_id INT NOT NULL
        REFERENCES education.quiz_sessions(session_id)
        ON DELETE CASCADE,

    skill_id INT NOT NULL
        REFERENCES education.skills(skill_id)
        ON DELETE RESTRICT,

    question_id INT NOT NULL
        REFERENCES education.questions(question_id)
        ON DELETE RESTRICT,

    difficulty_id INT NOT NULL
        REFERENCES education.difficulty_levels(difficulty_id)
        ON DELETE RESTRICT,

    selected_option CHAR(1) NOT NULL
        CHECK (selected_option IN ('A', 'B', 'C', 'D')),

    correct_option CHAR(1) NOT NULL
        CHECK (correct_option IN ('A', 'B', 'C', 'D')),

    is_correct BOOLEAN NOT NULL,

    marks_awarded INT NOT NULL DEFAULT 0,

    answered_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);


select * from education.student_answers;


CREATE INDEX idx_student_answers_session
ON education.student_answers(session_id);

CREATE INDEX idx_student_answers_question
ON education.student_answers(question_id);

CREATE INDEX idx_student_answers_skill
ON education.student_answers(skill_id);

CREATE INDEX idx_student_answers_difficulty
ON education.student_answers(difficulty_id);




drop table education.student_skill_results;

CREATE TABLE education.student_skill_results (
    result_id SERIAL PRIMARY KEY,

    session_id INT NOT NULL
        REFERENCES education.quiz_sessions(session_id)
        ON DELETE CASCADE,

    skill_id INT NOT NULL
        REFERENCES education.skills(skill_id)
        ON DELETE RESTRICT,

    obtained_score INT NOT NULL,

    maximum_score INT NOT NULL,

    percentage DECIMAL(5,2) NOT NULL
        CHECK (percentage BETWEEN 0 AND 100),

    skill_level SMALLINT NOT NULL
        CHECK (skill_level BETWEEN 1 AND 5),

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);


select * from education.student_skill_results;


CREATE INDEX idx_student_skill_results_session
ON education.student_skill_results(session_id);

CREATE INDEX idx_student_skill_results_skill
ON education.student_skill_results(skill_id);




CREATE TABLE education.quiz_state (

    session_id INT NOT NULL,
    skill_id INT NOT NULL,

    current_difficulty INT DEFAULT 1,
    correct_streak INT DEFAULT 0,
    wrong_streak INT DEFAULT 0,

    questions_answered INT DEFAULT 0,

    obtained_score INT DEFAULT 0,
    maximum_score INT DEFAULT 0,

    PRIMARY KEY (session_id, skill_id),

    FOREIGN KEY (session_id)
        REFERENCES education.quiz_sessions(session_id)
        ON DELETE CASCADE,

    FOREIGN KEY (skill_id)
        REFERENCES education.skills(skill_id)
);




