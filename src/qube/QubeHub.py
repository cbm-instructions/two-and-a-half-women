#!/usr/bin/python3
from PyQt4 import QtCore, QtGui, uic, Qt
from database.declare import User, Base, Question, Questionary
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
import random

class MainWindow(QtGui.QStackedWidget):
    def __init__(self):
        super(MainWindow, self).__init__()
        uic.loadUi('views/hub.ui', self)
        self.setCurrentWidget(self.main_view)

        #connect to database
        engine = create_engine('sqlite:///database/qube.db')
        Base.metadata.bind = engine
        DBSession = sessionmaker(bind=engine)
        self.session = DBSession()

        #populate combo boxes with database entries
        self.populate_questionary_box()
        self.populate_question_box()
        self.populate_player_box()

        #set buttons for main view - cancel button was set in Qt4Designer
        QtCore.QObject.connect(self.main_create_question_button, QtCore.SIGNAL("clicked()"), self.go_to_create_question)
        QtCore.QObject.connect(self.main_create_questionary_button,QtCore.SIGNAL("clicked()"), self.go_to_create_questionary)
        QtCore.QObject.connect(self.main_create_user_button,QtCore.SIGNAL("clicked()"), self.go_to_create_user)
        QtCore.QObject.connect(self.main_delete_button,QtCore.SIGNAL("clicked()"), self.go_to_delete_center)

        #set buttons for create user view
        QtCore.QObject.connect(self.create_user_cancel_button,QtCore.SIGNAL("clicked()"), self.go_to_main_view)
        QtCore.QObject.connect(self.create_user_create_button,QtCore.SIGNAL("clicked()"), self.create_user)

        #set buttons for create questionary view
        QtCore.QObject.connect(self.create_questionary_cancel_button,QtCore.SIGNAL("clicked()"), self.go_to_main_view)
        QtCore.QObject.connect(self.create_questionary_create_button,QtCore.SIGNAL("clicked()"), self.create_questionary)

        #set buttons for create question view
        QtCore.QObject.connect(self.create_question_cancel_button,QtCore.SIGNAL("clicked()"), self.go_to_main_view)
        QtCore.QObject.connect(self.create_question_create_button,QtCore.SIGNAL("clicked()"), self.create_question)

        #set buttons for delete center view
        QtCore.QObject.connect(self.delete_cancel_button,QtCore.SIGNAL("clicked()"), self.go_to_main_view)
        QtCore.QObject.connect(self.delete_player_button,QtCore.SIGNAL("clicked()"), self.delete_player)
        QtCore.QObject.connect(self.delete_question_button,QtCore.SIGNAL("clicked()"), self.delete_question)
        QtCore.QObject.connect(self.delete_questionary_button,QtCore.SIGNAL("clicked()"), self.delete_questionary)

######## DELETE METHODS ########

    def delete_question(self):
        success = False
        #fetch question from db with selected name
        question_name = self.delete_question_box.currentText()
        question = self.session.query(Question).filter(Question.name == question_name).first()

        self.session.delete(question)

        try:
            self.session.commit()
            success = True
        except Exception as e:
            print(e)
            self.session.rollback()
            self.session.flush()

        if(success == True):
            self.show_message("Question successfully deleted")
            self.populate_question_box()
        
    def delete_questionary(self):
        success = False
        #fetch questionary from db with selected name
        questionary_name = self.delete_questionary_box.currentText()
        questionary = self.session.query(Questionary).filter(Questionary.name == questionary_name).first()

        self.session.delete(questionary)

        try:
            self.session.commit()
            success = True
        except Exception as e:
            print(e)
            self.session.rollback()
            self.session.flush()

        if(success == True):
            self.show_message("Questionary successfully deleted")
            self.populate_questionary_box()

    def delete_player(self):
        success = False
        #fetch player from db with selected name
        player_nickname = self.delete_player_box.currentText()
        player = self.session.query(User).filter(User.nickname == player_nickname).first()

        self.session.delete(player)

        try:
            self.session.commit()
            success = True
        except Exception as e:
            print(e)
            self.session.rollback()
            self.session.flush()

        if(success == True):
            self.show_message("Player successfully deleted")
            self.populate_player_box()

