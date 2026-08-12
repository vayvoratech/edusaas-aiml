DIFFICULTY_LEVELS = [
    "EASY",
    "AVERAGE",
    "HARD",
    "DIFFICULT"
]

QUESTIONS_PER_LEVEL = 4


def get_next_difficulty(
    current_difficulty,
    correct_answers,
    total_questions
):

    current_difficulty = current_difficulty.upper()

    if current_difficulty not in DIFFICULTY_LEVELS:
        raise ValueError(
            f"Invalid difficulty: {current_difficulty}"
        )

    if total_questions == 0:
        return current_difficulty

    accuracy = (
        correct_answers / total_questions
    ) * 100

    current_index = DIFFICULTY_LEVELS.index(
        current_difficulty
    )

    # 75% or more → move up
    if accuracy >= 75:

        if current_index < len(DIFFICULTY_LEVELS) - 1:

            return DIFFICULTY_LEVELS[
                current_index + 1
            ]

        return "COMPLETED"

    # 50–74% → stay at same level
    elif accuracy >= 50:

        return current_difficulty

    # Below 50% → move down
    else:

        if current_index > 0:

            return DIFFICULTY_LEVELS[
                current_index - 1
            ]

        return "EASY"


if __name__ == "__main__":

    tests = [
        ("EASY", 4, 4),
        ("AVERAGE", 3, 4),
        ("HARD", 2, 4),
        ("HARD", 1, 4),
        ("DIFFICULT", 4, 4)
    ]

    for difficulty, correct, total in tests:

        result = get_next_difficulty(
            difficulty,
            correct,
            total
        )

        print(
            f"{difficulty} | "
            f"{correct}/{total} correct "
            f"→ {result}"
        )