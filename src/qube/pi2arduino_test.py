#!/usr/bin/python
# ardu2Pi.py
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
# Blinks
from tkinter import *
import time
DEVICE = '/dev/ttyACM'+str(com)
BAUD = 9600
ser = serial.Serial(DEVICE, BAUD)
root = Tk()
def one() :
  ser.write('1'.encode())
  return
def zero() :
  ser.write('0'.encode())
  return
def seven() :
  ser.write('7'.encode())
  return
def two() :
  ser.write('2'.encode())
  return
def three() :
  ser.write('3'.encode())
  return
def four() :
  ser.write('4'.encode())
  return
def five() :
  ser.write('5'.encode())
  return
root.title("Arduino im Test")
Label(text="Raspberry Pi Geek 05/2013", fg="#0A116B").pack()
Label(text="RasPi gruesst Arduino!",fg="#0A116B").pack()
Button(text='Richtig', command=one, background="#33D63B", fg="#FFFFFF").pack()
Button(text='Falsch', command=zero, background="#1DE4F2", fg="#FFFFFF").pack()
Button(text='Disco', command=two, background="#DC0F16", fg="#FFFFFF").pack()
Button(text='Player Blue', command=three, background="#DC0F16", fg="#FFFFFF").pack()
Button(text='Player Yellow', command=four, background="#DC0F16", fg="#FFFFFF").pack()
Button(text='Aus', command=five, background="#DC0F16", fg="#FFFFFF").pack()
root.mainloop()
