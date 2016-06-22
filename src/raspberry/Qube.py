#!/usr/bin/python3
################
#  Port Detection
import serial
for com in range(0,4):
  try:
    PORT = '/dev/ttyACM'+str(com)
    BAUD = 9600
    board = serial.Serial(PORT,BAUD)
    board.close()
    break
  except:
    pass
########

from PyQt4 import QtCore, QtGui, uic, Qt
import RPi.GPIO as GPIO
import time
from database.declare import User, Base, Question, Questionary
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import update
import os
import random

#set variables for communication with arduino over usb serial
DEVICE = '/dev/ttyACM'+str(com)
BAUD = 9600
ser = serial.Serial(DEVICE, BAUD)

GPIO.setmode(GPIO.BOARD)

#define buttons and leds
one_player_button = 12
two_player_button = 11
navi_button = 13
buzzer_one = 15
buzzer_two = 31
green_button = 16
blue_button = 22
red_button = 18
yellow_button = 29

#setup buttons and leds
GPIO.setup(one_player_button, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(two_player_button, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(navi_button, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(buzzer_one, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(buzzer_two, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(green_button, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(blue_button, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(red_button, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(yellow_button, GPIO.IN, pull_up_down = GPIO.PUD_UP)

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

        self.showFullScreen()

        self.start_new_game()

### ON PRESS METHODS ###
    def on_buzzer_press(self, channel):
        print("Buzzer pressed")
        print(channel)
        print(self.buzzer_mode)
        if (self.currentWidget() == self.question_view and self.buzzer_mode == True):
            if (channel == buzzer_one):
                print("Player One's turn")
                #turn buzzer one led on
                self.sendToArduino("3")
                self.buzzer_player = self.player_one
            elif (channel == buzzer_two):
                print("Player Two's turn")
                #turn buzzer two led on
                self.sendToArduino("4")
                self.buzzer_player = self.player_two
            self.buzzer_mode = False
            print ("Buzzer Mode finished")
            self.player_labels_visible(False)
            self.countdown_lcd.show()
            self.start_countdown()

    def on_answer_button_press(self, channel):
        answer = "Default Answer"
        print("colored Button pressed")
        print(channel)
        #turn buzzer leds off
        self.sendToArduino("5")
        if (self.currentWidget() == self.number_view):
            print("Number pressed")
            if (channel == green_button):
                print("Green pressed")
                self.number_questions = int(self.green_number_label.text())
                self.highlight_number_label("green")
            elif(channel == red_button):
                print("Red pressed")
                self.number_questions = int(self.red_number_label.text())
                self.highlight_number_label("red")
            elif (channel == blue_button):
                print("Blue pressed")
                self.number_questions = int(self.blue_number_label.text())
                self.highlight_number_label("blue")
            elif(channel == yellow_button):
                print("Yellow pressed")
                self.number_questions = int(self.yellow_number_label.text())
                self.highlight_number_label("yellow")
        if(self.currentWidget() == self.question_view and self.buzzer_mode == False and self.answer_pressed == False):                           
            print("Answer pressed")
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

    def on_navi_press(self, channel):
        print("Navi pressed")
        print(channel)
        if (self.currentWidget() == self.introduction_view):
            #set player mode
            if (self.one_player_mode == False):
                print("Two Player Mode")
                self.buzzer_mode = True
                print ("Buzzer Mode started")
            self.setCurrentWidget(self.number_view)
            self.show_number_view()
        elif (self.currentWidget() == self.question_view and self.answer_pressed == True):
            if (self.question_counter == self.number_questions):
                self.setCurrentWidget(self.end_view)
                self.show_end_view()
            else:
                self.next_question_label.hide()
                self.info_label.hide()
                self.show_question()
                self.answer_labels_visible(True)
        elif (self.currentWidget() == self.end_view):
            self.start_new_game()
        elif (self.currentWidget() == self.number_view):
            try:
                self.number_questions
            except:
                print("Please select a Number")
            else:
                self.setCurrentWidget(self.question_view)
                self.show_question()
          
    def on_player_press(self, channel):
        print("Player Button pressed")
        print(channel)
        if (self.currentWidget() == self.home_view):
            if (channel == one_player_button):
                print ("One Player Pressed")
                self.one_player_mode = True
                self.buzzer_mode = False
                print(self.one_player_mode)
            elif (channel == two_player_button):
                print ("Two Player Pressed")
                self.one_player_mode = False
                print(self.one_player_mode)
                self.buzzer_mode = True
            self.get_user()
            self.setCurrentWidget(self.introduction_view)

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
                #turn buzzer one led on
                self.sendToArduino("4")
            else:
                self.buzzer_player = self.player_one
                #turn buzzer two led on
                self.sendToArduino("3")
                
    def stop_timer(self):
        self.timer.stop()
        self.countdown_lcd.hide()
        self.player_labels_visible(True)

### SHOW METHODS ###
    def show_question(self):
        print("Show Question")
        #reset to default labels
        self.reset_question_view()
        
        print("Question Counter vor")
        print(self.question_counter)

        self.index_list = random.sample(range(0,self.total_questions),self.number_questions);

        #set Question Name
        self.current_question = self.questions[self.index_list[self.question_counter]]
        self.question_title_label.setText("Question " + str(self.question_counter + 1) + ": " + self.current_question.name)

        #set Answers
        self.red_answer_label.setText(self.current_question.answer_red)
        self.blue_answer_label.setText(self.current_question.answer_blue)
        self.green_answer_label.setText(self.current_question.answer_green)
        self.yellow_answer_label.setText(self.current_question.answer_yellow)

        self.question_counter += 1
        print("Question Counter nach")
        print(self.question_counter)
        
    def show_end_view(self):
        #show disco light
        self.sendToArduino("2")
        winner_name = "Placeholder"
        #show all neccessary labels
        self.show_end_points_labels()
        #display points
        self.end_player_one_lcd.display(self.player_one_score)
        self.end_title_label.setText("Congratulations. You made it.")
        if (self.one_player_mode == False):
            self.end_player_two_lcd.display(self.player_two_score)
            #calculate the winner
            if(self.player_one_score < self.player_two_score):
                #set winner label
                winner_name = self.player_two.nickname
                #answer_labels_visible(True)
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
        #show all neccessary labels
        #hide all labels from question view
        self.countdown_lcd.hide()
        self.answer_labels_visible(False)
        #stop timer if it is still active
        if (self.timer.isActive() == True):
            self.stop_timer()
        #show info
        #info = self.current_question.info
        #self.info_label.setText(info)
        #self.info_label.show()
        #show next question label/button
        self.next_question_label.show()
        self.next_question_text_label.show()
        #validate answer
        correct_answer = self.current_question.correct_answer
        print("Correct Answer: " + correct_answer)
        if (correct_answer == answer):
            #blink green
            self.sendToArduino("1")
            #set Title
            self.question_title_label.setText("Correct")
            self.question_title_label.setStyleSheet('QLabel#question_title_label {color: green}')
            self.set_points()
        else:
            #blink red
            self.sendToArduino("0")
            #set Title
            self.question_title_label.setText("Wrong")
            self.question_title_label.setStyleSheet('QLabel#question_title_label {color: red}')

    def show_number_view(self):
        self.get_questionaries()

        self.questions = self.current_questionary.questions
        self.total_questions = len(self.questions)
        print(self.total_questions)
        number_yellow = self.total_questions
        number_green = int(self.total_questions  * 0.75)
        number_blue = int(self.total_questions  * 0.5)
        number_red = int(self.total_questions  * 0.25)
        
        string_number_yellow = str(number_yellow)
        string_number_green = str(number_green)
        string_number_blue = str(number_blue)
        string_number_red = str(number_red)

        #set Number Labels
        self.yellow_number_label.setText(string_number_yellow)
        self.green_number_label.setText(string_number_green)
        self.blue_number_label.setText(string_number_blue)
        self.red_number_label.setText(string_number_red)

### HELPER METHODS ###
    def highlight_number_label(self, color):
      self.green_number_label.setStyleSheet("font-weight: normal; font-size: 16px")
      self.red_number_label.setStyleSheet("font-weight: normal; font-size: 16px")
      self.blue_number_label.setStyleSheet("font-weight: normal; font-size: 16px")
      self.yellow_number_label.setStyleSheet("font-weight: normal; font-size: 16px")
      if (color == "green"):
        self.green_number_label.setStyleSheet("font-weight: bold; font-size: 50px")
      if (color == "red"):
        self.red_number_label.setStyleSheet("font-weight: bold; font-size: 50px")
      if (color == "blue"):
        self.blue_number_label.setStyleSheet("font-weight: bold; font-size: 50px")
      if (color == "yellow"):
        self.yellow_number_label.setStyleSheet("font-weight: bold; font-size: 50px")
        
    def set_points(self):
        if (self.one_player_mode == True):
            self.player_one_score += 1
        else:
            if(self.buzzer_player == self.player_one):
                self.player_one_score += 1
            elif(self.buzzer_player == self.player_two):
                self.player_two_score += 1
        self.update_player_labels()
        
    #sends a number to arduino to control the lights
    def sendToArduino(self, number):
        print("Sending Number " + number + " to Arduino")
        ser.write(number.encode())  
             
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
            self.on_navi_press(button)
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
          
    def player_labels_visible(self, visible):
        #hide every label
        self.player_one_label.hide()
        self.player_two_label.hide()
        self.player_one_lcd.hide()
        self.player_two_lcd.hide()
        if(visible == True):
            #show player labels and score
            self.player_one_label.show()
            self.player_one_lcd.show()
            if(self.one_player_mode == False):
                self.player_two_label.show()
                self.player_two_lcd.show()

    def show_end_points_labels(self):
        print("Toggle End Labels")
        print("One Player Mode")
        print(self.one_player_mode)
        print("Erst mal nur Player One LCD und label anzeigen")
        self.end_player_one_label.show()
        self.end_player_one_lcd.show()
        #show player labels
        if(self.one_player_mode == False):
            print("Ok ich zeige auch Player Two an")
            self.end_player_two_label.show()
            self.end_player_two_lcd.show()
        else:
            print("Jetzt versetcke ich Player Two")
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

    #method reset every variable to its default value
    def start_new_game(self):
        self.one_player_mode = False
        self.buzzer_mode = False
        self.answer_pressed = False
        
        self.question_counter = 0
        self.total_questions = 0
        self.player_one_score = 0
        self.player_two_score = 0
        self.timer_start_value = 4

        self.question_title_label.setStyleSheet('QLabel#question_title_label {color: black}')

        #set all labels to default
        self.countdown_lcd.hide()
        self.info_label.hide()
        self.next_question_label.hide()
        self.update_player_labels()
        self.show_end_points_labels()
        self.answer_labels_visible(True)
        self.player_two_label.show()
        self.player_two_lcd.show()
        self.highlight_number_label("black")
        
        #go to home screen
        self.setCurrentWidget(self.home_view)

    def reset_question_view(self):
        self.player_labels_visible(True)
        self.timer_start_value = 5
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
        self.player_one = users[0]
        if(self.one_player_mode == False):
            self.player_two = users[1]
        self.set_player_labels()

if __name__ == '__main__':
    app = QtGui.QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()
