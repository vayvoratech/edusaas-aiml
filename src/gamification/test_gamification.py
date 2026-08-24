from src.gamification.gamification_service import (
    gamification_service
)


if __name__ == "__main__":

    # Replace with an existing user UUID
    USER_ID = "5a248b38-e21a-4ee2-8b4b-3b3b2fac9dca"

    print(
        "\n=========================================="
    )

    print(
        "EduSaaS Gamification Test"
    )

    print(
        "==========================================\n"
    )

    result = gamification_service.process_student(
        USER_ID
    )

    print(
        "Gamification Result:\n"
    )

    print(result)