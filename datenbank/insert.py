from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
 
from declare import Question, Questionary, User, Base
 
engine = create_engine('sqlite:///qube.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine
 
DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()

new_questionary = Questionary(name='Marktplatz - Fragen',
                        category='Sonstiges',
                        lecture='CBM')
session.add(new_questionary)
session.commit()
 
new_question = Question(name='Was ist eine If-Schleife?',
                   correct_answer='Das gibt es nicht',
                   answer_one='Ein Halsband',
                   answer_two='Das gibt es nicht',
                   answer_three='Eine Mischung aus if Abfrage und for Schleife',
                   answer_four='Das gleiche wie eine if Abfrage',
                   info='Das gibt es nicht! Merk es dir!',
                   questionary=new_questionary)
session.add(new_question)
session.commit()

johannes = User(nickname='Johannes',
                email='weber.johanes@gmail.com')
session.add(johannes)
session.commit()

tugba = User(nickname='Tugba')
session.add(tugba)
session.commit()

patric = User(nickname='Patric')
session.add(patric)
session.commit()
