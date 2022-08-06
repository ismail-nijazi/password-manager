import hashlib
import sys
from datetime import datetime
from DataBase import *
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMainWindow
from styles.style import * 
from utils.encryption import hashPassword
from View.MainWindow import Window

# Login windows
class Login(QMainWindow):
    def __init__(self, language, window = None, parent=None):
        super().__init__(parent)
        self.language = language
        self.window = window
        self.setupUi()

    def setupUi(self):
        self.setObjectName("Login")
        self.resize(1006, 578)
        self.setStyleSheet("border:none;")
        self.setWindowTitle("KeepUrPass")
        self.setWindowIcon(QtGui.QIcon('Images/logo.png'))
        self.centralwidget = QtWidgets.QWidget(self)
        self.centralwidget.setObjectName("centralwidget")

        # Create a gridLayout for centralwidget
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setSpacing(0)
        self.gridLayout.setObjectName("gridLayout")

        # Login button will have this frame as parent widget
        self.frameLoginButton = QtWidgets.QFrame(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.frameLoginButton.sizePolicy().hasHeightForWidth())
        self.frameLoginButton.setSizePolicy(sizePolicy)
        self.frameLoginButton.setMinimumSize(QtCore.QSize(400, 150))
        self.frameLoginButton.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frameLoginButton.setFrameShadow(QtWidgets.QFrame.Raised)

        # Login button
        self.loginButton = QtWidgets.QPushButton(self.frameLoginButton)
        self.loginButton.setGeometry(QtCore.QRect(100, 100, 200, 50))
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.loginButton.sizePolicy().hasHeightForWidth())
        self.loginButton.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setFamily("Roboto Mono")
        font.setPointSize(14)
        self.loginButton.setFont(font)
        self.loginButton.setStyleSheet(btn_style)
        self.loginButton.setObjectName("loginButton")
        self.loginButton.clicked.connect(self.run)
        self.loginButton.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.loginButton.setText(self.language["button-login"])
        self.gridLayout.addWidget(self.frameLoginButton, 1, 1, 1, 1)

        # If any error happend in login process then a text representation of that error will apear in this widget
        # It will help user to know why and where error happend
        self.ErrorText = QtWidgets.QLabel(self.frameLoginButton)
        self.ErrorText.setGeometry(QtCore.QRect(0, 0, 400, 21))
        font.setPointSize(11)
        self.ErrorText.setFont(font)
        self.ErrorText.setStyleSheet("color:red;")
        self.ErrorText.setAlignment(QtCore.Qt.AlignCenter)
        self.ErrorText.setObjectName("ErrorText")

        spacerItem = QtWidgets.QSpacerItem(
            40, 20, QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 0, 2, 1, 1)

        # User have to enter the master password here
        self.txtPassword = QtWidgets.QLineEdit(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.txtPassword.sizePolicy().hasHeightForWidth())
        self.txtPassword.setSizePolicy(sizePolicy)
        self.txtPassword.setMinimumSize(QtCore.QSize(400, 30))
        self.txtPassword.returnPressed.connect(self.run)
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(10)
        self.txtPassword.setFont(font)
        self.txtPassword.setContextMenuPolicy(QtCore.Qt.NoContextMenu)
        self.txtPassword.setStyleSheet(input_Style)
        self.txtPassword.setMaxLength(1000)
        self.txtPassword.setEchoMode(QtWidgets.QLineEdit.Password)
        self.txtPassword.setCursorMoveStyle(QtCore.Qt.LogicalMoveStyle)
        self.txtPassword.setClearButtonEnabled(True)
        self.txtPassword.setObjectName("txtPassword")
        self.txtPassword.setPlaceholderText(self.language["master key"])
        self.gridLayout.addWidget(self.txtPassword, 0, 1, 1, 1)

        spacerItem1 = QtWidgets.QSpacerItem(
            40, 20, QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem1, 0, 0, 1, 1)
        self.gridLayout.setColumnStretch(0, 2)
        self.gridLayout.setColumnStretch(1, 1)
        self.gridLayout.setColumnStretch(2, 2)
        self.setCentralWidget(self.centralwidget)

        QtCore.QMetaObject.connectSlotsByName(self)

    # After user clicked the login button then this function will run
    # The function will check if the master key is correct and the key.txt file is not modified
    def run(self):
        password = self.txtPassword.text()
        key = password
        password = hashPassword(password)

        with open("key.txt", "r") as file:
            masterkey = file.read()

        databaseManipulator = MasterKey()
        hashMaker = hashlib.sha256()
        with open("key.txt", "rb") as hashFile:
            buffer = hashFile.read()
            hashMaker.update(buffer)

        if password.decode() == masterkey:
            if databaseManipulator.getMasterKey()[1] != hashMaker.hexdigest():
                self.ErrorText.setText(self.language["key file is manipulated!"])
                sys.exit()

            # When program opens window is equal None
            # But when window locks
            #    (There is a timer in Window class therefor it will be closed after a certain time but it will not be destroed) the global window
            #    still is equal Window therefor if statment will not be run and the window just shows again
            # By this method we can lock the program if user forget to exit1544210
            # We dont destroy the login window and we just hide it so after program was locked the login window will again be shown
            self.hide()
            self.txtPassword.setText("")
            self.ErrorText.setText("")
            if self.window == None:
                self.window = Window(key, self)
            self.window.showMaximized()
        else:
            self.ErrorText.setText(self.language["incorrect password"])

