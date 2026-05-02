from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app.config import settings

# ===== ENGINE =====
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={'check_same_thread': False} # нужно для SQLite, для других БД может быть не нужно
)

# ===== SESSION =====
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# ===== BASE MODEL =====
class Base(DeclarativeBase):
    pass

# ===== DEPENDENCY =====
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()