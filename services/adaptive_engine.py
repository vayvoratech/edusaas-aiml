from copy import deepcopy
import random


class AdaptiveEngine:
    """
    Pure Adaptive Quiz Engine.

    This class contains only AI logic.
    It has no database interaction and no Flask dependencies.

    Node.js is responsible for:
        - Reading questions from PostgreSQL
        - Reading quiz state
        - Saving quiz state
        - Saving student answers
        - Saving skill results
    """

    def __init__(self):

        # Difficulty Levels
        self.EASY = 1
        self.MEDIUM = 2
        self.HARD = 3
        self.VERY_HARD = 4

        #Assessment Types
        self.INITIAL = "INITIAL"
        self.FINAL = "FINAL"

        # Questions per skill
        self.MAX_QUESTIONS = 10

        # Marks for each difficulty
        self.DIFFICULTY_MARKS = {
            self.EASY: 1,
            self.MEDIUM: 2,
            self.HARD: 3,
            self.VERY_HARD: 4
        }

    # ----------------------------------------------------
    # Create Initial Quiz State
    # ----------------------------------------------------
    def create_quiz_state(
            self,
            session_id: int,
            skill: dict,
            assessment_type: str = "INITIAL"
        ) -> dict:

            assessment_type = assessment_type.upper()

            if assessment_type not in (
                self.INITIAL,
                self.FINAL
            ):
                raise ValueError(
                    f"Invalid assessment_type: {assessment_type}"
                )

            starting_difficulty = (
                self.MEDIUM
                if assessment_type == self.FINAL
                else self.EASY
            )

            return {

                "session_id": session_id,

                "skill_id": skill["skill_id"],

                "skill_name": skill["skill_name"],

                "assessment_type": assessment_type,

                "current_difficulty": starting_difficulty,

                "correct_streak": 0,

                "wrong_streak": 0,

                "questions_answered": 0,

                "obtained_score": 0,

                "maximum_score": 0,

                "asked_questions": []

            }

    # ----------------------------------------------------
    # Update Difficulty
    # ----------------------------------------------------
    def update_difficulty(
        self,
        state: dict,
        is_correct: bool
    ) -> dict:

        state = deepcopy(state)

        assessment_type = state.get(
            "assessment_type",
            self.INITIAL
        ).upper()

        if assessment_type == self.FINAL:

            minimum_difficulty = self.MEDIUM
            maximum_difficulty = self.VERY_HARD

        else:

            minimum_difficulty = self.EASY
            maximum_difficulty = self.HARD

        if is_correct:

            state["correct_streak"] += 1
            state["wrong_streak"] = 0

        else:

            state["wrong_streak"] += 1
            state["correct_streak"] = 0

        # ------------------------------------------------
        # Move Up
        # ------------------------------------------------
        if (
            state["correct_streak"] >= 2
            and state["current_difficulty"] < maximum_difficulty
        ):

            state["current_difficulty"] += 1
            state["correct_streak"] = 0

        # ------------------------------------------------
        # Move Down
        # ------------------------------------------------
        elif (
            state["wrong_streak"] >= 2
            and state["current_difficulty"] > minimum_difficulty
        ):

            state["current_difficulty"] -= 1
            state["wrong_streak"] = 0

        return state

    # ----------------------------------------------------
    # Check Skill Completion
    # ----------------------------------------------------
    def is_skill_completed(self, state: dict) -> bool:

        return state["questions_answered"] >= self.MAX_QUESTIONS

    # ----------------------------------------------------
    # Get Next Question
    # ----------------------------------------------------
    def get_next_question(
    self,
    state: dict,
    questions: list
) -> dict | None:
        difficulty = state["current_difficulty"]
        asked_questions = set(state["asked_questions"])
        available_questions = [
            question
            for question in questions
            if (
                question["difficulty_id"] == difficulty
                and question["question_id"] not in asked_questions
            )

        ]

    # If none are available at the current difficulty,
    # use any remaining unanswered question.
        if not available_questions:
            available_questions = [
                question
                for question in questions
                if question["question_id"] not in asked_questions

         ]

        if not available_questions:
            return None

        return deepcopy(random.choice(available_questions))

    # ----------------------------------------------------
    # Submit Answer
    # ----------------------------------------------------
    def submit_answer(
            self,
            state: dict,
            question: dict,
            selected_option: str
        ) -> dict:

            state = deepcopy(state)

            is_correct = (
                selected_option.upper()
                ==
                question["correct_option"].upper()
            )

            marks = question["marks"]

            state["questions_answered"] += 1

            state["maximum_score"] += marks

            # Add question only once
            if question["question_id"] not in state["asked_questions"]:
                state["asked_questions"].append(
                    question["question_id"]
                )

            if is_correct:
                state["obtained_score"] += marks

            state = self.update_difficulty(
                state,
                is_correct
            )

            return {

                "is_correct": is_correct,

                "marks_awarded": marks if is_correct else 0,

                "current_difficulty": state["current_difficulty"],

                "skill_completed": self.is_skill_completed(state),

                "updated_state": state

            }

    # ----------------------------------------------------
    # Calculate Skill Score
    # ----------------------------------------------------
    def calculate_skill_score(
        self,
        state: dict
    ) -> dict:

        maximum_score = state["maximum_score"]

        obtained_score = state["obtained_score"]

        if maximum_score == 0:

            percentage = 0

        else:

            percentage = round(

                (obtained_score / maximum_score) * 100,

                2

            )

        if percentage >= 90:

            skill_level = 5

        elif percentage >= 70:

            skill_level = 4

        elif percentage >= 50:

            skill_level = 3

        elif percentage >= 25:

            skill_level = 2

        else:

            skill_level = 1

        return {

            "session_id": state["session_id"],

            "skill_id": state["skill_id"],

            "skill_name": state["skill_name"],

            "questions_answered": state["questions_answered"],

            "obtained_score": obtained_score,

            "maximum_score": maximum_score,

            "percentage": percentage,

            "skill_level": skill_level,

            "status": "Completed"

        }

    # ----------------------------------------------------
    # Get Next Skill
    # ----------------------------------------------------
    def get_next_skill(
        self,
        skills: list,
        current_skill_index: int
    ) -> dict | None:

        next_index = current_skill_index + 1

        if next_index >= len(skills):
            return None

        return {

            "next_skill_index": next_index,

            "next_skill": skills[next_index]

        }

    # ----------------------------------------------------
    # Finish Quiz
    # ----------------------------------------------------
    def finish_quiz(
        self,
        state: dict
    ) -> dict:

        return {

            "assessment_completed": True,

            "completed_skill": self.calculate_skill_score(
                state
            )

        }
        
        
        






