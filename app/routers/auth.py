from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth import create_access_token, hash_password, verify_password
from app.config import settings
from app.database import get_db
from app.dependencies import get_current_user
from app.models import User
from app.schemas import Token, UserCreate, UserLogin, UserOut

router = APIRouter(prefix='/auth', tags=['Auth'])


@router.post('/register', response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    existing_user = (
        db.query(User)
        .filter(
            (User.username == user_data.username) | (User.email == user_data.email)
        )
        .first()
    )

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Username or email already exists',
        )
    
    user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hash_password(user_data.password),
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user



@router.post('/login', response_model=Token)
def login(user_data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == user_data.username).first()

    if user is None or not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid username or password'
        )
    
    access_token = create_access_token(
        data={'sub': str(user.id)},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )

    return Token(access_token=access_token)


@router.get('/me', response_model=UserOut)
def me(current_user: User = Depends(get_current_user)):
    return current_user