from sqlalchemy import create_engine, text

from core.db.config import settings

engine = create_engine(
    url=settings.DATABASE_URL,
    echo=False
)
