import random
from DataBase import *
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import  QMessageBox, QMainWindow
from utils.encryption import hashPassword
from View.Login import Login
from styles.style import *

# This window will be shown first time after application is installed
# Here user will create a master key for inlogning to program
class RegWindow(QMainWindow):
    def __init__(self, language, change_main_window,parent=None):
        super().__init__(parent)
        self.language = language
        self.change_main_window = change_main_window
        self.setupUi()

    def setupUi(self):
        self.setObjectName("Register")
        self.setWindowTitle("KeepUrPass")
        self.resize(1100, 600)
        self.setStyleSheet("border:none;")
        self.setWindowIcon(QtGui.QIcon('Images/logo.png'))
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.sizePolicy().hasHeightForWidth())
        self.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setFamily("Roboto Mono")
        font.setPointSize(12)
        self.setFont(font)
        self.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.centralwidget = QtWidgets.QWidget(self)
        self.centralwidget.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.centralwidget.setAutoFillBackground(False)
        self.centralwidget.setStyleSheet("")
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setSizeConstraint(QtWidgets.QLayout.SetMinimumSize)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setSpacing(0)
        self.gridLayout.setObjectName("gridLayout")

        self.titleText = QtWidgets.QLabel(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.titleText.sizePolicy().hasHeightForWidth())
        self.titleText.setSizePolicy(sizePolicy)
        self.titleText.setMinimumSize(QtCore.QSize(0, 100))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(16)
        self.titleText.setFont(font)
        self.titleText.setStyleSheet("color:white;background-color:#002b4a;")
        self.titleText.setAlignment(QtCore.Qt.AlignCenter)
        self.titleText.setObjectName("titleText")
        self.gridLayout.addWidget(self.titleText, 0, 0, 1, 6)

        # Repeat password field
        self.lblrepeatedPsw = QtWidgets.QLabel(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.lblrepeatedPsw.sizePolicy().hasHeightForWidth())
        self.lblrepeatedPsw.setSizePolicy(sizePolicy)
        self.lblrepeatedPsw.setMinimumSize(QtCore.QSize(200, 30))
        font = QtGui.QFont()
        font.setFamily("Roboto Mono")
        font.setPointSize(12)
        self.lblrepeatedPsw.setFont(font)
        self.lblrepeatedPsw.setObjectName("lblrepeatedPsw")
        self.gridLayout.addWidget(self.lblrepeatedPsw, 2, 3, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(
            40, 20, QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 2, 0, 1, 1)
        spacerItem1 = QtWidgets.QSpacerItem(
            40, 20, QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem1, 2, 5, 1, 1)

        # password /master key field
        self.password = QtWidgets.QLineEdit(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.password.sizePolicy().hasHeightForWidth())
        self.password.setSizePolicy(sizePolicy)
        self.password.setMinimumSize(QtCore.QSize(300, 30))
        font = QtGui.QFont()
        font.setFamily("Roboto Mono")
        font.setPointSize(12)
        self.password.setFont(font)
        self.password.setContextMenuPolicy(QtCore.Qt.NoContextMenu)
        self.password.setStyleSheet(
            "border-bottom: 1px solid gray; border-radius: 3px;background-color:rgba(255,255,255,0%);color:#000;")
        self.password.setEchoMode(QtWidgets.QLineEdit.Password)
        self.password.setObjectName("password")
        self.gridLayout.addWidget(self.password, 2, 2, 1, 1)

        # Password/Masterkey label
        self.lblpassword = QtWidgets.QLabel(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.lblpassword.sizePolicy().hasHeightForWidth())
        self.lblpassword.setSizePolicy(sizePolicy)
        self.lblpassword.setMinimumSize(QtCore.QSize(100, 30))
        font = QtGui.QFont()
        font.setFamily("Roboto Mono")
        font.setPointSize(12)
        self.lblpassword.setFont(font)
        self.lblpassword.setObjectName("lblpassword")
        self.gridLayout.addWidget(self.lblpassword, 2, 1, 1, 1)

        # Repeat Password/Masterkey label
        self.repeatedPsw = QtWidgets.QLineEdit(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.repeatedPsw.sizePolicy().hasHeightForWidth())
        self.repeatedPsw.setSizePolicy(sizePolicy)
        self.repeatedPsw.setMinimumSize(QtCore.QSize(300, 30))
        font = QtGui.QFont()
        font.setFamily("Roboto Mono")
        font.setPointSize(12)
        self.repeatedPsw.setFont(font)
        self.repeatedPsw.setContextMenuPolicy(QtCore.Qt.NoContextMenu)
        self.repeatedPsw.setStyleSheet(
            "border-bottom: 1px solid gray; border-radius: 3px;background-color:rgba(255,255,255,0%);color:#000;")
        self.repeatedPsw.setEchoMode(QtWidgets.QLineEdit.Password)
        self.repeatedPsw.setObjectName("repeatedPsw")
        self.gridLayout.addWidget(self.repeatedPsw, 2, 4, 1, 1)

        # This frame is for register button
        self.frame = QtWidgets.QFrame(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.frame.sizePolicy().hasHeightForWidth())
        self.frame.setSizePolicy(sizePolicy)
        self.frame.setMinimumSize(QtCore.QSize(0, 250))
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")

        # Register button
        self.btnRegister = QtWidgets.QPushButton(self.frame)
        self.btnRegister.setGeometry(QtCore.QRect(250, 200, 241, 41))
        font = QtGui.QFont()
        font.setFamily("Roboto Mono")
        font.setPointSize(12)
        self.btnRegister.setFont(font)
        self.btnRegister.setStyleSheet(btn_style)
        self.btnRegister.setObjectName("btnRegister")
        self.btnRegister.clicked.connect(self.register)

        # If any error happend in registration process then a text representation of that error will apear in this widget
        self.ErrorText = QtWidgets.QLabel(self.frame)
        self.ErrorText.setGeometry(QtCore.QRect(70, 70, 600, 21))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.ErrorText.setFont(font)
        self.ErrorText.setStyleSheet("color:red;")
        self.ErrorText.setAlignment(QtCore.Qt.AlignCenter)
        self.ErrorText.setObjectName("ErrorText")

        self.gridLayout.addWidget(self.frame, 3, 2, 2, 3)
        self.gridLayout.setRowStretch(0, 2)
        self.gridLayout.setRowStretch(1, 1)
        self.gridLayout.setRowStretch(2, 1)
        self.gridLayout.setRowStretch(3, 1)
        self.gridLayout.setRowStretch(4, 1)
        self.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(self)
        self.statusbar.setObjectName("statusbar")
        self.setStatusBar(self.statusbar)

        self.retranslateUi(self)
        QtCore.QMetaObject.connectSlotsByName(self)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        self.btnRegister.setText( self.language["register"])
        self.lblpassword.setText( self.language["password"])
        self.lblrepeatedPsw.setText( self.language["repeat password"])
        self.titleText.setText( self.language["create master password"])

    # After register button was clicked this function will run
    def register(self):
        # psw: password
        psw = self.password.text()
        # rpsw: repeated password
        rpsw = self.repeatedPsw.text()

        # IF any one the fields is empty
        if not rpsw or not psw:
            self.ErrorText.setText( self.language["all fields should be filled!"])
        else:
            # If password and reapeted password were same
            if psw == rpsw:
                if len(psw) < 8:
                    self.ErrorText.setText(
                         self.language["your masterkey length should be at least 8 characters"])
                else:
                    try:
                        psw = hashPassword(psw)
                        with open("key.txt", "a+") as file:
                            file.write(psw.decode())
                         
                        databaseManipulator = MasterKey()
                        databaseManipulator.createMasterKey()
                        # If registration process finished successfully
						# Then the registration window will be destroyed and login window will be shown
                        self.close()
                        self.deleteLater()
                        self.change_main_window(Login(self.language))
                    except Exception as e:
                        QMessageBox.warning(self.centralwidget, self.language["error"],
                                            self.language["some unknown error occurred"], QMessageBox.Ok)
            else:
                self.ErrorText.setText(
                     self.language['passwords you entered are not matched'])
