from datetime import datetime, timedelta

from sqlalchemy import text

from src.database.database_connection import engine


class GamificationService:
    """
    Core Gamification Engine.

    Calculates:
    - Student points
    - Student level
    - Learning streak
    - Achievement progress
    - Newly earned achievements
    """

    POINTS_PER_LEVEL = 1000

    def get_student_stats(
        self,
        user_id
    ):

        query = text("""
            SELECT
                COUNT(*) AS activities_completed,
                COUNT(
                    DISTINCT DATE(created_at)
                ) AS active_days
            FROM education.activity_logs
            WHERE user_id = :user_id
        """)

        with engine.connect() as connection:

            result = connection.execute(
                query,
                {
                    "user_id": user_id
                }
            ).mappings().first()

        return {

            "activities_completed":
                int(
                    result["activities_completed"] or 0
                ),

            "active_days":
                int(
                    result["active_days"] or 0
                )
        }

    # ========================================================
    # POINTS
    # ========================================================

    def calculate_points(
        self,
        user_id
    ):

        stats = self.get_student_stats(
            user_id
        )

        activities = stats["activities_completed"]

        # Basic activity points
        points = activities * 10

        return points

    # ========================================================
    # LEVEL
    # ========================================================

    def calculate_level(
        self,
        points
    ):

        level = (
            points //
            self.POINTS_PER_LEVEL
        ) + 1

        return max(
            1,
            level
        )

    # ========================================================
    # STREAK
    # ========================================================

    def calculate_streak(
        self,
        user_id
    ):

        query = text("""
            SELECT DISTINCT
                DATE(created_at) AS activity_date
            FROM education.activity_logs
            WHERE user_id = :user_id
            ORDER BY activity_date DESC
        """)

        with engine.connect() as connection:

            rows = connection.execute(
                query,
                {
                    "user_id": user_id
                }
            ).fetchall()

        if not rows:

            return 0

        dates = [

            row[0]

            for row in rows

        ]

        today = datetime.now().date()

        # Allow today or yesterday
        # as the beginning of the streak.

        if dates[0] == today:

            expected_date = today

        elif dates[0] == (
            today - timedelta(days=1)
        ):

            expected_date = (
                today - timedelta(days=1)
            )

        else:

            return 0

        streak = 0

        for activity_date in dates:

            if activity_date == expected_date:

                streak += 1

                expected_date -= timedelta(
                    days=1
                )

            else:

                break

        return streak

    # ========================================================
    # ACHIEVEMENTS
    # ========================================================

    def evaluate_achievements(
        self,
        user_id,
        points,
        streak
    ):

        stats = self.get_student_stats(
            user_id
        )

        activities = (
            stats["activities_completed"]
        )

        query = text("""
            SELECT
                id,
                name,
                description,
                category,
                points,
                requirement_type,
                requirement_value,
                difficulty
            FROM education.achievements
            WHERE is_active = TRUE
        """)

        with engine.connect() as connection:

            achievements = connection.execute(
                query
            ).mappings().all()

        earned_query = text("""
            SELECT achievement_id
            FROM education.student_achievements
            WHERE user_id = :user_id
        """)

        with engine.connect() as connection:

            earned_rows = connection.execute(
                earned_query,
                {
                    "user_id": user_id
                }
            ).fetchall()

        earned_ids = {

            str(row[0])

            for row in earned_rows

        }

        newly_earned = []

        for achievement in achievements:

            achievement_id = str(
                achievement["id"]
            )

            if achievement_id in earned_ids:

                continue

            requirement_type = (
                achievement[
                    "requirement_type"
                ]
            )

            requirement_value = float(
                achievement[
                    "requirement_value"
                ]
            )

            current_value = 0

            if requirement_type == (
                "ACTIVITIES_COMPLETED"
            ):

                current_value = activities

            elif requirement_type == (
                "STREAK_DAYS"
            ):

                current_value = streak

            elif requirement_type == (
                "TOTAL_POINTS"
            ):

                current_value = points

            if current_value >= requirement_value:

                newly_earned.append(
                    achievement
                )

        # Save newly earned achievements

        if newly_earned:

            insert_query = text("""
                INSERT INTO
                    education.student_achievements
                (
                    user_id,
                    achievement_id,
                    progress
                )
                VALUES
                (
                    :user_id,
                    :achievement_id,
                    100
                )
                ON CONFLICT
                (
                    user_id,
                    achievement_id
                )
                DO NOTHING
            """)

            with engine.begin() as connection:

                for achievement in newly_earned:

                    connection.execute(
                        insert_query,
                        {
                            "user_id": user_id,

                            "achievement_id":
                                achievement["id"]
                        }
                    )

        return newly_earned

    # ========================================================
    # UPDATE GAMIFICATION SUMMARY
    # ========================================================

    def update_summary(
        self,
        user_id,
        points,
        level,
        streak
    ):

        query = text("""
            INSERT INTO
                education.student_gamification
            (
                user_id,
                total_points,
                current_level,
                current_streak,
                longest_streak,
                achievements_count,
                updated_at
            )
            VALUES
            (
                :user_id,
                :points,
                :level,
                :streak,
                :streak,
                0,
                CURRENT_TIMESTAMP
            )
            ON CONFLICT (user_id)
            DO UPDATE SET

                total_points =
                    EXCLUDED.total_points,

                current_level =
                    EXCLUDED.current_level,

                current_streak =
                    EXCLUDED.current_streak,

                longest_streak =
                    GREATEST(
                        education.student_gamification
                        .longest_streak,
                        EXCLUDED.longest_streak
                    ),

                updated_at =
                    CURRENT_TIMESTAMP
        """)

        with engine.begin() as connection:

            connection.execute(
                query,
                {
                    "user_id": user_id,
                    "points": points,
                    "level": level,
                    "streak": streak
                }
            )

    # ========================================================
    # COMPLETE GAMIFICATION PROCESS
    # ========================================================

    def process_student(
        self,
        user_id
    ):

        points = self.calculate_points(
            user_id
        )

        level = self.calculate_level(
            points
        )

        streak = self.calculate_streak(
            user_id
        )

        achievements = (
            self.evaluate_achievements(
                user_id,
                points,
                streak
            )
        )

        self.update_summary(
            user_id,
            points,
            level,
            streak
        )

        return {

            "user_id": user_id,

            "total_points": points,

            "level": level,

            "current_streak": streak,

            "new_achievements": [

                {
                    "id": str(
                        achievement["id"]
                    ),

                    "name":
                        achievement["name"],

                    "points":
                        achievement["points"],

                    "difficulty":
                        achievement["difficulty"]
                }

                for achievement
                in achievements

            ]
        }


gamification_service = GamificationService()