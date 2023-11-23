from fastapi import FastAPI
import openai
from schemas import QuestionCreate, InteractionDelete
from models import Interaction
from sqlalchemy.orm import Session
from fastapi import FastAPI, Depends, HTTPException, status
from database import SessionLocal, Base, engine, get_data
from fastapi.middleware.cors import CORSMiddleware
from uuid import uuid4
from datetime import date
from routes import router

Base.metadata.create_all(bind=engine)

origins = [
    "http://localhost",
    "http://localhost:8081",
    "http://localhost:8082"
    "http://localhost:3000",
]

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# this is for study purposes. In a real app store your api_key in an environment file 
openai.api_key = "your_api_key"

app.include_router(router)


@app.get("/api/interactions")
def fetch_interactions(db: Session = Depends(get_data)):
    return db.query(Interaction).all()


@app.post('/question')
async def ask_question(question: QuestionCreate, db: Session = Depends(get_data)):
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=question.text,
        max_tokens=256
    )
    answer = response.choices[0].text.strip()
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
