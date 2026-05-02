from datetime import datetime
from pydantic import BaseModel, EmailStr

# ===== USER =====

# вход (регистрация)
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

# вход (логин)
class UserLogin(BaseModel):
    username: str
    password: str

# ответ (без пароля!)
class UserOut(BaseModel):
    id: int
    username: str
    email: EmailStr
    created_at: datetime

    class Config:
        from_attributes = True


# ===== TOKEN =====
class Token(BaseModel):
    access_token: str
    token_type: str = 'bearer'


# ===== FILE =====
# ответ по файлу
class FileOut(BaseModel):
    id: int
    original_filename: str
    stored_filename: str
    file_size: int
    mime_type: str
    created_at: datetime

    class Config:
        from_attributes = True