######## CREATE METHODS ########
        
    def create_question(self):
        success = False
        correct_answer = "Placeholder"
        
        #fetch question infos from gui
        name = self.create_question_question_field.text()
        answer_one = self.create_question_answer_one_field.text()
        answer_two = self.create_question_answer_two_field.text()
        answer_three = self.create_question_answer_three_field.text()
        answer_four = self.create_question_answer_four_field.text()
        questionary_name = str(self.create_question_questionary_box.currentText())
        info = self.create_question_info_text.toPlainText()

        print(self.create_question_answer_one_button.isChecked())
        print(self.create_question_answer_two_button.isChecked())
        print(self.create_question_answer_three_button.isChecked())
        print(self.create_question_answer_four_button.isChecked())
        
        #find correct answer
        if(self.create_question_answer_one_button.isChecked() == True):
            correct_answer = answer_one
        elif(self.create_question_answer_two_button.isChecked() == True):
            correct_answer = answer_two
        elif(self.create_question_answer_three_button.isChecked() == True):
            correct_answer = answer_three
        elif(self.create_question_answer_four_button.isChecked() == True):
            correct_answer = answer_four
        print("The correct Answer is :" + correct_answer)

        #shuffle the ansers
        answers = [answer_one, answer_two, answer_three, answer_four]
        random.shuffle(answers)

        #fetch questionary
        questionary = self.session.query(Questionary).filter(Questionary.name == questionary_name).first()

        #save to daatbase
        new_question = Question(name=name,
                                correct_answer=correct_answer,
                                answer_blue=answers[2],
                                answer_red=answers[3],
                                answer_green=answers[0],
                                answer_yellow=answers[1],
                                info=info,
                                questionary=questionary)
        
        self.session.add(new_question)
        
        try:
            self.session.commit()
            success = True
        except Exception as e:
            print(e)
            self.session.rollback()
            self.session.flush()

        if(success == True):
            self.show_message("Question successfully created")
            #clear input
            self.create_question_question_field.clear()
            self.create_question_answer_one_field.clear()
            self.create_question_answer_two_field.clear()
            self.create_question_answer_three_field.clear()
            self.create_question_answer_four_field.clear()
            self.create_question_info_text.clear()

    def create_questionary(self):
        success = False
        
        #get questionary infos from gui
        name = self.create_questionary_name_field.text()
        category = self.create_questionary_category_field.text()
        lecture = self.create_questionary_lecture_field.text()

        #save questionary to database
        new_questionary = Questionary(name=name, category=category)
        self.session.add(new_questionary)
        
        try:
            self.session.commit()
            success = True
        except Exception as e:
            print(e)
            self.session.rollback()
            self.session.flush()

        if(success == True):
            self.show_message("Questionary successfully created")
            #clear input
            self.create_questionary_name_field.clear()
            self.create_questionary_category_field.clear()
            self.create_questionary_lecture_field.clear()
        

    def create_user(self):
        success = False
        
        #get user infos from gui
        nickname = self.create_user_nickname_field.text()
        email = self.create_user_email_field.text()

        #save user to database
        new_user = User(nickname=nickname, email=email)
        self.session.add(new_user)
        
        try:
            self.session.commit()
            success = True
        except Exception as e:
            print(e)
            self.session.rollback()
            self.session.flush()

        if(success == True):
            self.show_message("User successfully created")
            #clear input
            self.create_user_nickname_field.clear()
            self.create_user_email_field.clear()

######## POPULATE METHODS ########

    def populate_questionary_box(self):
        self.delete_questionary_box.clear()
        #fetch questionaries from db
        questionaries = self.session.query(Questionary).all()

        for questionary in questionaries:
            self.create_question_questionary_box.addItem(questionary.name)
            self.delete_questionary_box.addItem(questionary.name)

    def populate_player_box(self):
        self.delete_player_box.clear()
        #fetch players from db
        players = self.session.query(User).all()
        
        for player in players:
            self.delete_player_box.addItem(player.nickname)
        
    def populate_question_box(self):
        self.delete_question_box.clear()
        #fetch question from db
        questions = self.session.query(Question).all()

        for question in questions:
            self.delete_question_box.addItem(question.name)

######## GO TO METHODS ########

    def go_to_main_view(self):
        self.setCurrentWidget(self.main_view)

    def go_to_create_question(self):
        self.setCurrentWidget(self.create_question_view)
    
    def go_to_create_questionary(self):
        self.setCurrentWidget(self.create_questionary_view)

    def go_to_create_user(self):
        self.setCurrentWidget(self.create_user_view)

    def go_to_delete_center(self):
        self.refresh_delete_view()
        self.setCurrentWidget(self.delete_view)

######## HELPER METHODS ########

    def refresh_delete_view(self):
        self.populate_questionary_box()
        self.populate_question_box()
        self.populate_player_box()

    def show_message(self, message):
           message_box = QtGui.QMessageBox()
           message_box.setIcon(QtGui.QMessageBox.Information)
           message_box.setText(message)
           message_box.setWindowTitle("Attention")
           message_box.setStandardButtons(QtGui.QMessageBox.Ok)
           message_box.exec_()
    
if __name__ == '__main__':
    app = QtGui.QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()
