# -----------------------------------------
# Adaptive Quiz Weighted Scoring
# -----------------------------------------

DIFFICULTY_WEIGHTS = {
    "EASY": 1.0,
    "AVERAGE": 2.0,
    "HARD": 3.0,
    "DIFFICULT": 4.0
}


def calculate_score(
    difficulty,
    is_correct,
    response_time_seconds
):

    difficulty = difficulty.upper()

    if difficulty not in DIFFICULTY_WEIGHTS:
        raise ValueError(
            f"Invalid difficulty: {difficulty}"
        )

    # Incorrect answer = 0 score
    if not is_correct:
        return 0.0

    base_score = DIFFICULTY_WEIGHTS[difficulty]

    # --------------------------------
    # Speed Bonus
    # --------------------------------

    if response_time_seconds <= 30:

        speed_multiplier = 1.20

    elif response_time_seconds <= 60:

        speed_multiplier = 1.10

    else:

        speed_multiplier = 1.00

    final_score = (
        base_score
        * speed_multiplier
    )

    return round(final_score, 2)


# -----------------------------------------
# Calculate Percentage
# -----------------------------------------

def calculate_percentage(
    earned_score,
    maximum_score
):

    if maximum_score == 0:
        return 0.0

    percentage = (
        earned_score
        / maximum_score
    ) * 100

    return round(percentage, 2)


# -----------------------------------------
# Quick Testing
# -----------------------------------------

if __name__ == "__main__":

    tests = [

        ("EASY", True, 20),

        ("AVERAGE", True, 40),

        ("HARD", True, 55),

        ("DIFFICULT", True, 80),

        ("HARD", False, 30)

    ]

    for difficulty, correct, time_taken in tests:

        score = calculate_score(
            difficulty,
            correct,
            time_taken
        )

        print(
            f"{difficulty} | "
            f"Correct: {correct} | "
            f"Time: {time_taken}s "
            f"→ Score: {score}"
        )