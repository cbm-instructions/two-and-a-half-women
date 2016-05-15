#!/usr/bin/python3 
from declare import User, Base, Question, Questionary
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine('sqlite:///qube.db')
Base.metadata.bind = engine

DBSession = sessionmaker()
DBSession.bind = engine

session = DBSession()
all_user = session.query(User).all()
print(all_user[0].nickname)
