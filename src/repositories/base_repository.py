from sqlalchemy.orm import sessionmaker

from src.database.database_connection import engine


SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


class BaseRepository:

    def get_session(self):

        return SessionLocal()