from sqlalchemy import create_engine

# PostgreSQL Configuration
DB_USER = "postgres"
DB_PASSWORD = "Chinnu123"   
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "eduai_db"

DATABASE_URL = (
    f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

engine = create_engine(DATABASE_URL)

try:
    with engine.connect():
        print("✅ Connected to PostgreSQL successfully!")
except Exception as e:
    print("❌ Connection Failed")
    print(e)