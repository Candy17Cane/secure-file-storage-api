from datetime import datetime

from sqlalchemy import String, Integer, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


# ===== USER =====
class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    username: Mapped[str] = mapped_column(String, unique=True, index=True)
    email: Mapped[str] = mapped_column(String, unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String)

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )

    # связь с файлами
    files = relationship('File', back_populates='owner')

# ===== FILE =====
class File(Base):
    __tablename__ = 'files'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    owner_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey('users.id'),
        nullable=False
    )

    original_filename: Mapped[str] = mapped_column(String)
    stored_filename: Mapped[str] = mapped_column(String)

    file_size: Mapped[int] = mapped_column(Integer)
    mime_type: Mapped[str] = mapped_column(String)

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )

    # крипто-данные
    salt: Mapped[str] = mapped_column(String)
    nonce: Mapped[str] = mapped_column(String)

    # связь с пользователем
    owner = relationship('User', back_populates='files')