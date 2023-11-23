from pydantic import BaseModel


class QuestionCreate(BaseModel):
    text: str


class InteractionDelete(BaseModel):
    id: str


class UserBase(BaseModel):
    id: str
    email: str
    username: str
    hashed_password: str
    tags: str


class UserLogin(BaseModel):
    email: str
    password: str


class UserUpdate(BaseModel):
    tags: str


class UserCreate(BaseModel):
    username: str
    email: str
    password: str
