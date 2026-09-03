import uuid

from sqlalchemy import text

from src.database.database_connection import engine


# ============================================================
# ACHIEVEMENTS
# ============================================================

ACHIEVEMENTS = [

    {
        "name": "First Step",
        "description": "Complete your first learning activity.",
        "category": "LEARNING",
        "points": 50,
        "requirement_type": "ACTIVITIES_COMPLETED",
        "requirement_value": 1,
        "difficulty": "EASY"
    },

    {
        "name": "Quick Learner",
        "description": "Complete 5 learning activities.",
        "category": "LEARNING",
        "points": 100,
        "requirement_type": "ACTIVITIES_COMPLETED",
        "requirement_value": 5,
        "difficulty": "EASY"
    },

    {
        "name": "Dedicated Learner",
        "description": "Complete 25 learning activities.",
        "category": "LEARNING",
        "points": 250,
        "requirement_type": "ACTIVITIES_COMPLETED",
        "requirement_value": 25,
        "difficulty": "MEDIUM"
    },

    {
        "name": "Learning Champion",
        "description": "Complete 100 learning activities.",
        "category": "LEARNING",
        "points": 500,
        "requirement_type": "ACTIVITIES_COMPLETED",
        "requirement_value": 100,
        "difficulty": "HARD"
    },

    {
        "name": "Course Starter",
        "description": "Enroll in your first course.",
        "category": "COURSE",
        "points": 50,
        "requirement_type": "COURSES_ENROLLED",
        "requirement_value": 1,
        "difficulty": "EASY"
    },

    {
        "name": "Course Explorer",
        "description": "Enroll in 3 courses.",
        "category": "COURSE",
        "points": 150,
        "requirement_type": "COURSES_ENROLLED",
        "requirement_value": 3,
        "difficulty": "EASY"
    },

    {
        "name": "Course Master",
        "description": "Complete 5 courses.",
        "category": "COURSE",
        "points": 500,
        "requirement_type": "COURSES_COMPLETED",
        "requirement_value": 5,
        "difficulty": "HARD"
    },

    {
        "name": "Quiz Beginner",
        "description": "Complete your first quiz.",
        "category": "QUIZ",
        "points": 50,
        "requirement_type": "QUIZZES_COMPLETED",
        "requirement_value": 1,
        "difficulty": "EASY"
    },

    {
        "name": "Quiz Master",
        "description": "Complete 10 quizzes.",
        "category": "QUIZ",
        "points": 250,
        "requirement_type": "QUIZZES_COMPLETED",
        "requirement_value": 10,
        "difficulty": "MEDIUM"
    },

    {
        "name": "Perfect Score",
        "description": "Score 100% on a quiz.",
        "category": "QUIZ",
        "points": 300,
        "requirement_type": "PERFECT_QUIZ",
        "requirement_value": 1,
        "difficulty": "HARD"
    },

    {
        "name": "Assignment Hero",
        "description": "Complete 10 assignments.",
        "category": "ASSIGNMENT",
        "points": 250,
        "requirement_type": "ASSIGNMENTS_COMPLETED",
        "requirement_value": 10,
        "difficulty": "MEDIUM"
    },

    {
        "name": "Discussion Starter",
        "description": "Participate in your first discussion.",
        "category": "COMMUNITY",
        "points": 50,
        "requirement_type": "DISCUSSIONS",
        "requirement_value": 1,
        "difficulty": "EASY"
    },

    {
        "name": "Community Contributor",
        "description": "Participate in 20 discussions.",
        "category": "COMMUNITY",
        "points": 250,
        "requirement_type": "DISCUSSIONS",
        "requirement_value": 20,
        "difficulty": "MEDIUM"
    },

    {
        "name": "7 Day Streak",
        "description": "Learn for 7 consecutive days.",
        "category": "STREAK",
        "points": 200,
        "requirement_type": "STREAK_DAYS",
        "requirement_value": 7,
        "difficulty": "MEDIUM"
    },

    {
        "name": "30 Day Streak",
        "description": "Maintain a 30 day learning streak.",
        "category": "STREAK",
        "points": 750,
        "requirement_type": "STREAK_DAYS",
        "requirement_value": 30,
        "difficulty": "HARD"
    },

    {
        "name": "Knowledge Seeker",
        "description": "Watch 50 educational videos.",
        "category": "ENGAGEMENT",
        "points": 300,
        "requirement_type": "VIDEOS_WATCHED",
        "requirement_value": 50,
        "difficulty": "MEDIUM"
    },

    {
        "name": "Video Master",
        "description": "Watch 200 educational videos.",
        "category": "ENGAGEMENT",
        "points": 750,
        "requirement_type": "VIDEOS_WATCHED",
        "requirement_value": 200,
        "difficulty": "HARD"
    },

    {
        "name": "Early Achiever",
        "description": "Complete a course before its expected deadline.",
        "category": "PERFORMANCE",
        "points": 400,
        "requirement_type": "EARLY_COMPLETION",
        "requirement_value": 1,
        "difficulty": "HARD"
    },

    {
        "name": "High Performer",
        "description": "Maintain an average score above 90%.",
        "category": "PERFORMANCE",
        "points": 500,
        "requirement_type": "AVERAGE_SCORE",
        "requirement_value": 90,
        "difficulty": "HARD"
    },

    {
        "name": "Top Learner",
        "description": "Reach 5000 total learning points.",
        "category": "MILESTONE",
        "points": 1000,
        "requirement_type": "TOTAL_POINTS",
        "requirement_value": 5000,
        "difficulty": "LEGENDARY"
    }
]


