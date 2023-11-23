from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from uuid import uuid4
from fastapi.responses import JSONResponse
from pydantic import EmailStr
from jwt_handler import jwt_decode

from models import User
from schemas import UserLogin, UserCreate
from database import get_data
from jwt_handler import sign_jwt


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth_token")

router = APIRouter()


async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_data)):
    auth_token = jwt_decode(token)

    if not auth_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = db.query(User).filter(User.id == auth_token["user_id"]).first()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


def verify_password(plain_password, hashed_password, user_id):
    if not pwd_context.verify(plain_password, hashed_password):
        return HTTPException(status_code=400, detail="Incorrect email or password")
    return sign_jwt(user_id)


@router.post("/signup")
def create_user(user: UserCreate,  db: Session = Depends(get_data)):
    user_id = str(uuid4())

    if not db.query(User).filter(User.email == user.email).first():
        user_model = User(id=user_id, username=user.username,
                          email=user.email, hashed_password=pwd_context.hash(user.password))
        db.add(user_model)
        db.commit()

        return sign_jwt(user_id)

    return HTTPException(status_code=500, detail="Email already in use.")


@router.post("/auth_token")
def login(user: UserLogin, db: Session = Depends(get_data)):
    user_model = db.query(User).filter(User.email == user.email).first()

    if not user_model:
        return HTTPException(status_code=400, detail="Incorrect email or password")
    return verify_password(user.password, user_model.hashed_password, user_model.id)
