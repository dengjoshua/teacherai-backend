from openai import OpenAI
from schemas import QuestionCreate, InteractionDelete
from models import Interaction
from sqlalchemy.orm import Session
from fastapi import FastAPI, Depends, HTTPException, status
from database import SessionLocal, Base, engine, get_data
from fastapi.middleware.cors import CORSMiddleware
from uuid import uuid4
from datetime import date
from routes import router
from sqlalchemy.orm import Session
from models import User

from jwt_handler import jwt_decode
from routes import router, oauth2_scheme

Base.metadata.create_all(bind=engine)

origins = [
    "http://localhost",
    "http://localhost:8081",
    "http://localhost:8082"
    "http://localhost:3000",
]

app = FastAPI()

client = OpenAI(api_key="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")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


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


@app.get("/api/interactions")
def fetch_interactions(db: Session = Depends(get_data)):
    return db.query(Interaction).all()


@app.post('/question')
async def ask_question(question: QuestionCreate, db: Session = Depends(get_data)):
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "user",
             "content": question.text
             }
        ]
    )
    answer = response.choices[0].message.content
    interaction_model = Interaction(
        id=str(uuid4()), question=question.text, answer=answer)
    db.add(interaction_model)
    db.commit()

    return db.query(Interaction).all()


@app.delete("/api/interactions")
def delete_interaction(interaction: InteractionDelete, db: Session = Depends(get_data)):
    interaction_model = db.query(Interaction).filter(
        Interaction.id == interaction.id).first()
    db.delete(interaction_model)
    db.commit()

    return db.query(Interaction).all()


@app.get("/api/users")
def get_users(db: Session = Depends(get_data)):
    return db.query(User).all()


@app.get("/users/{id}")
def get_user(id: str, db: Session = Depends(get_data)):
    return db.query(User).filter(User.id == id).first()
