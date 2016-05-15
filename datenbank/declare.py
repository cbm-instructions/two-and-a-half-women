import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
 
Base = declarative_base()
 
class Questionary(Base):
    __tablename__ = 'questionary'
    id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False)
    lecture = Column(Text)
    category = Column(Text)
    questions = relationship("Question", back_populates="questionary")

class Question(Base):
    __tablename__ = 'question'
    id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False)
    points = Column(Integer, default=1)
    correct_answer = Column(Integer, nullable=False)
    answer_one = Column(Text, nullable=False)
    answer_two = Column(Text, nullable=False)
    answer_three = Column(Text, nullable=False)
    answer_four = Column(Text, nullable=False)
    info = Column(Text)
    questionary_id = Column(Integer, ForeignKey('questionary.id'))
    questionary = relationship("Questionary", back_populates="questions")

class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    nickname = Column(Text, nullable=False)
    email = Column(Text)
    points = Column(Integer, default=0)
 
# Create an engine that stores data in the local directory's
# sqlalchemy_example.db file.
engine = create_engine('sqlite:///qube.db')
 
# Create all tables in the engine. This is equivalent to "Create Table"
# statements in raw SQL.
Base.metadata.create_all(engine)
