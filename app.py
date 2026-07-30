from flask import Flask

app = Flask(__name__)

# Secret key (required for Flask sessions)
app.secret_key = "edusaas_secret_key"

# Register Routes
from routes.home import home_bp
from routes.quiz import quiz_bp
from routes.dashboard import dashboard_bp

app.register_blueprint(home_bp)
app.register_blueprint(quiz_bp)
app.register_blueprint(dashboard_bp)

if __name__ == "__main__":
    app.run(debug=True)