# ============================================================
# REWARDS
# ============================================================

REWARDS = [

    {
        "name": "Course Discount 5%",
        "description": "Get 5% discount on an eligible course.",
        "reward_type": "DISCOUNT",
        "points_cost": 500,
        "reward_value": 5,
        "stock": -1
    },

    {
        "name": "Course Discount 10%",
        "description": "Get 10% discount on an eligible course.",
        "reward_type": "DISCOUNT",
        "points_cost": 1000,
        "reward_value": 10,
        "stock": -1
    },

    {
        "name": "Course Discount 20%",
        "description": "Get 20% discount on an eligible course.",
        "reward_type": "DISCOUNT",
        "points_cost": 2000,
        "reward_value": 20,
        "stock": -1
    },

    {
        "name": "Premium Course Access",
        "description": "Unlock one eligible premium course.",
        "reward_type": "COURSE_ACCESS",
        "points_cost": 2500,
        "reward_value": 1,
        "stock": 100
    },

    {
        "name": "Certificate Upgrade",
        "description": "Upgrade an eligible course certificate.",
        "reward_type": "CERTIFICATE",
        "points_cost": 1500,
        "reward_value": 1,
        "stock": 100
    },

    {
        "name": "Profile Badge",
        "description": "Unlock an exclusive profile badge.",
        "reward_type": "BADGE",
        "points_cost": 750,
        "reward_value": 1,
        "stock": -1
    },

    {
        "name": "Mentor Session",
        "description": "Redeem one mentor consultation session.",
        "reward_type": "MENTOR_SESSION",
        "points_cost": 3000,
        "reward_value": 1,
        "stock": 50
    },

    {
        "name": "Premium Subscription",
        "description": "Unlock premium learning access for one month.",
        "reward_type": "SUBSCRIPTION",
        "points_cost": 5000,
        "reward_value": 1,
        "stock": 100
    },

    {
        "name": "Learning Credits",
        "description": "Receive additional learning credits.",
        "reward_type": "CREDIT",
        "points_cost": 1200,
        "reward_value": 100,
        "stock": -1
    },

    {
        "name": "Exclusive Avatar",
        "description": "Unlock an exclusive learner avatar.",
        "reward_type": "AVATAR",
        "points_cost": 800,
        "reward_value": 1,
        "stock": -1
    }
]


# ============================================================
# INSERT ACHIEVEMENTS
# ============================================================

def insert_achievements():

    query = text("""
        INSERT INTO education.achievements
        (
            id,
            name,
            description,
            category,
            points,
            requirement_type,
            requirement_value,
            difficulty,
            is_active
        )
        VALUES
        (
            :id,
            :name,
            :description,
            :category,
            :points,
            :requirement_type,
            :requirement_value,
            :difficulty,
            TRUE
        )
    """)

    records = []

    for achievement in ACHIEVEMENTS:

        records.append({

            "id": str(uuid.uuid4()),

            **achievement

        })

    with engine.begin() as connection:

        connection.execute(
            query,
            records
        )

    print(
        f"✅ {len(records)} achievements inserted."
    )


# ============================================================
# INSERT REWARDS
# ============================================================

def insert_rewards():

    query = text("""
        INSERT INTO education.rewards
        (
            id,
            name,
            description,
            reward_type,
            points_cost,
            reward_value,
            stock,
            is_active
        )
        VALUES
        (
            :id,
            :name,
            :description,
            :reward_type,
            :points_cost,
            :reward_value,
            :stock,
            TRUE
        )
    """)

    records = []

    for reward in REWARDS:

        records.append({

            "id": str(uuid.uuid4()),

            **reward

        })

    with engine.begin() as connection:

        connection.execute(
            query,
            records
        )

    print(
        f"✅ {len(records)} rewards inserted."
    )


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    print(
        "\n=========================================="
    )

    print(
        "EduSaaS Gamification Data Generator"
    )

    print(
        "==========================================\n"
    )

    insert_achievements()

    insert_rewards()

    print(
        "\n✅ Gamification master data created."
    )