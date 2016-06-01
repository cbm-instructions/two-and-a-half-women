#!/usr/bin/python3
from PyQt4 import QtCore, QtGui, uic, Qt
import RPi.GPIO as GPIO
import time
from database.declare import User, Base, Question, Questionary
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import update
import os

GPIO.setmode(GPIO.BOARD)

one_player_button = 12
two_player_button = 11
navi_button = 13
buzzer_one = 15
buzzer_two = 31
green_button = 16
blue_button = 22
red_button = 18
yellow_button = 29

GPIO.setup(one_player_button, GPIO.IN)
GPIO.setup(two_player_button, GPIO.IN)
GPIO.setup(navi_button, GPIO.IN)
GPIO.setup(buzzer_one, GPIO.IN)
GPIO.setup(buzzer_two, GPIO.IN)
GPIO.setup(green_button, GPIO.IN)
GPIO.setup(blue_button, GPIO.IN)
GPIO.setup(red_button, GPIO.IN)
GPIO.setup(yellow_button, GPIO.IN)

#setup database connection and session
engine = create_engine('sqlite:///database/qube.db')
Base.metadata.bind = engine
DBSession = sessionmaker()
DBSession.bind = engine
        
class MainWindow(QtGui.QStackedWidget):
    #catch a signal from the main thread
    updated = QtCore.pyqtSignal(int)
    
    def __init__(self):
        super(MainWindow, self).__init__()
        #load design from Qt4Designer
        uic.loadUi('views/main.ui', self)

        #receive the signal and call self.button_handler
        self.updated.connect(self.button_handler)
        
        #start Session
        self.session = DBSession()

        #create additional widgets
        self.info_label = QtGui.QLabel(self)
        self.answer_grid_layout.addWidget(self.info_label)

        #set countdown attributes
        self.countdown_lcd = QtGui.QLCDNumber(self)
        self.player_layout.addWidget(self.countdown_lcd)
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_countdown_display)

        #add events to gpio pins
        GPIO.add_event_detect(one_player_button, GPIO.FALLING, callback=self.on_button_press, bouncetime=500)
        GPIO.add_event_detect(two_player_button, GPIO.FALLING, callback=self.on_button_press, bouncetime=500)
        GPIO.add_event_detect(navi_button, GPIO.FALLING, callback=self.on_button_press, bouncetime=500)
        GPIO.add_event_detect(green_button, GPIO.FALLING, callback=self.on_button_press, bouncetime=500)
        GPIO.add_event_detect(blue_button, GPIO.FALLING, callback=self.on_button_press, bouncetime=500)
        GPIO.add_event_detect(red_button, GPIO.FALLING, callback=self.on_button_press, bouncetime=500)
        GPIO.add_event_detect(buzzer_one, GPIO.FALLING, callback=self.on_button_press, bouncetime=500)
        GPIO.add_event_detect(yellow_button, GPIO.FALLING, callback=self.on_button_press, bouncetime=500)
        GPIO.add_event_detect(buzzer_two, GPIO.FALLING, callback=self.on_button_press, bouncetime=500)

        self.start_new_game()

