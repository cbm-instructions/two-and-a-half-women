#!/usr/bin/python3
from PyQt4 import QtCore, QtGui, uic, Qt
from database.declare import User, Base, Question, Questionary
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

class MainWindow(QtGui.QStackedWidget):
    def __init__(self):
        super(MainWindow, self).__init__()
        uic.loadUi('views/question.ui', self)
        self.setCurrentWidget(self.main_page)


if __name__ == '__main__':
    app = QtGui.QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()
