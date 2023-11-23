from database import Base
from sqlalchemy import Integer, Column, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship


class Interaction(Base):
    __tablename__ = "interactions"

    id = Column(String, primary_key=True, index=True)
    question = Column(String)
    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="items")
    answer = Column(String)


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True)
    username = Column(String)
    email = Column(String)
    hashed_password = Column(String)

    items = relationship("Interaction", back_populates="owner")