### ON PRESS METHODS ###
    def on_buzzer_press(self, channel):
        print("Buzzer pressed")
        print(self.buzzer_mode)
        if (self.currentWidget() == self.question_view and self.buzzer_mode == True):
            if (channel == buzzer_one):
                print("Player One's turn")
                self.buzzer_player = self.player_one
            elif (channel == buzzer_two):
                print("Player Two's turn")
                self.buzzer_player = self.player_two
            self.buzzer_mode = False
            print ("Buzzer Mode finished")
            self.player_labels_visible(False)
            self.countdown_lcd.show()
            self.start_countdown()

    def on_answer_button_press(self, channel):
        answer = "Default Answer"
        print("Answer pressed")
        if(self.currentWidget() == self.question_view and self.buzzer_mode == False and self.answer_pressed == False):
            if (channel == green_button):
                print("Green pressed")
                answer = self.current_question.answer_green
            elif(channel == red_button):
                print("Red pressed")
                answer = self.current_question.answer_red
            elif (channel == blue_button):
                print("Blue pressed")
                answer = self.current_question.answer_blue
            elif(channel == yellow_button):
                print("Yellow pressed")
                answer = self.current_question.answer_yellow
            print("Logged Answer: " + answer)
            self.answer_pressed = True
            self.show_result(answer)


    #send the signal if a button is pressed
    def on_button_press(self, channel):
        self.updated.emit(channel)

    def on_navi_press(self):
        print("Navi pressed")
        if (self.currentWidget() == self.introduction_view):
            if (self.one_player_mode == False):
                print("Two Player Mode")
                self.buzzer_mode = True
                print ("Buzzer Mode started")
            self.setCurrentWidget(self.question_view)
            self.continue_game()
        elif (self.currentWidget() == self.question_view and self.answer_pressed == True):
            if (self.question_counter == self.total_questions):
                self.setCurrentWidget(self.end_view)
                self.show_end_view()
            else:
                self.next_question_label.hide()
                self.info_label.hide()
                self.show_question()
                self.answer_labels_visible(True)
        elif (self.currentWidget() == self.end_view):
            self.start_new_game()
    
    def on_player_press(self, channel):
        print("Player Button pressed")
        if (self.currentWidget() == self.home_view):
            if (channel == one_player_button):
                print ("One Player Pressed")
                self.one_player_mode = True
                self.buzzer_mode = False
            elif (channel == two_player_button):
                print ("Two Player Pressed")
                self.buzzer_mode = True
            self.get_user()
            self.setCurrentWidget(self.introduction_view)
            self.continue_game()

    ### COUNTDOWN TIMER METHODS ###    
    def start_countdown(self):
        self.countdown_lcd.display(self.timer_start_value)
        self.timer.start(1000)

    def update_countdown_display(self):
        self.timer_start_value -= 1
        self.countdown_lcd.display(self.timer_start_value)
        if self.timer_start_value <= 0:
            self.stop_timer()
            if (self.buzzer_player == self.player_one):
                self.buzzer_player = self.player_two
            else:
                self.buzzer_player = self.player_one
                
    def stop_timer(self):
        self.timer.stop()
        self.countdown_lcd.hide()
        self.player_labels_visible(True)

### SHOW METHODS ###
    def show_question(self):
        #reset to default labels
        self.reset_question_view()
        
        self.questions = self.current_questionary.questions
        self.total_questions = len(self.questions)

        #set Question Name
        self.current_question = self.questions[self.question_counter]
        self.question_number_label.setText("Question " + str(self.question_counter + 1) + ": ")
        self.question_title_label.setText(self.current_question.name)

        #set Answers
        self.red_answer_label.setText(self.current_question.answer_red)
        self.blue_answer_label.setText(self.current_question.answer_blue)
        self.green_answer_label.setText(self.current_question.answer_green)
        self.yellow_answer_label.setText(self.current_question.answer_yellow)

        #hide Player_two labels
        if(self.one_player_mode == True):
            self.player_two_lcd.hide()
            self.player_two_label.hide()

        self.question_counter += 1
        
    def show_end_view(self):
        winner_name = "Placeholder"
        #display points
        self.end_player_one_lcd.display(self.player_one_score)
        self.end_title_label.setText("Congratulations. You made it.")
        if (self.one_player_mode == False):
            self.end_player_two_lcd.display(self.player_two_score)
            #calculate the winner
            if(self.player_one_score < self.player_two_score):
                #set winner label
                winner_name = self.player_two.nickname
                self.end_player_two_label.setStyleSheet('QLabel#en_title_label {color: green}')
                self.end_player_one_label.setStyleSheet('QLabel#en_title_label {color: red}')
            elif(self.player_one_score > self.player_two_score):
                winner_name = self.player_one.nickname
                self.end_player_one_label.setStyleSheet('QLabel#en_title_label {color: green}')
                self.end_player_two_label.setStyleSheet('QLabel#en_title_label {color: red}')
            self.end_title_label.setText("Congratulations " + winner_name + ". You've won.")
            self.end_title_label.setStyleSheet('QLabel#en_title_label {color: green}')
            if (self.player_one_score == self.player_two_score):
                self.end_title_label.setText("Draw")
            #set player two points
            self.player_two.points += self.player_two_score
                
        #set player one points
        self.player_one.points += self.player_one_score
        #save players score to database
        self.session.commit()
            
    def show_result(self, answer):
        self.show_end_points_labels()
        if (self.timer.isActive() == True):
            self.stop_timer()
        self.countdown_lcd.hide()
        self.question_number_label.hide()
        #set info
        self.answer_labels_visible(False)
        #show next question label/button
        self.next_question_label.show()
        self.next_question_text_label.show()
        #show info
        info = self.current_question.info
        self.info_label.setText(info)
        self.info_label.show()
        #validate answer
        correct_answer = self.current_question.correct_answer
        print("Correct Answer: " + correct_answer)
        if (correct_answer == answer):
            #set Title
            self.question_title_label.setText("Correct")
            self.question_title_label.setStyleSheet('QLabel#question_title_label {color: green}')
            self.set_points()
        else:
            #set Title
            self.question_title_label.setText("Wrong")
            self.question_title_label.setStyleSheet('QLabel#question_title_label {color: red}')

    def set_points(self):
        if (self.one_player_mode == True):
            self.player_one_score += 1
        else:
            if(self.buzzer_player == self.player_one):
                self.player_one_score += 1
            elif(self.buzzer_player == self.player_two):
                self.player_two_score += 1
        self.update_player_labels()
        

