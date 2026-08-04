from flask import Blueprint

skill_gap_bp = Blueprint("skill_gap", __name__)

@skill_gap_bp.route("/")
def test():
    return {"message": "Skill Gap API Working"}