CREATE TABLE job_roles (
    job_role_id SERIAL PRIMARY KEY,
    job_role_name VARCHAR(100) NOT NULL UNIQUE,
    category VARCHAR(50),
    description TEXT,
    demand_level VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);




INSERT INTO job_roles
(job_role_name, category, description, demand_level)
VALUES

('AI Engineer',
 'Artificial Intelligence',
 'Builds AI applications using machine learning, deep learning, NLP, and Generative AI.',
 'Very High'),

('Machine Learning Engineer',
 'Artificial Intelligence',
 'Develops, trains, and deploys machine learning models for production systems.',
 'Very High'),

('Data Scientist',
 'Data',
 'Analyzes complex datasets to extract insights and build predictive models.',
 'Very High'),

('Data Analyst',
 'Data',
 'Analyzes business data and creates reports and dashboards for decision-making.',
 'High'),

('Data Engineer',
 'Data',
 'Designs, builds, and maintains data pipelines and data warehouses.',
 'Very High'),

('Generative AI Engineer',
 'Artificial Intelligence',
 'Develops applications using Large Language Models (LLMs) and Generative AI technologies.',
 'Very High'),

('MLOps Engineer',
 'Artificial Intelligence',
 'Deploys, monitors, and manages machine learning models in production.',
 'Very High'),

('Backend Developer',
 'Software Development',
 'Develops server-side applications, APIs, and databases.',
 'Very High'),

('Full Stack Developer',
 'Software Development',
 'Develops both frontend and backend components of web applications.',
 'Very High'),

('Frontend Developer',
 'Software Development',
 'Builds responsive and interactive web user interfaces.',
 'High'),

('Cloud Engineer',
 'Cloud Computing',
 'Designs and manages cloud infrastructure and cloud-based services.',
 'Very High'),

('DevOps Engineer',
 'Cloud Computing',
 'Automates software deployment and infrastructure management.',
 'Very High'),

('Cybersecurity Analyst',
 'Cybersecurity',
 'Protects systems, networks, and data from cyber threats.',
 'Very High'),

('Software Development Engineer',
 'Software Development',
 'Designs and develops scalable software applications.',
 'Very High'),

('Mobile Application Developer',
 'Software Development',
 'Develops Android and iOS mobile applications.',
 'High'),

('UI/UX Designer',
 'Design',
 'Designs user-friendly interfaces and enhances user experience.',
 'High'),

('Business Intelligence Developer',
 'Data',
 'Creates business reports, dashboards, and analytical solutions.',
 'High'),

('Blockchain Developer',
 'Blockchain',
 'Builds decentralized applications and smart contracts.',
 'Medium'),

('IoT Engineer',
 'Internet of Things',
 'Develops embedded systems and Internet of Things solutions.',
 'High'),

('Robotics and Computer Vision Engineer',
 'Artificial Intelligence',
 'Develops robotic systems and computer vision applications.',
 'High');

 
INSERT INTO job_roles
(job_role_name, category, description, demand_level)
VALUES

('Software Test Engineer',
 'Software Testing',
 'Designs, executes, and automates tests to ensure software quality.',
 'Very High');


 select * from job_roles;



	CREATE TABLE skill (
	    skill_id SERIAL PRIMARY KEY,
	    skill_name VARCHAR(100) NOT NULL UNIQUE,
	    category VARCHAR(50),
	    description TEXT,
	    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
	);




INSERT INTO skill (skill_name, category, description) VALUES

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


select * from skill;


SELECT skill_id, skill_name
FROM skill
ORDER BY skill_id;
 



 CREATE TABLE job_required_skills (
    job_required_skill_id SERIAL PRIMARY KEY,
    job_role_id INT NOT NULL,
    skill_id INT NOT NULL,
    required_level SMALLINT NOT NULL CHECK (required_level BETWEEN 0 AND 5),

    FOREIGN KEY (job_role_id) REFERENCES job_roles(job_role_id) ON DELETE CASCADE,
    FOREIGN KEY (skill_id) REFERENCES skill(skill_id) ON DELETE CASCADE,

    UNIQUE (job_role_id, skill_id)
);

select * from job_required_skills;




#AI ENGINEER

INSERT INTO job_required_skills (job_role_id, skill_id, required_level)
VALUES
(
    (SELECT job_role_id FROM job_roles WHERE job_role_name = 'AI Engineer'),
    (SELECT skill_id FROM skill WHERE skill_name = 'Python'),
    5
),
(
    (SELECT job_role_id FROM job_roles WHERE job_role_name = 'AI Engineer'),
    (SELECT skill_id FROM skill WHERE skill_name = 'Machine Learning'),
    5
),
(
    (SELECT job_role_id FROM job_roles WHERE job_role_name = 'AI Engineer'),
    (SELECT skill_id FROM skill WHERE skill_name = 'Deep Learning'),
    5
),
(
    (SELECT job_role_id FROM job_roles WHERE job_role_name = 'AI Engineer'),
    (SELECT skill_id FROM skill WHERE skill_name = 'SQL'),
    3
),
(
    (SELECT job_role_id FROM job_roles WHERE job_role_name = 'AI Engineer'),
    (SELECT skill_id FROM skill WHERE skill_name = 'Git'),
    3
);

#2.Machine Learning Engineer


INSERT INTO job_required_skills (job_role_id, skill_id, required_level)
VALUES
(
    (SELECT job_role_id FROM job_roles WHERE job_role_name = 'Machine Learning Engineer'),
    (SELECT skill_id FROM skill WHERE skill_name = 'Python'),
    5
),
(
    (SELECT job_role_id FROM job_roles WHERE job_role_name = 'Machine Learning Engineer'),
    (SELECT skill_id FROM skill WHERE skill_name = 'Machine Learning'),
    5
),
(
    (SELECT job_role_id FROM job_roles WHERE job_role_name = 'Machine Learning Engineer'),
    (SELECT skill_id FROM skill WHERE skill_name = 'Feature Engineering'),
    5
),
(
    (SELECT job_role_id FROM job_roles WHERE job_role_name = 'Machine Learning Engineer'),
    (SELECT skill_id FROM skill WHERE skill_name = 'SQL'),
    3
),
(
    (SELECT job_role_id FROM job_roles WHERE job_role_name = 'Machine Learning Engineer'),
    (SELECT skill_id FROM skill WHERE skill_name = 'MLOps'),
    3
);



#3.Data Scientist
INSERT INTO job_required_skills (job_role_id, skill_id, required_level)
VALUES
(
    (SELECT job_role_id FROM job_roles WHERE job_role_name = 'Software Test Engineer'),
    (SELECT skill_id FROM skill WHERE skill_name = 'Manual Testing'),
    5
),
(
    (SELECT job_role_id FROM job_roles WHERE job_role_name = 'Software Test Engineer'),
    (SELECT skill_id FROM skill WHERE skill_name = 'SQL'),
    4
),
(
    (SELECT job_role_id FROM job_roles WHERE job_role_name = 'Software Test Engineer'),
    (SELECT skill_id FROM skill WHERE skill_name = 'API Testing'),
    4
),
(
    (SELECT job_role_id FROM job_roles WHERE job_role_name = 'Software Test Engineer'),
    (SELECT skill_id FROM skill WHERE skill_name = 'Selenium'),
    4
),
(
    (SELECT job_role_id FROM job_roles WHERE job_role_name = 'Software Test Engineer'),
    (SELECT skill_id FROM skill WHERE skill_name = 'Bug Tracking (Jira)'),
    3
);