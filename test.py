#!/usr/bin/python3
from PyQt4 import QtCore, QtGui, uic, Qt
import RPi.GPIO as GPIO
import time

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

class MainWindow(QtGui.QStackedWidget):
    def __init__(self):
        super(MainWindow, self).__init__()
        uic.loadUi('nav.ui', self)
        self.setCurrentWidget(self.pageOne)
        
        QtCore.QObject.connect(self.weiter,QtCore.SIGNAL("clicked()"), self.weiter_pressed)
        QtCore.QObject.connect(self.zuruck,QtCore.SIGNAL("clicked()"), self.zuruck_pressed)

        GPIO.add_event_detect(button, GPIO.RISING, callback=self.on_button_press, bouncetime=500)

    def on_button_press(self, channel):
        print ("Button pressed")
        if self.currentWidget() == self.pageOne:
            self.weiter_pressed()
        elif self.currentWidget() == self.pageTwo:
            self.led_on()

    def zuruck_pressed(self):
        self.setCurrentWidget(self.pageOne)

    def weiter_pressed(self):
        self.setCurrentWidget(self.pageTwo)

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

if __name__ == '__main__':
    app = QtGui.QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()
