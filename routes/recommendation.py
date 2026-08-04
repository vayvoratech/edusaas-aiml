from flask import Blueprint

recommendation_bp = Blueprint("recommendation", __name__)

@recommendation_bp.route("/")
def test():
    return {"message": "Recommendation API Working"}