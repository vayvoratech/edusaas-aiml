import os

from dotenv import load_dotenv

load_dotenv()


class Settings:

    # ==========================================
    # Database Configuration
    # ==========================================

    DB_USER = os.getenv("DB_USER")

    DB_PASSWORD = os.getenv("DB_PASSWORD")

    DB_HOST = os.getenv("DB_HOST")

    DB_PORT = os.getenv("DB_PORT")

    DB_NAME = os.getenv("DB_NAME")

    DATABASE_URL = (
        f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}"
        f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )

    # ==========================================
    # API Configuration
    # ==========================================

    API_VERSION = os.getenv(
        "API_VERSION",
        "1.0.0"
    )

    APP_NAME = os.getenv(
        "APP_NAME",
        "EduSaaS AI Platform"
    )

    # ==========================================
    # AI Models
    # ==========================================

    MODEL_VERSION = os.getenv(
        "MODEL_VERSION",
        "1.0.0"
    )

    MODEL_PATH = os.getenv(
        "MODEL_PATH",
        "models/"
    )

    # ==========================================
    # Logging
    # ==========================================

    LOG_LEVEL = os.getenv(
        "LOG_LEVEL",
        "INFO"
    )

    # ==========================================
    # Batch Prediction
    # ==========================================

    MAX_BATCH_SIZE = int(
        os.getenv(
            "MAX_BATCH_SIZE",
            "100"
        )
    )


settings = Settings()