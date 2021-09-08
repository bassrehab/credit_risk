import sys
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtGui import QBrush, QColor 
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from pyqtspinner.spinner import WaitingSpinner
from ui import Ui_MainWindow
import os
from os.path import expanduser
import sys
from PyQt5.Qt import QApplication, QClipboard
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QCheckBox,QMainWindow, QFileDialog, QApplication, QWidget, QPushButton, QAction, QLineEdit, QMessageBox, QPlainTextEdit,QLabel, QFrame
from PyQt5.QtCore import QSize
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSlot
import os, os.path
import cv2
import glob
import copy 
import numpy as np
import json
import io
import codecs
from train import ModelClass
import threading
import  pickle

class MainW (QMainWindow, Ui_MainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.setupUi(self)
        self.pushButton_2.clicked.connect(self.pushButton_2_clicked)
        self.pushButton_13.clicked.connect(self.open_dialog_box2)
        self.listWidget_5.clicked[QtCore.QModelIndex].connect(self.listWidget_5_clicked)
        self.Size_2.valueChanged.connect(self.valuechange_size2)
        self.spinBox.valueChanged.connect(self.valuechange_spinBox)
        self.spinBox_2.valueChanged.connect(self.valuechange_spinBox_2)
        self.doubleSpinBox.valueChanged.connect(self.valuechange_doubleSpinBox)
        self.pushButton_14.clicked.connect(self.pushButton_14_clicked)
        self.listWidget_4.clicked.connect(self.listWidget_4_clicked)
        self.actionOutput_Directory.triggered.connect(self.chooseDirectory)
        self.pushButton_15.clicked.connect(self.pushButton_15_clicked)
        self.pushButton_5.clicked.connect(self.pushButton_5_clicked)
        self.pushButton_6.clicked.connect(self.pushButton_6_clicked)
        self.epochs=10 
        self.batch_size=2
        self.learning_rate=0.00001
        self.pushButton_7.clicked.connect(self.pushButton_7_clicked)
        self.pushButton_9.clicked.connect(self.pushButton_9_clicked)
        self.new_image_name=""
        self.dictin={}
        self.dir=""
        self.pushButton_10.clicked.connect(self.pushButton_10_clicked)
        self.pushButton_12.clicked.connect(self.pushButton_12_clicked)
        self.check=False
        self.loaded_image_3t=False
        self.loaded_image_4t=False    

    def segmentedImage4t(self,fileName):
        im=self.obj.predict(self.original_image,fileName)   
        im = cv2.resize(im,(480,320))
        image = QtGui.QImage(im.data, im.shape[1], im.shape[0], QtGui.QImage.Format_RGB888).rgbSwapped()
        self.label_8.setPixmap(QtGui.QPixmap.fromImage(image))
        self.label_8.setScaledContents(True)
        self.label_8.setWordWrap(False)
        self.label_8.setOpenExternalLinks(False)

    def segmentedImage3t(self,fileName):
        print(fileName)
        im=self.obj.predict(self.original_image,fileName)
        im=cv2.imread('./Image.png')
        im = cv2.resize(im,(480,320))
        image = QtGui.QImage(im.data, im.shape[1], im.shape[0], QtGui.QImage.Format_RGB888).rgbSwapped()
        self.label_6.setPixmap(QtGui.QPixmap.fromImage(image))
        self.label_6.setScaledContents(True)
        self.label_6.setWordWrap(False)
        self.label_6.setOpenExternalLinks(False)
        os.remove('./Image.png')

    def runParallel(self):
        self.obj.trainModel(self.epochs,self.batch_size,self.learning_rate)
        self.label_12.setVisible(False)
        self.check=True

if __name__ == '__main__':

    app = QApplication(sys.argv)
    myapp = MainW()
    myapp.show()
    sys.exit(app.exec_())