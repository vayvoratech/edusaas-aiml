from flask import Blueprint, request, jsonify
from services.adaptive_engine import AdaptiveEngine

quiz_bp = Blueprint("quiz", __name__)

engine = AdaptiveEngine()


# ----------------------------------------------------
# Create Quiz State
# ----------------------------------------------------
@quiz_bp.route("/create-state", methods=["POST"])
def create_state():

    data = request.get_json()

    if not data:
        return jsonify({
            "success": False,
            "message": "Request body is required."
        }), 400

    if "session_id" not in data or "skill" not in data:
        return jsonify({
            "success": False,
            "message": "session_id and skill are required."
        }), 400

    state = engine.create_quiz_state(
        data["session_id"],
        data["skill"]
    )

    return jsonify({
        "success": True,
        "state": state
    })


# ----------------------------------------------------
# Get Next Question
# ----------------------------------------------------
@quiz_bp.route("/next-question", methods=["POST"])
def next_question():

    data = request.get_json()

    if not data:
        return jsonify({
            "success": False,
            "message": "Request body is required."
        }), 400

    if "state" not in data or "questions" not in data:
        return jsonify({
            "success": False,
            "message": "state and questions are required."
        }), 400

    question = engine.get_next_question(
        data["state"],
        data["questions"]
    )

    return jsonify({
        "success": True,
        "question": question
    })


# ----------------------------------------------------
# Submit Answer
# ----------------------------------------------------
@quiz_bp.route("/submit-answer", methods=["POST"])
def submit_answer():

    data = request.get_json()

    if not data:
        return jsonify({
            "success": False,
            "message": "Request body is required."
        }), 400

    required = [
        "state",
        "question",
        "selected_option"
    ]

    for field in required:

        if field not in data:

            return jsonify({
                "success": False,
                "message": f"{field} is required."
            }), 400

    result = engine.submit_answer(
        data["state"],
        data["question"],
        data["selected_option"]
    )

    return jsonify({
        "success": True,
        "result": result
    })


# ----------------------------------------------------
# Calculate Skill Score
# ----------------------------------------------------
@quiz_bp.route("/calculate-score", methods=["POST"])
def calculate_score():

    data = request.get_json()

    if not data or "state" not in data:

        return jsonify({
            "success": False,
            "message": "state is required."
        }), 400

    result = engine.calculate_skill_score(
        data["state"]
    )

    return jsonify({
        "success": True,
        "result": result
    })


# ----------------------------------------------------
# Get Next Skill
# ----------------------------------------------------
@quiz_bp.route("/next-skill", methods=["POST"])
def next_skill():

    data = request.get_json()

    if not data:

        return jsonify({
            "success": False,
            "message": "Request body is required."
        }), 400

    if (
        "skills" not in data
        or
        "current_skill_index" not in data
    ):

        return jsonify({
            "success": False,
            "message": "skills and current_skill_index are required."
        }), 400

    result = engine.get_next_skill(
        data["skills"],
        data["current_skill_index"]
    )

    return jsonify({
        "success": True,
        "result": result
    })


# ----------------------------------------------------
# Finish Quiz
# ----------------------------------------------------
@quiz_bp.route("/finish", methods=["POST"])
def finish_quiz():

    data = request.get_json()

    if not data or "state" not in data:

        return jsonify({
            "success": False,
            "message": "state is required."
        }), 400

    result = engine.finish_quiz(
        data["state"]
    )

    return jsonify({
        "success": True,
        "result": result
    })