### HELPER METHODS ###
    def set_player_labels(self):
        print(self.player_one.nickname)
        self.player_one_label.setText(self.player_one.nickname)
        self.end_player_one_label.setText(self.player_one.nickname)
        if (self.one_player_mode == False):
            print(self.player_two.nickname)
            self.player_two_label.setText(self.player_two.nickname)
            self.end_player_two_label.setText(self.player_two.nickname)
        
    def button_handler(self, button):
        buzzer_buttons = [buzzer_one, buzzer_two]
        answer_buttons = [green_button, blue_button, red_button, yellow_button]
        player_buttons = [one_player_button, two_player_button]
        
        if (button == navi_button):
            self.on_navi_press()
        elif button in buzzer_buttons:
            self.on_buzzer_press(button)
        elif button in answer_buttons:
            self.on_answer_button_press(button)
        elif button in player_buttons:
            self.on_player_press(button)
        else:
            print("Button unknown")
            
    def update_player_labels(self):
        self.player_one_lcd.display(self.player_one_score)
        self.player_two_lcd.display(self.player_two_score)

    def continue_game(self):
        if (self.currentWidget() == self.questionary_view):
            self.show_questionary()
        elif (self.currentWidget() == self.question_view):
            #gehört eigenltich in das obere if...aber wir überspringen die questionary_view..vorübergehend...deswegen ist auch die methode gerade so unnötig xD
            self.get_questionaries()
            self.show_question()

    def player_labels_visible(self, visible):
        if(visible == True):
            #show player labels and score
            self.player_one_label.show()
            self.player_one_lcd.show()
            if(self.one_player_mode == False):
                self.player_two_label.show()
                self.player_two_lcd.show()
        else:
            self.player_one_label.hide()
            self.player_two_label.hide()
            self.player_one_lcd.hide()
            self.player_two_lcd.hide()

    def show_end_points_labels(self):
        self.end_player_one_label.show()
        self.end_player_one_lcd.show()
        #show player labels and score
        if(self.one_player_mode == False):
            self.player_two_label.show()
            self.player_two_lcd.show()
        else:
            self.end_player_two_label.hide()
            self.end_player_two_lcd.hide()
            

    def answer_labels_visible(self, visible):
        if(visible == True):
            self.blue_answer_label.show()
            self.green_answer_label.show()
            self.yellow_answer_label.show()
            self.red_answer_label.show()
        else:
            self.blue_answer_label.hide()
            self.green_answer_label.hide()
            self.yellow_answer_label.hide()
            self.red_answer_label.hide()

    #this method reset every variable to its default value
    def start_new_game(self):
        self.one_player_mode = False
        self.buzzer_mode = False
        self.answer_pressed = False
        self.question_counter = 0
        self.total_questions = 0
        self.player_one_score = 0
        self.player_two_score = 0
        self.timer_start_value = 4
        self.countdown_lcd.hide()
        self.info_label.hide()
        self.next_question_label.hide()
        self.question_title_label.setStyleSheet('QLabel#question_title_label {color: black}')
        self.answer_labels_visible(True)
        self.update_player_labels()
        self.question_number_label.show()
        #go to home screen
        self.setCurrentWidget(self.home_view)

    def reset_question_view(self):
        self.question_number_label.show()
        self.timer_start_value = 4
        self.answer_pressed = False
        self.next_question_text_label.hide()
        self.question_title_label.setStyleSheet('QLabel#question_title_label {color: black}')
        if (self.one_player_mode == False):
            self.buzzer_mode = True
        

### DATABASE HELPER ###
    def get_questionaries(self):
        questionaries = self.session.query(Questionary).all()
        self.current_questionary = questionaries[0]

    def get_user(self):
        users = self.session.query(User).all()
        self.player_one = users[2]
        if(self.one_player_mode == False):
            self.player_two = users[1]
        self.set_player_labels()

if __name__ == '__main__':
    app = QtGui.QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()
