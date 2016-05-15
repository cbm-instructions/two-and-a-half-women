#!/usr/bin/python3
import time  
import RPi.GPIO as GPIO
from PyQt4 import QtCore, QtGui, uic, Qt
from datenbank.declare import User, Base, Question, Questionary
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

GPIO.setmode(GPIO.BOARD)  
red = 11 
green = 13  
blue = 15
button = 16
Freq = 100 #Hz

GPIO.setup(red, GPIO.OUT)  
GPIO.setup(green, GPIO.OUT)  
GPIO.setup(blue, GPIO.OUT)
GPIO.setup(button, GPIO.IN)

#setup all the colours  
RED = GPIO.PWM(red, Freq) #Pin, frequency  
RED.start(0) #Initial duty cycle of 0, so off  
GREEN = GPIO.PWM(green, Freq)    
GREEN.start(0)   
BLUE = GPIO.PWM(blue, Freq)  
BLUE.start(0)

#setup database connection and session
engine = create_engine('sqlite:///datenbank/qube.db')
Base.metadata.bind = engine

DBSession = sessionmaker()
DBSession.bind = engine

class MainWindow(QtGui.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        uic.loadUi('main.ui', self)
        self.show()
        
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_countdown_display)
        self.set_image()
        
        QtCore.QObject.connect(self.pushButton,QtCore.SIGNAL("clicked()"), self.set_label)
        QtCore.QObject.connect(self.rainbow,QtCore.SIGNAL("clicked()"), self.led_on)
        QtCore.QObject.connect(self.exit,QtCore.SIGNAL("clicked()"), self.cleanup)
        QtCore.QObject.connect(self.countdown,QtCore.SIGNAL("clicked()"), self.start_countdown)

        GPIO.add_event_detect(button, GPIO.RISING, callback=self.on_button_press, bouncetime=500)

    def on_button_press(self, channel):
        self.start_countdown()

    def set_image(self):
        myPixmap = QtGui.QPixmap(os.getcwd() + '/hello')
        myPixmap = myPixmap.scaledToWidth(self.image_label.width())
        myPixmap = myPixmap.scaledToHeight(self.image_label.height())
        self.image_label.setPixmap(myPixmap)

    def start_countdown(self):
        self.timer_start_value = 3
        self.counter.display(self.timer_start_value)
        self.timer.start(1000)

    def update_countdown_display(self):
        self.timer_start_value -= 1
        self.counter.display(self.timer_start_value)
        if self.timer_start_value <= 0:
           self.timer.stop()

    
    def set_label(self):
        session = DBSession()
        question_object = session.query(Question).first()
        question = question_object.name
        self.label.setText(question)

    def led_on(self):
        gelb = [255.0, 48.0, 0.0]
        lila = [255.0, 10.0, 200.0]
        indigo = [75.0, 0.0, 130.0]
        aqua = [127.0, 255.0, 255.0]
        hellgrin = [0.0, 205.0, 25.0]
        rot = [255.0, 0.0, 0.0]

        rgb = [(x / 255) * 100 for x in lila]
        self.colour(rgb[0], rgb[1], rgb[2], 1)

        rgb = [(x / 255) * 100 for x in gelb]
        self.colour(rgb[0], rgb[1], rgb[2], 1)

        rgb = [(x / 255) * 100 for x in aqua]
        self.colour(rgb[0], rgb[1], rgb[2], 1)

        rgb = [(x / 255) * 100 for x in hellgrin]
        self.colour(rgb[0], rgb[1], rgb[2], 1)

        rgb = [(x / 255) * 100 for x in rot]
        self.colour(rgb[0], rgb[1], rgb[2], 1)
   
    def colour(self, R, G, B, on_time):  
        #colour brightness range is 0-100  
        RED.ChangeDutyCycle(R)  
        GREEN.ChangeDutyCycle(G)  
        BLUE.ChangeDutyCycle(B)  
        time.sleep(on_time)  
       
        #turn everything off  
        RED.ChangeDutyCycle(0)  
        GREEN.ChangeDutyCycle(0)  
        BLUE.ChangeDutyCycle(0)

    def cleanup(self):
        #Stop all the PWM objects  
        RED.stop()  
        GREEN.stop()  
        BLUE.stop()  
           
        #Tidy up and remaining connections.  
        GPIO.cleanup()     

if __name__ == '__main__':
    app = QtGui.QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()
