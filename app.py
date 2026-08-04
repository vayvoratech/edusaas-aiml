from flask import Flask
from routes.quiz import quiz_bp

app = Flask(__name__)

app.register_blueprint(
    quiz_bp,
    url_prefix="/api/quiz"
)

print("\nRegistered Routes")

for rule in app.url_map.iter_rules():
    print(rule)

if __name__ == "__main__":
    app.run(debug=True)