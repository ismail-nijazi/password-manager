import json
import os
import random
import sys
from datetime import datetime
from DataBase import *
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMenu, QMessageBox
from utils.encryption import *
from styles.style import *


class Window(QtWidgets.QMainWindow):
    # Program have 3 part the leftside which is a sidebar
    # The middle which is main part
    # And the right side which is for:
    #     1.New button, when we click on new button 3 buttons will be display on this part those buttons are
    #       Add new password, Add new login and add new note
    #     2. When user want to see details about passwords and click on one of them the information will be displayed on right side
    # Program will not switch between frames whiout it will remove everythings from main or right frame.
    # Then it will create new child widgets with main or right frame as parent widget

    buttonSideBar = []

    # Determine what is displaying on the main frame
    currentFrame = None
    # Determine what is displaying on the right frame
    rightSideCurrentFrame = None
    
    # Styling of sidebar buttons
    btnStyle = """
		QPushButton{
				outline:none;
				padding-left:20px;
				text-align:left;
				border: 0px;
			}
		QPushButton::hover {
			background-color:#002b4a;
			color:#fff;
		}
	"""

	# Delete buttons style
    button_Delete_style = """QPushButton{
					outline:none;
					background-color: #002b4a;
					color: white;
					border-radius:3px;
					border:none;
					padding:10px 10px;
								}
					QPushButton::hover {background-color: #004678}"""

    otherButtons_style = """
							QPushButton{
								text-align:center;
								outline:none;
								background-color:#002b4a;
								color: White;
								border: 0;
								border-radius:4px;
								}
							QPushButton::hover{
								background-color:#004678;
							}
						"""

	# 'Show password' button style
    showButton_Style = "background-color:#fff;border-top:1px solid #999;;border-right:1px solid #999;border-bottom:1px solid #999 "
	# Fields style
    input_Style_main = 'border:1px solid #999; border-radius: 1px;background-color:#fff;color:black;'
	# password fields style
    input_Password_Style = 'border:1px solid #999; border-radius: 1px;background-color:#fff;color:black;border-right:none;'
    # Check if user already was in the generate pass and if he/she was
    # It will save the last generated password on lastPassword and last password lenght on lastLength.
    checkForGenPass = False
    lastPassword = ""
    lastLength = None

    digits = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
    lowercaseChar = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h',
                     'i', 'j', 'k', 'm', 'n', 'o', 'p', 'q',
                     'r', 's', 't', 'u', 'v', 'w', 'x', 'y',
                     'z']

    uperCaserChaer = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H',
                      'I', 'J', 'K', 'M', 'N', 'O', 'p', 'Q',
                      'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y',
                      'Z']

    symbols = ['@', '#', '$', '%', '=', ':', '?', '.', '/', '|', '~', '>',
               '*', '(', ')', '<', '&']

    combinded = digits + lowercaseChar + uperCaserChaer + symbols

    # Links list which can be chosen when user want to create a 'login'
    links = {
        "custom url": "",
        "google": "https://main.google.com/",
        "facebook": "https://facebok.com",
        "instagram": "https://instagram.com",
        "amazon": "https://www.amazon.com/ap/signin?_encoding=UTF8&openid.assoc_handle=usflex&openid.claimed_id=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.identity=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.mode=checkid_setup&openid.ns=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0&openid.ns.pape=http%3A%2F%2Fspecs.openid.net%2Fextensions%2Fpape%2F1.0&openid.pape.max_auth_age=0&openid.return_to=https%3A%2F%2Fwww.amazon.com%2Fgp%2Fyourstore%2Fhome%3Fie%3DUTF8%26ref_%3Dnav_ya_signin",
        "live": "https://login.live.com/login.srf",
        "paypal": "https://www.paypal.com/login",
    }

    def __init__(self, masterKey, loginWindow = None):
        self.loginWindow = loginWindow
        # Window class inherit from QtWidgets.QMainWindow
        # Run QtWidgets.QMainWindow init method
        super().__init__()
        # Get the apps settings from 'settings.json' and save them in a dictionary which is self.settings
        self.settings = {"theme-name": "",
                         "language": "", "theme": {}, "time": ""}
        with open("Lang/lang.json") as file:
            loaded_file = json.load(file)
            with open("settings.json") as settingFile:
                settings = json.load(settingFile)
                self.settings["theme-name"] = settings["settings"]["theme"]
                self.settings["language"] = settings["settings"]["language"]
                self.settings["theme"] = settings["Themes"][self.settings["theme-name"]]
                self.settings["time"] = settings["settings"]["time"]
                self.duration = [settings["settings"]
                                 ["time"], settings["settings"]["time"]]
                settingFile.close()
            # self.language will save wich language should app will be displayed
            self.language = loaded_file["languages"][self.settings["language"]]
        # Depends on which theme app will be shown can sidebar buttons styling change
        self.setDefualtBtnStyles()
        self.btnStyle += f"background-color:{self.settings['theme']['bgColorFrameLeftSide']};color:{self.settings['theme']['sidebar-textColor']};"

        self.masterKey = masterKey
        # UserInfo is a class in Database.py it will interact with the database
        self.db = UserInfo(masterKey)
        self.countLabelRole = 0
        self.countFieldRole = 0
        self.setupUi()

        # self.clearLayout() will remove everything frome main frame and create new child widgets on it
        # in this case it will create a new frame with main frame as parent
        # therafter will be created a list of buttons with the new frame as parent and a summery of the
        # passwords info will be display on the buttons
        self.clearLayout(self.frameShowPasswords, "all")
        self.currentFrame = "all"
        self.activeButton = self.btnAll_Item

    def setupUi(self):
        self.setObjectName("MainWindow")
        self.resize(1600, 907)
        # Set focus on the app
        self.setFocus()
        # Change the defualt styles
        self.setStyleSheet("""
                    QScrollBar:vertical {
                        width: 6px;
                        background-color:#383838;
                      }

                      QScrollBar::handle:vertical {
                        min-height: 10px;
                        background-color:#383838;
                        border-radius:5px;
                      }

                      QScrollBar:horizontal {
                        height: 0px;
                        background-color:#383838;
                      }

                      QScrollBar::handle:horizontal {
                        background-color:#383838;
                      }
                    QMenu{padding:5px;background-color:#fff;}
                    QMenu::item::selected{
                        background-color:#838485;color:white;
                    }
                    border:none;
                    """)
        self.setWindowTitle("KeepUrPass")
        # Set the logo which will be display on top left of the window
        self.setWindowIcon(QtGui.QIcon('Images/logo.png'))

        # Create a size policy for the main window
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.sizePolicy().hasHeightForWidth())
        self.setSizePolicy(sizePolicy)
        self.centralwidget = QtWidgets.QWidget(self)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setSpacing(0)
        self.gridLayout.setObjectName("gridLayout")

        self.frameMain = QtWidgets.QFrame(self.centralwidget)
        self.frameMain.setStyleSheet(
            f"border:0;background-color:{self.settings['theme']['frameMainBgColor']}")
        self.frameMain.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.frameMain.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frameMain.setObjectName("frameMain")

        self.gridLayout_2 = QtWidgets.QGridLayout(self.frameMain)
        self.gridLayout_2.setContentsMargins(-1, 10, -1, -1)
        self.gridLayout_2.setObjectName("gridLayout_2")

        self.frameShowPasswords = QtWidgets.QFrame(self.frameMain)
        self.frameShowPasswords.setStyleSheet("border:0;")
        self.frameShowPasswords.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.frameShowPasswords.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frameShowPasswords.setObjectName("frameShowPasswords")
        self.gridLayout_2.addWidget(self.frameShowPasswords, 0, 0, 2, 1)
        self.verticalLayout_6 = QtWidgets.QVBoxLayout(self.frameShowPasswords)
        self.verticalLayout_6.setContentsMargins(5, 0, 0, 0)
        self.verticalLayout_6.setObjectName("verticalLayout_6")

        self.frame_4 = QtWidgets.QFrame(self.frameMain)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.frame_4.sizePolicy().hasHeightForWidth())
        self.frame_4.setSizePolicy(sizePolicy)
        self.frame_4.setStyleSheet(
            f"background-color:#002b4a;border-right:5px solid {self.settings['theme']['frameMainBgColor']};"
            f"border-top:5px solid {self.settings['theme']['frameMainBgColor']};"
            f"border-bottom:5px solid {self.settings['theme']['frameMainBgColor']}")
        self.frame_4.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_4.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_4.setObjectName("frame_4")
        self.gridLayout_3 = QtWidgets.QGridLayout(self.frame_4)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.btnNew = QtWidgets.QPushButton(self.frame_4)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.btnNew.sizePolicy().hasHeightForWidth())
        self.btnNew.setSizePolicy(sizePolicy)
        self.btnNew.setMinimumSize(QtCore.QSize(30, 30))
        self.btnNew.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.btnNew.setFont(font)
        self.btnNew.setStyleSheet(
            "QPushButton{background-color:none;color:black;border-radius:14px;border:0;margin-right:10px;}")
        self.btnNew.setText("")
        self.btnNew.clicked.connect(
            lambda: self.showButtonsInAddFrame(self.frameSideRight, "new"))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("Images/addIcon.png"),
                       QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btnNew.setIcon(icon)
        self.btnNew.setIconSize(QtCore.QSize(30, 30))
        self.btnNew.setObjectName("btnNew")
        self.gridLayout_3.addWidget(self.btnNew, 0, 1, 1, 1)
        self.showMessageHere = QtWidgets.QLabel(self.frame_4)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.showMessageHere.sizePolicy().hasHeightForWidth())
        self.showMessageHere.setSizePolicy(sizePolicy)
        self.showMessageHere.setStyleSheet(
            "color:#00fa32;background-color:#002b4a;border:none;")
        font.setFamily("Roboto")
        font.setPointSize(12)
        self.showMessageHere.setFont(font)
        self.gridLayout_3.addWidget(self.showMessageHere, 0, 0, 1, 1)
        self.gridLayout_2.addWidget(self.frame_4, 0, 1, 1, 1)
        self.frameSideRight = QtWidgets.QFrame(self.frameMain)
        self.frameSideRight.setStyleSheet(
            "border:0;border-left:1px solid #383838;background-color:"
            f"{self.settings['theme']['bgColorFrameRightSide']};color:{self.settings['theme']['AddPagesTextColor']};")
        self.frameSideRight.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frameSideRight.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frameSideRight.setObjectName("frameSideRight")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.frameSideRight)
        self.verticalLayout.setContentsMargins(100, 100, -1, -1)
        self.verticalLayout.setSpacing(15)
        self.verticalLayout.setObjectName("verticalLayout")

        self.gridLayout_2.addWidget(self.frameSideRight, 1, 1, 1, 1)
        self.gridLayout_2.setColumnStretch(0, 5)
        self.gridLayout_2.setColumnStretch(1, 4)
        self.gridLayout_2.setRowStretch(0, 1)
        self.gridLayout_2.setRowStretch(1, 15)
        self.gridLayout_2.setHorizontalSpacing(0)
        self.gridLayout_2.setVerticalSpacing(0)
        self.gridLayout.addWidget(self.frameMain, 0, 1, 1, 1)
        self.frameSideLeft = QtWidgets.QFrame(self.centralwidget)
        self.frameSideLeft.setStyleSheet(
            f"border:0;background-color:{self.settings['theme']['bgColorFrameLeftSide']};")
        self.frameSideLeft.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frameSideLeft.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frameSideLeft.setObjectName("frameSideLeft")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.frameSideLeft)
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.frameMenueLeft = QtWidgets.QFrame(self.frameSideLeft)
        self.frameMenueLeft.setStyleSheet("border:0;")
        self.frameMenueLeft.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frameMenueLeft.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frameMenueLeft.setObjectName("frameMenueLeft")
        self.frameSideLeft.setFixedWidth(250)
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.frameMenueLeft)
        self.verticalLayout_4.setContentsMargins(0, 80, 0, 40)
        self.verticalLayout_4.setSpacing(10)
        self.verticalLayout_4.setObjectName("verticalLayout_4")

        self.btnAll_Item = QtWidgets.QPushButton(self.frameMenueLeft)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.btnAll_Item.sizePolicy().hasHeightForWidth())
        self.btnAll_Item.setSizePolicy(sizePolicy)
        self.btnAll_Item.setFont(font)
        self.btnAll_Item.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.btnAll_Item.setObjectName("btnAll_Item")
        self.btnAll_Item.setIcon(QtGui.QIcon('Images/list'))
        self.btnAll_Item.setIconSize(QtCore.QSize(20, 20))
        self.btnAll_Item.clicked.connect(
            lambda: self.clearLayout(self.frameShowPasswords, "all"))
        self.verticalLayout_4.addWidget(self.btnAll_Item)

        spacerItem2 = QtWidgets.QSpacerItem(
            20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Preferred)
        self.verticalLayout_4.addItem(spacerItem2)
        self.btnPassword = QtWidgets.QPushButton(self.frameMenueLeft)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.btnPassword.sizePolicy().hasHeightForWidth())
        self.btnPassword.setSizePolicy(sizePolicy)
        self.btnPassword.setFont(font)
        self.btnPassword.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.btnPassword.setObjectName("btnPassword")
        self.btnPassword.setIcon(QtGui.QIcon("images/pin-code.png"))
        self.btnPassword.setIconSize(QtCore.QSize(20, 20))
        self.btnPassword.clicked.connect(
            lambda: self.clearLayout(self.frameShowPasswords, "password"))
        self.verticalLayout_4.addWidget(self.btnPassword)
        self.btnLogin = QtWidgets.QPushButton(self.frameMenueLeft)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.btnLogin.sizePolicy().hasHeightForWidth())
        self.btnLogin.setSizePolicy(sizePolicy)
        self.btnLogin.setFont(font)
        self.btnLogin.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.btnLogin.setObjectName("btnLogin")
        self.btnLogin.setIcon(QtGui.QIcon("images/user.png"))
        self.btnLogin.setIconSize(QtCore.QSize(20, 20))
        self.btnLogin.clicked.connect(
            lambda: self.clearLayout(self.frameShowPasswords, "login"))
        self.verticalLayout_4.addWidget(self.btnLogin)
        self.btnGeneratePassword = QtWidgets.QPushButton(self.frameMenueLeft)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.btnGeneratePassword.sizePolicy().hasHeightForWidth())
        self.btnGeneratePassword.setSizePolicy(sizePolicy)
        self.btnGeneratePassword.setFont(font)
        self.btnGeneratePassword.setCursor(
            QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.btnGeneratePassword.setObjectName("btnGeneratePassword")
        self.btnGeneratePassword.setIcon(QtGui.QIcon("images/pass.png"))
        self.btnGeneratePassword.setIconSize(QtCore.QSize(20, 20))
        self.btnGeneratePassword.clicked.connect(
            lambda: self.showFrameGenPassword(self.frameShowPasswords, "genPass"))
        self.btnNote = QtWidgets.QPushButton(self.frameMenueLeft)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.btnNote.sizePolicy().hasHeightForWidth())
        self.btnNote.setSizePolicy(sizePolicy)
        self.btnNote.setFont(font)
        self.btnNote.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.btnNote.setObjectName("btnNote")
        self.btnNote.setIcon(QtGui.QIcon("images/file.png"))
        self.btnNote.setIconSize(QtCore.QSize(20, 20))
        self.btnNote.clicked.connect(
            lambda: self.clearLayout(self.frameShowPasswords, "note"))
        self.verticalLayout_4.addWidget(self.btnNote)
        self.verticalLayout_4.addWidget(self.btnGeneratePassword)
        spacerItem3 = QtWidgets.QSpacerItem(
            20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_4.addItem(spacerItem3)
        self.verticalLayout_4.setStretch(0, 2)
        self.verticalLayout_4.setStretch(1, 5)
        self.verticalLayout_4.setStretch(2, 2)
        self.verticalLayout_4.setStretch(3, 2)
        self.verticalLayout_4.setStretch(4, 2)
        self.verticalLayout_4.setStretch(5, 2)
        self.verticalLayout_4.setStretch(6, 10)
        self.verticalLayout_3.addWidget(self.frameMenueLeft)
        self.frameMenueDown = QtWidgets.QFrame(self.frameSideLeft)
        self.frameMenueDown.setStyleSheet("border:0;")
        self.frameMenueDown.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frameMenueDown.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frameMenueDown.setObjectName("frameMenueDown")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.frameMenueDown)
        self.verticalLayout_2.setContentsMargins(0, -1, 0, -1)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        spacerItem4 = QtWidgets.QSpacerItem(
            20, 150, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Preferred)
        self.verticalLayout_2.addItem(spacerItem4)
        self.btnSettings = QtWidgets.QPushButton(self.frameMenueDown)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.btnSettings.sizePolicy().hasHeightForWidth())
        self.btnSettings.setSizePolicy(sizePolicy)
        self.btnSettings.setFont(font)
        self.btnSettings.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.btnSettings.clicked.connect(
            lambda: self.clearLayout(self.frameShowPasswords, "settings"))
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap("Images/settings.png"),
                        QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btnSettings.setIcon(icon1)
        self.btnSettings.setObjectName("btnSettings")
        self.verticalLayout_2.addWidget(self.btnSettings)

        self.btnAbout = QtWidgets.QPushButton(self.frameMenueDown)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.btnAbout.sizePolicy().hasHeightForWidth())
        self.btnAbout.setSizePolicy(sizePolicy)
        self.btnAbout.setFont(font)
        self.btnAbout.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.btnAbout.clicked.connect(
            lambda: self.clearLayout(self.frameShowPasswords, "about"))
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap("Images/about.png"),
                        QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btnAbout.setIcon(icon2)
        self.btnAbout.setObjectName("btnAbout")

        self.verticalLayout_2.addWidget(self.btnAbout)
        self.verticalLayout_2.setStretch(0, 3)
        self.verticalLayout_2.setStretch(1, 1)
        self.verticalLayout_2.setStretch(2, 1)
        self.verticalLayout_3.addWidget(self.frameMenueDown)
        self.verticalLayout_3.setStretch(0, 3)
        self.verticalLayout_3.setStretch(1, 1)
        self.gridLayout.addWidget(self.frameSideLeft, 0, 0, 1, 1)
        self.gridLayout.setColumnStretch(0, 1)
        self.setCentralWidget(self.centralwidget)
        self.buttonSideBar.append(self.btnAll_Item)
        self.buttonSideBar.append(self.btnPassword)
        self.buttonSideBar.append(self.btnLogin)
        self.buttonSideBar.append(self.btnNote)
        self.buttonSideBar.append(self.btnGeneratePassword)
        self.buttonSideBar.append(self.btnAbout)
        self.buttonSideBar.append(self.btnSettings)
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.checkTime)
        self.timer.start(1000)

        self.setButtonsText()
        QtCore.QMetaObject.connectSlotsByName(self)

    def checkTime(self):
        if (self.isActiveWindow()):
            self.duration[0] = self.duration[1]
        else:
            if self.duration[0] != 0:
                self.duration[0] -= 1
            else:
                self.close()
                self.loginWindow.showMaximized()
        width = self.size().width()
        if width < 1435:
            for btn in self.buttonSideBar:
                btn.setText("")
                btn.setIconSize(QtCore.QSize(30, 30))
            self.btnStyleActive = """
                        QPushButton{
                                outline:none;
                                text-align:center;
                                background-color:#002b4a;
                                color: White;
                                border: 0px;
                           }
                    """
            self.btnStyle = """
                            QPushButton{
                                    outline:none;
                                    text-align:center;
                                    border: 0px;
                               }
                            QPushButton::hover {
                                background-color:#002b4a;
                                color:#fff;
                            }
                        """
            self.btnStyle += f"background-color:{self.settings['theme']['bgColorFrameLeftSide']};color:{self.settings['theme']['sidebar-textColor']};"
            self.changeButtonStyle()
            self.frameSideLeft.setFixedWidth(80)

        else:
            self.setDefualtBtnStyles()
            for btn in self.buttonSideBar:
                btn.setIconSize(QtCore.QSize(20, 20))
            self.changeButtonStyle()
            self.setButtonsText()
            self.frameSideLeft.setFixedWidth(250)

    # Function to show all items
    # This function is the first function that will be run after mainwindow was created
    def start(self, message=None):
        font = QtGui.QFont()
        font.setFamily("Arial")
        self.showMessageHere.setText(message)
        passwords = self.db.getAllData()
        # Create a QButtonGroup to set all buttons on it
        self.btn_grp = QtWidgets.QButtonGroup()
        self.btn_grp.setExclusive(True)
        self.formLayout = QtWidgets.QFormLayout(self.scrollAreaWidgetContents)
        self.formLayout.setRowWrapPolicy(QtWidgets.QFormLayout.WrapLongRows)
        self.formLayout.setContentsMargins(100, 30, -1, -1)
        self.formLayout.setHorizontalSpacing(50)
        self.formLayout.setVerticalSpacing(30)
        self.formLayout.setObjectName("formLayout")
        # If there is no data in database we will create a empty page to user
        # Then he/she knows that there is nothing saved in database
        if not passwords:
            labelEmpty = QtWidgets.QLabel(self.scrollAreaWidgetContents)
            pixmap = QtGui.QPixmap("images/folderEmptyState.png")
            labelEmpty.setPixmap(pixmap)
            labelEmpty.setAlignment(QtCore.Qt.AlignCenter)
            labelEmpty.setMinimumSize(QtCore.QSize(900, 580))
            labelText = QtWidgets.QLabel(self.scrollAreaWidgetContents)
            labelText.setText(
                self.language['press new button + to create new item'])
            font.setPointSize(13)
            font.setBold(True)
            labelText.setFont(font)
            labelText.setAlignment(QtCore.Qt.AlignCenter)
            labelText.setStyleSheet(
                "background-color:rgba(0,0,0,0);color:#000;")
            labelText.setGeometry(QtCore.QRect(0, 400, 900, 50))

        # Loop over all data in database and create a button for every row in database
        for password in passwords:
            self.createButtons(password)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.verticalLayout_6.addWidget(self.scrollArea)
        self.btn_grp.buttonClicked.connect(self.updateItem)
        self.countFieldRole = 0
        self.countLabelRole = 0

    def showPasLogNote(self, item, message=None):
        self.showMessageHere.setText(message)
        passwords = self.db.getAllData()
        font = QtGui.QFont()
        font.setFamily("Arial")
        self.btn_grp = QtWidgets.QButtonGroup()
        self.btn_grp.setExclusive(True)
        self.formLayout = QtWidgets.QFormLayout(self.scrollAreaWidgetContents)
        self.formLayout.setRowWrapPolicy(QtWidgets.QFormLayout.WrapLongRows)
        self.formLayout.setContentsMargins(100, 30, -1, -1)
        self.formLayout.setHorizontalSpacing(50)
        self.formLayout.setVerticalSpacing(30)
        self.formLayout.setObjectName("formLayout")

        isEmpty = True
        for password in passwords:
            if password[1] == item:
                isEmpty = False
        if isEmpty:
            labelEmpty = QtWidgets.QLabel(self.scrollAreaWidgetContents)
            imagePath = ""
            infoText = ""
            if item == "note":
                imagePath = "images/folderEmptyState.png"
                infoText = self.language["press new button + to create new note"]
            elif item == "login":
                imagePath = "images/folderEmptyState.png"
                infoText = self.language["press new button + to create new login"]
            elif item == "password":
                imagePath = "images/folderEmptyState.png"
                infoText = self.language["press new button + to create new password"]
            pixmap = QtGui.QPixmap(imagePath)
            labelEmpty.setPixmap(pixmap)
            labelEmpty.setAlignment(QtCore.Qt.AlignCenter)
            labelEmpty.setMinimumSize(QtCore.QSize(900, 580))
            labelText = QtWidgets.QLabel(self.scrollAreaWidgetContents)
            labelText.setText(infoText)
            font.setPointSize(13)
            font.setBold(True)
            labelText.setFont(font)
            labelText.setAlignment(QtCore.Qt.AlignCenter)
            labelText.setStyleSheet(
                "background-color:rgba(0,0,0,0);color:#000;")
            labelText.setGeometry(QtCore.QRect(0, 400, 900, 50))
        for password in passwords:
            if password[1] == item:
                self.createButtons(password)

        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.verticalLayout_6.addWidget(self.scrollArea)

        self.btn_grp.buttonClicked.connect(self.updateItem)
        self.countFieldRole = 0
        self.countLabelRole = 0

    def createButtons(self, password):
        font = QtGui.QFont()
        font.setFamily("Arial")
        button = QtWidgets.QPushButton(self.scrollAreaWidgetContents)
        font.setPointSize(12)
        passwordType = QtWidgets.QLabel(button)
        if password[1] == "login":
            if password[4] in self.links.keys():
                pixmap = QtGui.QPixmap(f"Images/Logos/{password[4]}.png")
            else:
                pixmap = QtGui.QPixmap("Images/Logos/login.png")
        else:
            pixmap = QtGui.QPixmap(f"Images/Logos/{password[1]}.png")
        passwordType.setPixmap(pixmap)
        passwordType.setAlignment(QtCore.Qt.AlignCenter)
        passwordType.setFont(font)
        passwordType.setGeometry(QtCore.QRect(0, 5, 240, 50))
        passwordType.setStyleSheet(
            "QLabel{background-color:rgba(0,0,0,0%);color:#0d4b78;border-radius:3px;border:0px;} ")
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(button.sizePolicy().hasHeightForWidth())
        button.setSizePolicy(sizePolicy)
        button.setMinimumSize(QtCore.QSize(240, 110))
        button.setMaximumSize(QtCore.QSize(240, 110))
        button.setFont(font)
        button.setText(f"\n\n\n\t{password[2]}")
        button.setStyleSheet(
            "QPushButton{padding: 10px 20px;background-color:white;color:black;border-radius:3px;border:0px;outline:none;}QPushButton::hover{border-bottom:2px solid #004678;}")
        button.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        button.setObjectName(f"{password[1]}-{password[0]}")
        self.btn_grp.addButton(button)
        if self.countLabelRole == self.countFieldRole:
            self.formLayout.setWidget(
                self.countLabelRole, QtWidgets.QFormLayout.LabelRole, button)
            self.countLabelRole += 1
        elif self.countLabelRole > self.countFieldRole:
            self.formLayout.setWidget(
                self.countFieldRole, QtWidgets.QFormLayout.FieldRole, button)
            self.countFieldRole += 1

    def showSettingsPage(self):
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.scrollAreaWidgetContents.sizePolicy().hasHeightForWidth())
        self.scrollAreaWidgetContents.setSizePolicy(sizePolicy)
        self.scrollAreaWidgetContents.setInputMethodHints(QtCore.Qt.ImhNone)
        self.verticalLayoutSetting = QtWidgets.QVBoxLayout(
            self.scrollAreaWidgetContents)
        self.verticalLayoutSetting.setSizeConstraint(
            QtWidgets.QLayout.SetDefaultConstraint)
        self.verticalLayoutSetting.setContentsMargins(0, 0, 0, 0)
        self.verticalLayoutSetting.setSpacing(0)
        self.SettingsTabs = QtWidgets.QTabWidget(self.scrollAreaWidgetContents)
        font = QtGui.QFont()
        font.setFamily("Roboto Mono")
        font.setPointSize(10)
        self.SettingsTabs.setFont(font)
        self.SettingsTabs.setStyleSheet(
            "QTabBar::tab{padding:10px;background-color:#002b4a;color:white;}"
            "QTabBar::tab::selected{background-color:#035794;}QTabWidget::pane { border: 0; }")
        self.SettingsTabs.setDocumentMode(False)
        self.SettingsTabs.setTabsClosable(False)
        self.SettingsTabs.setObjectName("SettingsTabs")
        self.General_tab = QtWidgets.QWidget()
        self.General_tab.setObjectName("General_tab")
        label = QtWidgets.QLabel(self.General_tab)
        label.setGeometry(QtCore.QRect(60, 50, 81, 21))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(13)
        font.setBold(True)
        label.setFont(font)
        label.setObjectName("label")
        label.setStyleSheet("color:black")
        self.classicTheme = QtWidgets.QRadioButton(self.General_tab)
        self.classicTheme.clicked.connect(
            lambda: self.applySettings(self.classicTheme))
        self.classicTheme.setGeometry(QtCore.QRect(60, 110, 82, 17))
        font.setPointSize(10)
        font.setBold(False)
        self.classicTheme.setFont(font)
        self.classicTheme.setObjectName("classicTheme")
        self.darkTheme = QtWidgets.QRadioButton(self.General_tab)
        self.darkTheme.clicked.connect(
            lambda: self.applySettings(self.darkTheme))
        self.darkTheme.setGeometry(QtCore.QRect(190, 110, 82, 17))
        self.darkTheme.setFont(font)
        self.darkTheme.setObjectName("darkTheme")
        label_2 = QtWidgets.QLabel(self.General_tab)
        label_2.setGeometry(QtCore.QRect(60, 200, 81, 21))
        font.setPointSize(13)
        font.setBold(True)
        label_2.setFont(font)
        label_2.setObjectName("label_2")
        label_2.setStyleSheet("color:black")
        self.chosenLanguage = QtWidgets.QComboBox(self.General_tab)
        self.chosenLanguage.setGeometry(QtCore.QRect(60, 250, 141, 31))
        font.setPointSize(11)
        font.setBold(False)
        self.chosenLanguage.setFont(font)
        self.chosenLanguage.setStyleSheet(
            "border:1px solid rgba(97, 97, 97,0.5);background-color:white;")
        self.chosenLanguage.setObjectName("chosenLanguage")
        self.chosenLanguage.addItem("")
        self.chosenLanguage.addItem("")
        self.chosenLanguage.addItem("")

        self.message = QtWidgets.QLabel(self.General_tab)
        self.message.setGeometry(QtCore.QRect(60, 350, 500, 50))
        font.setPointSize(12)
        self.message.setFont(font)
        self.message.setStyleSheet("color:#d43f3f;border:none;")
        self.message.setText("")
        self.SettingsTabs.addTab(self.General_tab, "")

        self.Security_tab = QtWidgets.QWidget()
        self.Security_tab.setObjectName("Security_tab")
        self.btnMasterkey = QtWidgets.QPushButton(self.Security_tab)
        self.btnMasterkey.setGeometry(QtCore.QRect(80, 120, 171, 31))
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.btnMasterkey.sizePolicy().hasHeightForWidth())
        self.btnMasterkey.setSizePolicy(sizePolicy)
        self.btnMasterkey.clicked.connect(
            lambda: self.pageChangeMasterKey("UpdateMasterKey"))
        font.setPointSize(12)
        self.btnMasterkey.setFont(font)
        self.btnMasterkey.setStyleSheet(
            "border:1xp solid black;color:white;border-radius:3px;;background-color:#5e5e5e;")
        self.btnMasterkey.setObjectName("btnMasterkey")
        label_5 = QtWidgets.QLabel(self.Security_tab)
        label_5.setGeometry(QtCore.QRect(80, 50, 241, 31))
        font.setPointSize(13)
        font.setBold(True)
        label_5.setFont(font)
        label_5.setObjectName("label_5")
        label_5.setStyleSheet("color:black")

        lblLockTime = QtWidgets.QLabel(self.Security_tab)
        lblLockTime.setGeometry(QtCore.QRect(80, 190, 200, 31))
        lblLockTime.setFont(font)

        self.lblAfter = QtWidgets.QLabel(self.Security_tab)
        self.lblAfter.setGeometry(QtCore.QRect(80, 240, 100, 31))
        font.setPointSize(11)
        font.setBold(False)
        self.lblAfter.setFont(font)

        self.choseTime = QtWidgets.QComboBox(self.Security_tab)
        self.choseTime.addItems(
            [self.language["allways"], "1", "2", "3", "4", "5", "10", "20", "30", "60"])
        self.choseTime.currentIndexChanged.connect(self.changeTime)
        self.choseTime.setGeometry(80, 280, 100, 31)
        self.choseTime.setStyleSheet(
            "border:1px solid rgba(97, 97, 97,0.5);background-color:#fff;")
        font.setPointSize(11)
        font.setBold(False)
        self.choseTime.setFont(font)

        self.SettingsTabs.addTab(self.Security_tab, "")
        self.Advanced_tab = QtWidgets.QWidget()
        self.Advanced_tab.setObjectName("Advanced_tab")
        font.setPointSize(13)
        font.setBold(True)
        label_4 = QtWidgets.QLabel(self.Advanced_tab)
        label_4.setGeometry(QtCore.QRect(80, 60, 150, 21))
        label_4.setFont(font)
        label_4.setObjectName("label_4")
        label_4.setStyleSheet("color:black")
        self.btnDeleteAllData = QtWidgets.QPushButton(self.Advanced_tab)
        self.btnDeleteAllData.setGeometry(QtCore.QRect(80, 120, 141, 31))
        font.setPointSize(12)
        font.setBold(False)
        self.btnDeleteAllData.setFont(font)
        self.btnDeleteAllData.setStyleSheet(
            "color:white;border-radius:3px;border:1xp solid black;background-color:#5e5e5e;")
        self.btnDeleteAllData.setObjectName("btnDeleteAllData")
        self.btnDeleteAllData.clicked.connect(
            lambda: self.pageDeleteAll("DeleteAll"))
        self.SettingsTabs.addTab(self.Advanced_tab, "")

        label.setText(self.language["theme"])
        self.classicTheme.setText(self.language["classic"])
        self.darkTheme.setText(self.language["dark"])
        label_2.setText(self.language["language"])
        self.chosenLanguage.setItemText(0, self.language["english"])
        self.chosenLanguage.setItemText(1, self.language["swedish"])
        self.chosenLanguage.setItemText(2, self.language["persian"])
        self.chosenLanguage.setCurrentText(self.settings["language"])
        self.chosenLanguage.currentIndexChanged.connect(
            lambda x: self.applySettings(self.darkTheme, language=self.chosenLanguage.currentText()))
        self.SettingsTabs.setTabText(self.SettingsTabs.indexOf(
            self.General_tab), self.language["general"])
        self.btnMasterkey.setText(self.language["master key"])
        label_5.setText(self.language["change your master key"])
        lblLockTime.setText(self.language["lock the program "])
        self.SettingsTabs.setTabText(self.SettingsTabs.indexOf(
            self.Security_tab), self.language["security"])
        label_4.setText(self.language["delete all data"])
        self.btnDeleteAllData.setText(self.language["delete"])
        self.SettingsTabs.setTabText(self.SettingsTabs.indexOf(
            self.Advanced_tab), self.language["advanced"])
        if (self.settings["time"] == 5):
            self.lblAfter.setText(self.language["allways"])
            self.choseTime.setCurrentText(self.language["allways"])
        else:
            self.lblAfter.setText(
                self.language["after"] + " " + str(int(self.settings["time"] / 60)) + " " + self.language["minute"])
            self.choseTime.setCurrentText(str(int(self.settings["time"] / 60)))

        if self.settings["theme-name"] == "Dark":
            self.darkTheme.setChecked(True)
        else:
            self.classicTheme.setChecked(True)

        self.verticalLayoutSetting.addWidget(self.SettingsTabs)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.verticalLayout_6.addWidget(self.scrollArea)

    def changeTime(self, t):
        index = self.choseTime.currentIndex()
        if index == 0:
            time = 5
            self.duration = [5, 5]
            self.lblAfter.setText(self.language["allways"])
        else:
            time = int(self.choseTime.currentText()) * 60
            self.duration = [time, time]
            self.lblAfter.setText(
                self.language["after"] + " " + self.choseTime.currentText() + " " + self.language["minute"])

        self.settings["time"] = time
        with open("settings.json") as file:
            data = json.load(file)
            file.close()

        data["settings"]["time"] = time
        with open("settings.json", "w") as newSettings:
            json.dump(data, newSettings, indent=4)

    def applySettings(self, radioButton, language=None):
        if language is not None:
            self.settings["language"] = language
            self.message.setText(
                self.language["these settings require restarting KeepUrPass to take effect"])

        if radioButton.text() == self.language["dark"]:
            if radioButton.isChecked():
                self.settings["theme-name"] = "Dark"
            else:
                self.settings["theme-name"] = "Classic"
        else:
            if radioButton.isChecked():
                self.settings["theme-name"] = "Classic"
            else:
                self.settings["theme-name"] = "Dark"

        with open("settings.json") as file:
            data = json.load(file)
            file.close()

        data["settings"]["theme"] = self.settings["theme-name"]
        data["settings"]["language"] = self.settings["language"]

        with open("settings.json", "w") as newSetting:
            json.dump(data, newSetting, indent=4)

        self.message.setText(
            self.language["these settings require restarting KeepUrPass to take effect"])

    def pageChangeMasterKey(self, newLayout):
        input_Style = 'border:none; background-color:#f0f0f0;color:black;border-top:1px solid gray;border-left:1px ' \
                      'solid gray;border-bottom:1px solid gray;padding:5px;'
        showButton_Style = "background-color:#f0f0f0;border-top:1px solid gray;;border-right:1px solid " \
                           "gray;border-bottom:1px solid gray "

        if newLayout != self.rightSideCurrentFrame:
            self.deleteRightSideFame(self.frameSideRight)
            frameInput = QtWidgets.QFrame(self.frameSideRight)
            sizePolicy = QtWidgets.QSizePolicy(
                QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
            sizePolicy.setHorizontalStretch(0)
            sizePolicy.setVerticalStretch(0)
            sizePolicy.setHeightForWidth(
                frameInput.sizePolicy().hasHeightForWidth())
            frameInput.setSizePolicy(sizePolicy)
            frameInput.setMinimumSize(QtCore.QSize(500, 200))
            frameInput.setStyleSheet("border:none;")
            frameInput.setFrameShape(QtWidgets.QFrame.StyledPanel)
            frameInput.setFrameShadow(QtWidgets.QFrame.Raised)
            frameInput.setObjectName("frame")

            self.inputOldMasterKey = QtWidgets.QLineEdit(frameInput)
            self.inputOldMasterKey.setGeometry(QtCore.QRect(70, 10, 350, 40))
            font = QtGui.QFont()
            font.setFamily("Roboto Mono")
            font.setPointSize(10)
            self.inputOldMasterKey.setFont(font)
            self.inputOldMasterKey.setContextMenuPolicy(
                QtCore.Qt.NoContextMenu)
            self.inputOldMasterKey.setStyleSheet(self.input_Password_Style)
            self.inputOldMasterKey.setPlaceholderText(
                self.language["current master password"])
            self.inputOldMasterKey.setEchoMode(QtWidgets.QLineEdit.Password)
            OldMasterKey = QtWidgets.QPushButton(frameInput)
            OldMasterKey.setGeometry(QtCore.QRect(420, 10, 50, 40))
            OldMasterKey.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
            OldMasterKey.clicked.connect(
                lambda: self.showPassword(self.inputOldMasterKey))
            OldMasterKey.setIcon(QtGui.QIcon("images/showPAssword.png"))
            OldMasterKey.setIconSize(QtCore.QSize(20, 20))
            OldMasterKey.setStyleSheet(self.showButton_Style)

            self.inputNewMasterKey = QtWidgets.QLineEdit(frameInput)
            self.inputNewMasterKey.setGeometry(QtCore.QRect(70, 90, 350, 40))
            self.inputNewMasterKey.setFont(font)
            self.inputNewMasterKey.setStyleSheet(self.input_Password_Style)
            self.inputNewMasterKey.setContextMenuPolicy(
                QtCore.Qt.NoContextMenu)
            self.inputNewMasterKey.setPlaceholderText(
                self.language["new master password"])
            self.inputNewMasterKey.setEchoMode(QtWidgets.QLineEdit.Password)
            showNewPassword = QtWidgets.QPushButton(frameInput)
            showNewPassword.setGeometry(QtCore.QRect(420, 90, 50, 40))
            showNewPassword.setCursor(
                QtGui.QCursor(QtCore.Qt.PointingHandCursor))
            showNewPassword.clicked.connect(
                lambda: self.showPassword(self.inputNewMasterKey))
            showNewPassword.setIcon(QtGui.QIcon("images/showPAssword.png"))
            showNewPassword.setIconSize(QtCore.QSize(20, 20))
            showNewPassword.setStyleSheet(self.showButton_Style)

            self.inputConfirmPassword = QtWidgets.QLineEdit(frameInput)
            self.inputConfirmPassword.setGeometry(
                QtCore.QRect(70, 135, 350, 40))
            self.inputConfirmPassword.setFont(font)
            self.inputConfirmPassword.setStyleSheet(self.input_Password_Style)
            self.inputConfirmPassword.setContextMenuPolicy(
                QtCore.Qt.NoContextMenu)
            self.inputConfirmPassword.setPlaceholderText(
                self.language["repeat password"])
            self.inputConfirmPassword.setEchoMode(QtWidgets.QLineEdit.Password)
            showConfirmPassword = QtWidgets.QPushButton(frameInput)
            showConfirmPassword.setGeometry(QtCore.QRect(420, 135, 50, 40))
            showConfirmPassword.setCursor(
                QtGui.QCursor(QtCore.Qt.PointingHandCursor))
            showConfirmPassword.clicked.connect(
                lambda: self.showPassword(self.inputConfirmPassword))
            showConfirmPassword.setIcon(QtGui.QIcon("images/showPAssword.png"))
            showConfirmPassword.setIconSize(QtCore.QSize(20, 20))
            showConfirmPassword.setStyleSheet(self.showButton_Style)

            self.frameButton = QtWidgets.QFrame(self.frameSideRight)
            sizePolicy = QtWidgets.QSizePolicy(
                QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
            sizePolicy.setHorizontalStretch(0)
            sizePolicy.setVerticalStretch(0)
            sizePolicy.setHeightForWidth(
                self.frameButton.sizePolicy().hasHeightForWidth())
            self.frameButton.setSizePolicy(sizePolicy)
            self.frameButton.setMinimumSize(QtCore.QSize(500, 150))
            self.frameButton.setStyleSheet("border:none;")
            self.frameButton.setFrameShape(QtWidgets.QFrame.StyledPanel)
            self.frameButton.setFrameShadow(QtWidgets.QFrame.Raised)
            self.frameButton.setObjectName("frame_2")
            self.errorText = QtWidgets.QLabel(self.frameButton)
            self.errorText.setGeometry(QtCore.QRect(0, 0, 500, 40))
            self.errorText.setStyleSheet("color:#d43f3f")
            self.errorText.setFont(font)
            self.errorText.setAlignment(QtCore.Qt.AlignCenter)

            btnUpdateMsKe = QtWidgets.QPushButton(self.frameButton)
            btnUpdateMsKe.setGeometry(QtCore.QRect(110, 110, 300, 38))
            sizePolicy = QtWidgets.QSizePolicy(
                QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
            sizePolicy.setHorizontalStretch(0)
            sizePolicy.setVerticalStretch(0)
            sizePolicy.setHeightForWidth(
                btnUpdateMsKe.sizePolicy().hasHeightForWidth())
            btnUpdateMsKe.setSizePolicy(sizePolicy)
            btnUpdateMsKe.setMinimumSize(QtCore.QSize(300, 30))
            btnUpdateMsKe.setSizeIncrement(QtCore.QSize(0, 0))
            btnUpdateMsKe.clicked.connect(self.changeMasterkey)
            font.setFamily("Arial")
            btnUpdateMsKe.setFont(font)
            btnUpdateMsKe.setStyleSheet(btn_style)
            btnUpdateMsKe.setText(self.language["update master password"])
            self.verticalLayout.addWidget(frameInput)
            self.verticalLayout.addWidget(self.frameButton)
            self.rightSideCurrentFrame = newLayout

    def pageDeleteAll(self, newLayout):

        if newLayout != self.rightSideCurrentFrame:
            self.deleteRightSideFame(self.frameSideRight)
            frameInput = QtWidgets.QFrame(self.frameSideRight)
            sizePolicy = QtWidgets.QSizePolicy(
                QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
            sizePolicy.setHorizontalStretch(0)
            sizePolicy.setVerticalStretch(0)
            sizePolicy.setHeightForWidth(
                frameInput.sizePolicy().hasHeightForWidth())
            frameInput.setSizePolicy(sizePolicy)
            frameInput.setMinimumSize(QtCore.QSize(500, 200))
            frameInput.setStyleSheet("border:none;")
            frameInput.setFrameShape(QtWidgets.QFrame.StyledPanel)
            frameInput.setFrameShadow(QtWidgets.QFrame.Raised)
            frameInput.setObjectName("frame")

            self.inputMAsterKey = QtWidgets.QLineEdit(frameInput)
            self.inputMAsterKey.setGeometry(QtCore.QRect(70, 150, 350, 35))
            font = QtGui.QFont()
            font.setFamily("Roboto Mono")
            font.setPointSize(10)
            self.inputMAsterKey.setFont(font)
            self.inputMAsterKey.setContextMenuPolicy(QtCore.Qt.NoContextMenu)
            self.inputMAsterKey.setStyleSheet(self.input_Password_Style)
            self.inputMAsterKey.setPlaceholderText(self.language["master key"])
            self.inputMAsterKey.setEchoMode(QtWidgets.QLineEdit.Password)
            masterKey = QtWidgets.QPushButton(frameInput)
            masterKey.setGeometry(QtCore.QRect(420, 150, 50, 35))
            masterKey.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
            masterKey.clicked.connect(
                lambda: self.showPassword(self.inputMAsterKey))
            masterKey.setIcon(QtGui.QIcon("images/showPAssword.png"))
            masterKey.setIconSize(QtCore.QSize(20, 20))
            masterKey.setStyleSheet(self.showButton_Style)

            self.frameButton = QtWidgets.QFrame(self.frameSideRight)
            sizePolicy = QtWidgets.QSizePolicy(
                QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
            sizePolicy.setHorizontalStretch(0)
            sizePolicy.setVerticalStretch(0)
            sizePolicy.setHeightForWidth(
                self.frameButton.sizePolicy().hasHeightForWidth())
            self.frameButton.setSizePolicy(sizePolicy)
            self.frameButton.setMinimumSize(QtCore.QSize(500, 150))
            self.frameButton.setStyleSheet("border:none;")
            self.frameButton.setFrameShape(QtWidgets.QFrame.StyledPanel)
            self.frameButton.setFrameShadow(QtWidgets.QFrame.Raised)
            self.frameButton.setObjectName("frame_2")
            self.errorText = QtWidgets.QLabel(self.frameButton)
            self.errorText.setGeometry(QtCore.QRect(0, 0, 500, 35))
            self.errorText.setStyleSheet("color:#e83b2e")
            font.setPointSize(11)
            self.errorText.setFont(font)
            self.errorText.setAlignment(QtCore.Qt.AlignCenter)

            btnDelete = QtWidgets.QPushButton(self.frameButton)
            btnDelete.setGeometry(QtCore.QRect(180, 110, 150, 38))
            sizePolicy = QtWidgets.QSizePolicy(
                QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
            sizePolicy.setHorizontalStretch(0)
            sizePolicy.setVerticalStretch(0)
            sizePolicy.setHeightForWidth(
                btnDelete.sizePolicy().hasHeightForWidth())
            btnDelete.setSizePolicy(sizePolicy)
            btnDelete.setSizeIncrement(QtCore.QSize(0, 0))
            btnDelete.clicked.connect(self.deleteAll)
            font.setFamily("Arial")
            font.setPointSize(12)
            btnDelete.setFont(font)
            btnDelete.setStyleSheet(btn_style)
            btnDelete.setText(self.language["delete"])
            btnDelete.setIcon(QtGui.QIcon("Images/danger.png"))
            btnDelete.setIconSize(QtCore.QSize(25, 25))
            self.verticalLayout.setContentsMargins(80, -1, 80, -1)
            self.verticalLayout.addWidget(frameInput)
            self.verticalLayout.addWidget(self.frameButton)
            self.rightSideCurrentFrame = newLayout

    def showAboutPage(self):
        aboutLabel = QtWidgets.QLabel(self.scrollAreaWidgetContents)
        pixmap = QtGui.QPixmap("images/aboutPage.png")
        aboutLabel.setPixmap(pixmap)
        aboutLabel.setAlignment(QtCore.Qt.AlignCenter)
        aboutLabel.setMinimumSize(QtCore.QSize(800, 580))
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.verticalLayout_6.addWidget(self.scrollArea)

    def clearLayout(self, layout, newLayout, refresh=False, message=""):
        if refresh == True:
            self.currentFrame = None
        if newLayout != self.currentFrame:
            for child in layout.children():
                if child != self.verticalLayout_6:
                    child.deleteLater()

            self.scrollArea = QtWidgets.QScrollArea(layout)
            self.scrollArea.setVerticalScrollBarPolicy(
                QtCore.Qt.ScrollBarAsNeeded)
            self.scrollArea.setHorizontalScrollBarPolicy(
                QtCore.Qt.ScrollBarAsNeeded)
            self.scrollArea.setWidgetResizable(True)
            self.scrollArea.setObjectName("scrollArea")
            self.scrollAreaWidgetContents = QtWidgets.QWidget()
            self.scrollAreaWidgetContents.setGeometry(
                QtCore.QRect(0, 0, 673, 771))
            self.scrollAreaWidgetContents.setObjectName(
                "scrollAreaWidgetContents")

            if newLayout == "all":
                self.start(message=message)
                self.currentFrame = "all"
                self.activeButton = self.btnAll_Item
            elif newLayout == "password":
                self.showPasLogNote("password", message="  " + message)
                self.currentFrame = "password"
                self.activeButton = self.btnPassword
            elif newLayout == "login":
                self.showPasLogNote("login", message="  " + message)
                self.currentFrame = "login"
                self.activeButton = self.btnLogin
            elif newLayout == "note":
                self.showPasLogNote("note", message="  " + message)
                self.currentFrame = "note"
                self.activeButton = self.btnNote
            elif newLayout == "about":
                self.showAboutPage()
                self.currentFrame = "about"
                self.activeButton = self.btnAbout
            elif newLayout == "settings":
                self.showSettingsPage()
                self.currentFrame = "settings"
                self.activeButton = self.btnSettings

        self.changeButtonStyle()

    def changeButtonStyle(self):
        for button in self.buttonSideBar:
            if button != self.activeButton:
                button.setStyleSheet(self.btnStyle)
            else:
                button.setStyleSheet(self.btnStyleActive)

    def showButtonsInAddFrame(self, layout, newLayout, message=False):
        if (message == False):
            self.showMessageHere.setText("")
        if newLayout != self.rightSideCurrentFrame:
            for child in layout.children():
                if child != self.verticalLayout:
                    child.deleteLater()

            frameButtonsContainer = QtWidgets.QFrame(layout)
            frameButtonsContainer.setStyleSheet("border:0px;")
            VLayout = QtWidgets.QVBoxLayout(frameButtonsContainer)
            VLayout.setSpacing(15)
            VLayout.setObjectName("verticalLayout")
            self.btnAddPassword = QtWidgets.QPushButton(frameButtonsContainer)
            self.btnAddPassword.setEnabled(True)
            self.btnAddPassword.clicked.connect(
                lambda: self.showAddPasswordPage(self.frameSideRight, "addPassword"))
            sizePolicy = QtWidgets.QSizePolicy(
                QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
            sizePolicy.setHorizontalStretch(0)
            sizePolicy.setVerticalStretch(0)
            sizePolicy.setHeightForWidth(
                self.btnAddPassword.sizePolicy().hasHeightForWidth())
            self.btnAddPassword.setSizePolicy(sizePolicy)
            self.btnAddPassword.setMinimumSize(QtCore.QSize(400, 50))
            self.btnAddPassword.setCursor(
                QtGui.QCursor(QtCore.Qt.PointingHandCursor))
            font = QtGui.QFont()
            font.setFamily("Roboto Mono")
            font.setPointSize(14)
            self.btnAddPassword.setFont(font)
            self.btnAddPassword.setStyleSheet(self.otherButtons_style)
            self.btnAddPassword.setObjectName("btnAddPassword")
            VLayout.addWidget(self.btnAddPassword)
            self.btnAddLogin = QtWidgets.QPushButton(frameButtonsContainer)
            self.btnAddLogin.setCursor(
                QtGui.QCursor(QtCore.Qt.PointingHandCursor))
            sizePolicy = QtWidgets.QSizePolicy(
                QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
            sizePolicy.setHorizontalStretch(0)
            sizePolicy.setVerticalStretch(0)
            sizePolicy.setHeightForWidth(
                self.btnAddLogin.sizePolicy().hasHeightForWidth())
            self.btnAddLogin.setSizePolicy(sizePolicy)
            self.btnAddLogin.setMinimumSize(QtCore.QSize(400, 50))
            font = QtGui.QFont()
            font.setFamily("Roboto Mono")
            font.setPointSize(14)
            self.btnAddLogin.setFont(font)
            self.btnAddLogin.setStyleSheet(self.otherButtons_style)
            self.btnAddLogin.setObjectName("btnAddLogin")
            self.btnAddLogin.clicked.connect(
                lambda: self.showAddLoginPage(self.frameSideRight, "addLogin"))
            VLayout.addWidget(self.btnAddLogin)
            self.btnAddNote = QtWidgets.QPushButton(frameButtonsContainer)
            sizePolicy = QtWidgets.QSizePolicy(
                QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
            sizePolicy.setHorizontalStretch(0)
            sizePolicy.setVerticalStretch(0)
            sizePolicy.setHeightForWidth(
                self.btnAddNote.sizePolicy().hasHeightForWidth())
            self.btnAddNote.setSizePolicy(sizePolicy)
            self.btnAddNote.setMinimumSize(QtCore.QSize(400, 50))
            self.btnAddNote.setCursor(
                QtGui.QCursor(QtCore.Qt.PointingHandCursor))
            font = QtGui.QFont()
            font.setFamily("Roboto Mono")
            font.setPointSize(14)
            self.btnAddNote.setFont(font)
            self.btnAddNote.setStyleSheet(self.otherButtons_style)
            self.btnAddNote.setObjectName("btnAddNote")
            self.btnAddNote.clicked.connect(
                lambda: self.showAddNotePage(self.frameSideRight, "addNote"))
            VLayout.addWidget(self.btnAddNote)

            spacerItem1 = QtWidgets.QSpacerItem(
                20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
            VLayout.addItem(spacerItem1)
            self.btnAddPassword.setText(self.language["password"])
            self.btnAddLogin.setText(self.language["login"])
            self.btnAddNote.setText(self.language["note"])

            self.verticalLayout.setContentsMargins(150, 150, -1, -1)
            self.verticalLayout.addWidget(frameButtonsContainer)

            self.rightSideCurrentFrame = newLayout

    def deleteRightSideFame(self, layout):
        for child in layout.children():
            if child != self.verticalLayout:
                child.deleteLater()

    def showAddPasswordPage(self, layout, newLayout, itemID=None):
        self.showMessageHere.setText("")
        itemAttributes = {"name": "", "username": "",
                          "password": "", "moreInfo": "", "date_time": ""}
        addButtonText = self.language["add"]

        if itemID != None:
            passwordGotFromDB = self.db.getPasswordById(itemID)
            if passwordGotFromDB != []:
                itemAttributes['name'] = passwordGotFromDB[2]
                itemAttributes['username'] = passwordGotFromDB[3]
                itemAttributes['password'] = passwordGotFromDB[4]
                itemAttributes['moreInfo'] = passwordGotFromDB[5]
                date = datetime.strptime(
                    passwordGotFromDB[6], "%Y-%m-%d %H:%M:%S.%f")
                itemAttributes['date_time'] = self.language["created at"] + "    " + date.strftime(
                    "%B %d, %Y  %H:%M:%S")
                self.rightSideCurrentFrame = itemID
                addButtonText = self.language["update"]
            else:
                return

        def txtInputChanged():
            cursor = self.inputMoreInfo.textCursor()
            if len(self.inputMoreInfo.toPlainText()) > 300:
                text = self.inputMoreInfo.toPlainText()
                text = text[:300]
                self.inputMoreInfo.setPlainText(text)

                cursor = self.inputMoreInfo.textCursor()
            cursor.setPosition(300)
            self.inputMoreInfo.setTextCursor(cursor)

        if newLayout != self.rightSideCurrentFrame:
            self.deleteRightSideFame(layout)

            frameAdd = QtWidgets.QFrame(layout)
            frameAdd.setFrameShape(QtWidgets.QFrame.StyledPanel)
            frameAdd.setFrameShadow(QtWidgets.QFrame.Raised)
            frameAdd.setStyleSheet("border:0;")
            font = QtGui.QFont()
            font.setPointSize(12)

            self.inputName = QtWidgets.QLineEdit(frameAdd)
            self.inputName.setGeometry(QtCore.QRect(150, 40, 400, 41))
            self.inputName.setStyleSheet(self.input_Style_main)
            font = QtGui.QFont()
            font.setFamily("Roboto Mono")
            font.setPointSize(12)
            self.inputName.setFont(font)
            self.inputName.setMaxLength(50)
            self.inputName.setText(itemAttributes['name'])
            labelName = QtWidgets.QLabel(frameAdd)
            labelName.setGeometry(QtCore.QRect(0, 50, 130, 21))
            labelName.setFont(font)
            labelName.setText(self.language["name"])
            labelName.setStyleSheet("border:0;")
            font.setPointSize(8)

            lblDate_Time = QtWidgets.QLabel(frameAdd)
            lblDate_Time.setGeometry(QtCore.QRect(150, 82, 400, 21))
            lblDate_Time.setText(itemAttributes['date_time'])
            lblDate_Time.setStyleSheet("color:#000")
            lblDate_Time.setFont(font)
            font.setPointSize(12)

            self.inputUsername = QtWidgets.QLineEdit(frameAdd)
            self.inputUsername.setGeometry(QtCore.QRect(150, 160, 300, 41))
            self.inputUsername.setFont(font)
            self.inputUsername.setMaxLength(50)
            self.inputUsername.setStyleSheet(self.input_Style_main)
            self.inputUsername.setText(itemAttributes['username'])
            labelUsername = QtWidgets.QLabel(frameAdd)
            labelUsername.setGeometry(QtCore.QRect(0, 170, 150, 21))
            labelUsername.setFont(font)
            labelUsername.setText(self.language["username"])
            labelUsername.setStyleSheet("border:0;")

            self.inputPassword = QtWidgets.QLineEdit(frameAdd)
            self.inputPassword.setGeometry(QtCore.QRect(150, 230, 400, 41))
            self.inputPassword.setFont(font)
            self.inputPassword.setStyleSheet(self.input_Password_Style)
            self.inputPassword.setMaxLength(100)
            self.inputPassword.setEchoMode(QtWidgets.QLineEdit.Password)
            self.inputPassword.setText(itemAttributes['password'])
            labelPassword = QtWidgets.QLabel(frameAdd)
            labelPassword.setGeometry(QtCore.QRect(0, 240, 130, 21))
            labelPassword.setFont(font)
            labelPassword.setText(self.language["password"])
            labelPassword.setStyleSheet("border:0;")

            showNewPassword = QtWidgets.QPushButton(frameAdd)
            showNewPassword.setGeometry(QtCore.QRect(550, 230, 50, 41))
            showNewPassword.setCursor(
                QtGui.QCursor(QtCore.Qt.PointingHandCursor))
            showNewPassword.clicked.connect(
                lambda: self.showPassword(self.inputPassword))
            showNewPassword.setIcon(QtGui.QIcon("images/showPAssword.png"))
            showNewPassword.setIconSize(QtCore.QSize(20, 20))
            showNewPassword.setStyleSheet(self.showButton_Style)
            self.inputMoreInfo = QtWidgets.QTextEdit(frameAdd)
            self.inputMoreInfo.setGeometry(QtCore.QRect(150, 310, 450, 120))
            font.setPointSize(10)
            self.inputMoreInfo.setFont(font)
            self.inputMoreInfo.textChanged.connect(txtInputChanged)
            self.inputMoreInfo.setStyleSheet(self.input_Style_main)
            self.inputMoreInfo.setText(itemAttributes['moreInfo'])
            labelMoreInfo = QtWidgets.QLabel(frameAdd)
            labelMoreInfo.setGeometry(QtCore.QRect(0, 360, 130, 21))
            labelMoreInfo.setFont(font)
            labelMoreInfo.setText(self.language["more information"])
            labelMoreInfo.setStyleSheet("border:0;")

            self.btnAddToDatabase = QtWidgets.QPushButton(frameAdd)
            self.btnAddToDatabase.setGeometry(QtCore.QRect(270, 750, 141, 41))
            font = QtGui.QFont()
            font.setFamily("Segoe UI Semibold")
            font.setPointSize(12)
            font.setBold(True)
            font.setWeight(75)
            self.btnAddToDatabase.setFont(font)
            self.btnAddToDatabase.setCursor(
                QtGui.QCursor(QtCore.Qt.PointingHandCursor))
            self.btnAddToDatabase.setStyleSheet(btn_style)
            self.btnAddToDatabase.setDefault(True)
            self.btnAddToDatabase.setText(addButtonText)
            self.btnAddToDatabase.clicked.connect(
                lambda: self.addDataToDataBase(itemID))

            if itemID != None:
                self.btnAddToDatabase.setIcon(
                    QtGui.QIcon('Images/updated.png'))
                self.btnAddToDatabase.setGeometry(
                    QtCore.QRect(380, 750, 141, 41))
                self.btnDeleteItem = QtWidgets.QPushButton(frameAdd)
                self.btnDeleteItem.setGeometry(QtCore.QRect(230, 750, 141, 41))
                self.btnDeleteItem.setFont(font)
                self.btnDeleteItem.setCursor(
                    QtGui.QCursor(QtCore.Qt.PointingHandCursor))
                self.btnDeleteItem.setStyleSheet(self.button_Delete_style)
                self.btnDeleteItem.setDefault(True)
                self.btnDeleteItem.setText(self.language["delete"])
                self.btnDeleteItem.setIcon(QtGui.QIcon('Images/delete.png'))
                self.btnDeleteItem.setIconSize(QtCore.QSize(20, 20))
                self.btnDeleteItem.clicked.connect(lambda: self.deleteData(
                    self.inputName.text(), 'password', itemID))

            self.verticalLayout.setContentsMargins(30, 30, -1, -1)
            self.verticalLayout.addWidget(frameAdd)
            self.rightSideCurrentFrame = newLayout

    def deleteData(self, name, dataType, itemID):
        askForConfirmation = QMessageBox.warning(self, self.language["confiramtion"],
                                                 f"\n\n{self.language['are you sure you want to delete']} ' {name} ' ?\t\t\n\n",
                                                 QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        self.setFocus()

        if askForConfirmation == QMessageBox.Yes:
            if dataType == "password":
                self.db.deletePassword(itemID)
                self.clearLayout(self.frameShowPasswords, "password", refresh=True,
                                 message=f"' {name} ' " + self.language["was deleted successfully"])
            elif dataType == "login":
                self.db.deleteLogin(itemID)
                self.clearLayout(self.frameShowPasswords, "login", refresh=True,
                                 message=f"' {name} ' " + self.language["was deleted successfully"])
            elif dataType == "note":
                self.db.deleteNote(itemID)
                self.clearLayout(self.frameShowPasswords, "note", refresh=True,
                                 message=f"' {name} ' " + self.language["was deleted successfully"])
            self.showButtonsInAddFrame(
                self.frameSideRight, "new", message=True)

    def addDataToDataBase(self, itemID):
        if self.rightSideCurrentFrame == "addPassword":
            name = self.inputName.text()
            username = self.inputUsername.text()
            password = self.inputPassword.text()
            more = self.inputMoreInfo.toPlainText()
            if itemID == None:
                self.db.addPassword(name, username, password, more)
                self.clearLayout(self.frameShowPasswords, "password", refresh=True,
                                 message=self.language["your new password added to your list!"])
            else:
                self.db.addPassword(name, username, password,
                                    more, idNumber=itemID)
                self.clearLayout(self.frameShowPasswords, "password", refresh=True,
                                 message=self.language["your password was updated successfully!"])

        elif self.rightSideCurrentFrame == "addLogin":
            name = self.inputName.text()
            username = self.inputUsername.text()
            url = self.choseUrl.currentText()
            if self.choseUrl.currentText() == "custom url":
                url = self.inputURL.text()
            password = self.inputPassword.text()
            email = self.inputEmail.text()
            phone = self.inputPhoneNumber.text()
            more = self.inputMoreInfo.toPlainText()
            if itemID == None:
                self.db.addLogin(name, username, url,
                                 password, email, phone, more)
                self.clearLayout(self.frameShowPasswords, "login", refresh=True,
                                 message=self.language["your new login added to your list!"])
            else:
                self.db.addLogin(name, username, url, password,
                                 email, phone, more, idNumber=itemID)
                self.clearLayout(self.frameShowPasswords, "login", refresh=True,
                                 message=self.language["your login was updated successfully!"])

        elif self.rightSideCurrentFrame == "addNote":
            title = self.title.text()
            text = self.inputText.toPlainText()
            if itemID == None:
                self.db.addNote(title, text)
                self.clearLayout(self.frameShowPasswords, "note", refresh=True,
                                 message=self.language["your new note added to your list!"])
            else:
                self.db.addNote(title, text, idNumber=itemID)
                self.clearLayout(self.frameShowPasswords, "note", refresh=True,
                                 message=self.language["your login was updated successfully!"])

        self.showButtonsInAddFrame(self.frameSideRight, "new", message=True)

    def showAddLoginPage(self, layout, newLayout, itemID=None):
        self.showMessageHere.setText("")
        itemAttributes = {"name": "", "username": "", "url": "", "password": "", "email": "", "phoneNumber": "",
                          "moreInfo": "", "date_time": ""}
        addButtonText = self.language["add"]
        currentUrl = ""

        if itemID != None:
            passwordGotFromDB = self.db.getLoginById(itemID)
            if passwordGotFromDB != []:
                currentUrl = passwordGotFromDB[4]
                itemAttributes['name'] = passwordGotFromDB[2]
                itemAttributes['username'] = passwordGotFromDB[3]
                try:
                    itemAttributes['url'] = self.links[passwordGotFromDB[4]]
                except KeyError:
                    itemAttributes['url'] = passwordGotFromDB[4]
                itemAttributes['password'] = passwordGotFromDB[5]
                itemAttributes['email'] = passwordGotFromDB[6]
                itemAttributes['phoneNumber'] = passwordGotFromDB[7]
                itemAttributes['moreInfo'] = passwordGotFromDB[8]
                date = datetime.strptime(
                    passwordGotFromDB[9], "%Y-%m-%d %H:%M:%S.%f")
                itemAttributes['date_time'] = self.language["created at"] + "    " + date.strftime(
                    "%B %d, %Y  %H:%M:%S")
                self.rightSideCurrentFrame = itemID
                addButtonText = self.language["update"]
            else:
                return

        def txtInputChanged():
            cursor = self.inputMoreInfo.textCursor()
            if len(self.inputMoreInfo.toPlainText()) > 300:
                text = self.inputMoreInfo.toPlainText()
                text = text[:300]
                self.inputMoreInfo.setPlainText(text)

                cursor = self.inputMoreInfo.textCursor()
            cursor.setPosition(300)
            self.inputMoreInfo.setTextCursor(cursor)

        if newLayout != self.rightSideCurrentFrame:
            self.deleteRightSideFame(layout)

            self.scrollAreaAddPages = QtWidgets.QScrollArea(layout)
            sizePolicy = QtWidgets.QSizePolicy(
                QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
            sizePolicy.setHorizontalStretch(0)
            sizePolicy.setVerticalStretch(0)
            sizePolicy.setHeightForWidth(
                self.scrollAreaAddPages.sizePolicy().hasHeightForWidth())
            self.scrollAreaAddPages.setSizePolicy(sizePolicy)
            self.scrollAreaAddPages.setSizeAdjustPolicy(
                QtWidgets.QAbstractScrollArea.AdjustToContents)
            self.scrollAreaAddPages.setWidgetResizable(False)
            self.scrollAreaAddPages.setStyleSheet("border:0;")
            self.verticalLayout.addWidget(self.scrollAreaAddPages)

            scrollAreaWidgetContents = QtWidgets.QWidget()

            font = QtGui.QFont()
            font.setFamily("Roboto Mono")
            font.setPointSize(12)
            self.inputName = QtWidgets.QLineEdit(scrollAreaWidgetContents)
            self.inputName.setGeometry(QtCore.QRect(150, 40, 400, 41))
            self.inputName.setStyleSheet(self.input_Style_main)
            self.inputName.setFont(font)
            self.inputName.setMaxLength(50)
            self.inputName.setText(itemAttributes['name'])
            labelName = QtWidgets.QLabel(scrollAreaWidgetContents)
            labelName.setGeometry(QtCore.QRect(0, 50, 130, 21))
            labelName.setFont(font)
            labelName.setText(self.language["name"])
            labelName.setStyleSheet("border:0;")

            lblDate_Time = QtWidgets.QLabel(scrollAreaWidgetContents)
            lblDate_Time.setGeometry(QtCore.QRect(150, 82, 400, 21))
            lblDate_Time.setText(itemAttributes['date_time'])
            lblDate_Time.setStyleSheet("color:#000")
            font.setPointSize(8)
            lblDate_Time.setFont(font)
            font.setPointSize(12)

            self.inputUsername = QtWidgets.QLineEdit(scrollAreaWidgetContents)
            self.inputUsername.setGeometry(QtCore.QRect(150, 160, 300, 41))
            self.inputUsername.setFont(font)
            self.inputUsername.setMaxLength(50)
            self.inputUsername.setStyleSheet(self.input_Style_main)
            self.inputUsername.setText(itemAttributes['username'])
            labelUsername = QtWidgets.QLabel(scrollAreaWidgetContents)
            labelUsername.setGeometry(QtCore.QRect(0, 170, 130, 21))
            labelUsername.setFont(font)
            labelUsername.setText(self.language["username"])
            labelUsername.setStyleSheet("border:0;")

            self.choseUrl = QtWidgets.QComboBox(scrollAreaWidgetContents)
            self.choseUrl.setGeometry(QtCore.QRect(150, 230, 150, 30))
            font.setPointSize(11)
            font.setBold(False)
            self.choseUrl.setFont(font)
            self.choseUrl.setStyleSheet(
                "border: 1px solid #2e2e2e; border-radius: 1px;background-color:rgba(250,250,250,0.90);color:black;")
            self.choseUrl.setObjectName("choseUrl")
            self.choseUrl.activated[str].connect(self.onActivated)
            for link in self.links.keys():
                self.choseUrl.addItem(link)
            if currentUrl != "":
                try:
                    self.choseUrl.setCurrentText(currentUrl)
                except:
                    self.choseUrl.setCurrentText("custom url")
            self.inputURL = QtWidgets.QLineEdit(scrollAreaWidgetContents)
            self.inputURL.setGeometry(QtCore.QRect(150, 260, 400, 41))
            self.inputURL.setFont(font)
            self.inputURL.setStyleSheet(self.input_Style_main)
            self.inputURL.setMaxLength(500)
            self.inputURL.setText(itemAttributes['url'])

            labelURL = QtWidgets.QLabel(scrollAreaWidgetContents)
            labelURL.setGeometry(QtCore.QRect(0, 260, 130, 21))
            labelURL.setFont(font)
            labelURL.setText("URL")
            labelURL.setStyleSheet("border:0;")

            self.inputPassword = QtWidgets.QLineEdit(scrollAreaWidgetContents)
            self.inputPassword.setGeometry(QtCore.QRect(150, 340, 400, 41))
            self.inputPassword.setFont(font)
            self.inputPassword.setStyleSheet(self.input_Password_Style)
            self.inputPassword.setMaxLength(100)
            self.inputPassword.setEchoMode(QtWidgets.QLineEdit.Password)
            self.inputPassword.setText(itemAttributes['password'])
            labelPassword = QtWidgets.QLabel(scrollAreaWidgetContents)
            labelPassword.setGeometry(QtCore.QRect(0, 340, 130, 21))
            labelPassword.setFont(font)
            labelPassword.setText(self.language["password"])
            labelPassword.setStyleSheet("border:0;")

            showNewPassword = QtWidgets.QPushButton(scrollAreaWidgetContents)
            showNewPassword.setGeometry(QtCore.QRect(550, 340, 50, 41))
            showNewPassword.setCursor(
                QtGui.QCursor(QtCore.Qt.PointingHandCursor))
            showNewPassword.clicked.connect(
                lambda: self.showPassword(self.inputPassword))
            showNewPassword.setIcon(QtGui.QIcon("images/showPAssword.png"))
            showNewPassword.setIconSize(QtCore.QSize(20, 20))
            showNewPassword.setStyleSheet(self.showButton_Style)

            self.inputEmail = QtWidgets.QLineEdit(scrollAreaWidgetContents)
            self.inputEmail.setGeometry(QtCore.QRect(150, 420, 400, 41))
            self.inputEmail.setFont(font)
            self.inputEmail.setMaxLength(70)
            self.inputEmail.setStyleSheet(self.input_Style_main)
            self.inputEmail.setText(itemAttributes['email'])
            labelEmail = QtWidgets.QLabel(scrollAreaWidgetContents)
            labelEmail.setGeometry(QtCore.QRect(0, 430, 130, 21))
            labelEmail.setFont(font)
            labelEmail.setText(self.language["email"])
            labelEmail.setStyleSheet("border:0;")

            self.inputPhoneNumber = QtWidgets.QLineEdit(
                scrollAreaWidgetContents)
            self.inputPhoneNumber.setGeometry(QtCore.QRect(150, 490, 300, 41))
            self.inputPhoneNumber.setFont(font)
            self.inputPhoneNumber.setMaxLength(50)
            self.inputPhoneNumber.setStyleSheet(self.input_Style_main)
            self.inputPhoneNumber.setText(itemAttributes['phoneNumber'])
            labelPhoneNumber = QtWidgets.QLabel(scrollAreaWidgetContents)
            labelPhoneNumber.setGeometry(QtCore.QRect(0, 500, 130, 21))
            labelPhoneNumber.setFont(font)
            labelPhoneNumber.setText(self.language["phone number"])
            labelPhoneNumber.setStyleSheet("border:0;")

            self.inputMoreInfo = QtWidgets.QTextEdit(scrollAreaWidgetContents)
            self.inputMoreInfo.setGeometry(QtCore.QRect(150, 560, 450, 120))
            font.setPointSize(10)
            self.inputMoreInfo.setFont(font)
            self.inputMoreInfo.textChanged.connect(txtInputChanged)
            self.inputMoreInfo.setStyleSheet(self.input_Style_main)
            self.inputMoreInfo.setText(itemAttributes['moreInfo'])
            labelMoreInfo = QtWidgets.QLabel(scrollAreaWidgetContents)
            labelMoreInfo.setGeometry(QtCore.QRect(0, 600, 130, 21))
            labelMoreInfo.setFont(font)
            labelMoreInfo.setText(self.language["more information"])
            labelMoreInfo.setStyleSheet("border:0;")

            self.btnAddToDatabase = QtWidgets.QPushButton(
                scrollAreaWidgetContents)
            self.btnAddToDatabase.setGeometry(QtCore.QRect(270, 750, 141, 41))
            font = QtGui.QFont()
            font.setFamily("Segoe UI Semibold")
            font.setPointSize(12)
            font.setBold(True)
            font.setWeight(75)
            self.btnAddToDatabase.setFont(font)
            self.btnAddToDatabase.setCursor(
                QtGui.QCursor(QtCore.Qt.PointingHandCursor))
            self.btnAddToDatabase.setStyleSheet(btn_style)
            self.btnAddToDatabase.setDefault(True)
            self.btnAddToDatabase.setText(addButtonText)
            self.btnAddToDatabase.clicked.connect(
                lambda: self.addDataToDataBase(itemID))

            if itemID != None:
                self.btnAddToDatabase.setIcon(
                    QtGui.QIcon('Images/updated.png'))
                self.btnAddToDatabase.setGeometry(
                    QtCore.QRect(380, 750, 141, 41))
                self.btnDeleteItem = QtWidgets.QPushButton(
                    scrollAreaWidgetContents)
                self.btnDeleteItem.setGeometry(QtCore.QRect(230, 750, 141, 41))
                self.btnDeleteItem.setFont(font)
                self.btnDeleteItem.setCursor(
                    QtGui.QCursor(QtCore.Qt.PointingHandCursor))
                self.btnDeleteItem.setStyleSheet(self.button_Delete_style)
                self.btnDeleteItem.setText(self.language["delete"])
                self.btnDeleteItem.setIcon(QtGui.QIcon('Images/delete.png'))
                self.btnDeleteItem.setIconSize(QtCore.QSize(20, 20))
                self.btnDeleteItem.clicked.connect(
                    lambda: self.deleteData(self.inputName.text(), 'login', itemID))

            self.verticalLayout.setContentsMargins(30, 30, -1, -1)
            scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 654, 900))

            self.scrollAreaAddPages.setWidget(scrollAreaWidgetContents)
            self.rightSideCurrentFrame = newLayout

    def onActivated(self):
        text = self.choseUrl.currentText()
        self.inputURL.setText(self.links[text])

    def showAddNotePage(self, layout, newLayout, itemID=None):
        self.showMessageHere.setText("")
        itemAttributes = {"title": "", "text": "", "date_time": ""}
        addButtonText = self.language["add"]

        if itemID != None:
            passwordGotFromDB = self.db.getNoteById(itemID)
            if passwordGotFromDB != []:
                itemAttributes['title'] = passwordGotFromDB[2]
                itemAttributes['text'] = passwordGotFromDB[3]
                date = datetime.strptime(
                    passwordGotFromDB[4], "%Y-%m-%d %H:%M:%S.%f")
                itemAttributes['date_time'] = self.language["created at"] + "    " + date.strftime(
                    "%B %d, %Y  %H:%M:%S")

                self.rightSideCurrentFrame = itemID
                addButtonText = self.language["update"]
            else:
                return

        def txtInputChanged():
            cursor = self.inputText.textCursor()
            if len(self.inputText.toPlainText()) > 300:
                text = self.inputText.toPlainText()
                text = text[:300]
                self.inputText.setPlainText(text)

                cursor = self.inputText.textCursor()
            cursor.setPosition(300)
            self.inputText.setTextCursor(cursor)

        if newLayout != self.rightSideCurrentFrame:
            self.deleteRightSideFame(layout)

            self.scrollAreaAddPages = QtWidgets.QScrollArea(layout)
            sizePolicy = QtWidgets.QSizePolicy(
                QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
            sizePolicy.setHorizontalStretch(0)
            sizePolicy.setVerticalStretch(0)
            sizePolicy.setHeightForWidth(
                self.scrollAreaAddPages.sizePolicy().hasHeightForWidth())
            self.scrollAreaAddPages.setSizePolicy(sizePolicy)
            self.scrollAreaAddPages.setSizeAdjustPolicy(
                QtWidgets.QAbstractScrollArea.AdjustToContents)
            self.scrollAreaAddPages.setWidgetResizable(False)
            self.scrollAreaAddPages.setStyleSheet("border:0;")
            self.verticalLayout.addWidget(self.scrollAreaAddPages)

            scrollAreaWidgetContents = QtWidgets.QWidget()

            font = QtGui.QFont()
            font.setFamily("Roboto Mono")
            font.setPointSize(12)

            self.title = QtWidgets.QLineEdit(scrollAreaWidgetContents)
            self.title.setGeometry(QtCore.QRect(150, 120, 400, 41))
            self.title.setFont(font)
            self.title.setMaxLength(100)
            self.title.setStyleSheet(self.input_Style_main)
            self.title.setText(itemAttributes['title'])
            labelTitle = QtWidgets.QLabel(scrollAreaWidgetContents)
            labelTitle.setGeometry(QtCore.QRect(0, 130, 130, 21))
            labelTitle.setFont(font)
            labelTitle.setText(self.language["title"])
            labelTitle.setStyleSheet("border:0;")

            lblDate_Time = QtWidgets.QLabel(scrollAreaWidgetContents)
            lblDate_Time.setGeometry(QtCore.QRect(150, 162, 400, 21))
            lblDate_Time.setText(itemAttributes['date_time'])
            lblDate_Time.setStyleSheet("color:#000")
            font.setPointSize(8)
            lblDate_Time.setFont(font)
            font.setPointSize(12)

            self.inputText = QtWidgets.QTextEdit(scrollAreaWidgetContents)
            self.inputText.setGeometry(QtCore.QRect(150, 230, 400, 160))
            font.setPointSize(12)
            self.inputText.setFont(font)
            self.inputText.textChanged.connect(txtInputChanged)
            self.inputText.setStyleSheet(self.input_Style_main)
            self.inputText.setText(itemAttributes['text'])
            labelText = QtWidgets.QLabel(scrollAreaWidgetContents)
            labelText.setGeometry(QtCore.QRect(0, 280, 130, 21))
            labelText.setFont(font)
            labelText.setText(self.language["text"])
            labelText.setStyleSheet("border:0;")

            self.btnAddToDatabase = QtWidgets.QPushButton(
                scrollAreaWidgetContents)
            self.btnAddToDatabase.setGeometry(QtCore.QRect(270, 750, 141, 41))
            font = QtGui.QFont()
            font.setFamily("Segoe UI Semibold")
            font.setPointSize(12)
            font.setBold(True)
            font.setWeight(75)
            self.btnAddToDatabase.setFont(font)
            self.btnAddToDatabase.setCursor(
                QtGui.QCursor(QtCore.Qt.PointingHandCursor))
            self.btnAddToDatabase.setStyleSheet(btn_style)
            self.btnAddToDatabase.setDefault(True)
            self.btnAddToDatabase.setText(addButtonText)
            self.btnAddToDatabase.clicked.connect(
                lambda: self.addDataToDataBase(itemID))

            if itemID != None:
                self.btnAddToDatabase.setIcon(
                    QtGui.QIcon('Images/updated.png'))
                self.btnAddToDatabase.setGeometry(
                    QtCore.QRect(380, 750, 141, 41))
                self.btnDeleteItem = QtWidgets.QPushButton(
                    scrollAreaWidgetContents)
                self.btnDeleteItem.setGeometry(QtCore.QRect(230, 750, 141, 41))
                self.btnDeleteItem.setFont(font)
                self.btnDeleteItem.setCursor(
                    QtGui.QCursor(QtCore.Qt.PointingHandCursor))
                self.btnDeleteItem.setStyleSheet(self.button_Delete_style)
                self.btnDeleteItem.setDefault(True)
                self.btnDeleteItem.setText(self.language["delete"])
                self.btnDeleteItem.setIcon(QtGui.QIcon('Images/delete.png'))
                self.btnDeleteItem.setIconSize(QtCore.QSize(20, 20))
                self.btnDeleteItem.clicked.connect(
                    lambda: self.deleteData(self.title.text(), 'note', itemID))

            self.verticalLayout.setContentsMargins(30, 30, -1, -1)
            scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 654, 900))

            self.scrollAreaAddPages.setWidget(scrollAreaWidgetContents)
            self.rightSideCurrentFrame = newLayout

    def showPassword(self, widget):
        if widget.echoMode() == QtWidgets.QLineEdit.Password:
            widget.setEchoMode(QtWidgets.QLineEdit.Normal)
        else:
            widget.setEchoMode(QtWidgets.QLineEdit.Password)

    # After user clicked on 'update master key' button this funcktion will be run
    # It will check if the password user entered is correct
    # And if it is so the password will be change
    def changeMasterkey(self):
        self.errorText.setText("")
        if self.inputOldMasterKey.text() == self.masterKey:
            self.masterKey = self.inputOldMasterKey.text()
            if len(self.inputNewMasterKey.text()) >= 8:
                if self.inputNewMasterKey.text() == self.inputConfirmPassword.text():
                    self.db.updateData(self.inputNewMasterKey.text())
                    self.showMessageHere.setText(
                        "\t" + self.language["your master key changed successfully"])
                else:
                    self.errorText.setText(
                        self.language['passwords you entered are not matched'])
            else:
                self.errorText.setText(
                    self.language["your masterkey length should be at least 8 characters"])
        else:
            self.errorText.setText(
                self.language["the master password is incorrect!"])

    def deleteAll(self):
        if self.inputMAsterKey.text() == self.masterKey:
            question = QMessageBox.question(self, "",
                                            f"\n  {self.language['Are you sure you want to delete everything?']}\t\n"
                                            f"   {self.language['You will not be able to get back your data!']}\t\n",
                                            QMessageBox.Yes, QMessageBox.Cancel)
            if question == QMessageBox.Yes:
                self.db.closeDB()
                os.remove("data.KeepUrPass")
                os.remove("key.txt")
                self.close()
                sys.exit()
        else:
            self.errorText.setText(self.language["incorrect password"])

    def showFrameGenPassword(self, layout, newLayout):
        if newLayout != self.currentFrame:
            for child in layout.children():
                if child != self.verticalLayout_6:
                    child.deleteLater()

            font = QtGui.QFont()
            font.setFamily("Arial")
            font.setPointSize(11)
            self.frameGenreratePass = QtWidgets.QFrame(self.frameShowPasswords)
            self.frameGenreratePass.setFrameShape(QtWidgets.QFrame.StyledPanel)
            self.frameGenreratePass.setFrameShadow(QtWidgets.QFrame.Raised)
            self.frameGenreratePass.setObjectName("frameGenreratePass")
            self.gridLayout_4 = QtWidgets.QGridLayout(self.frameGenreratePass)
            self.gridLayout_4.setContentsMargins(0, 0, 0, 0)
            self.gridLayout_4.setSpacing(0)
            self.gridLayout_4.setObjectName("gridLayout_4")
            self.lblYourPassword = QtWidgets.QLabel(self.frameGenreratePass)
            sizePolicy = QtWidgets.QSizePolicy(
                QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
            sizePolicy.setHorizontalStretch(0)
            sizePolicy.setVerticalStretch(0)
            sizePolicy.setHeightForWidth(
                self.lblYourPassword.sizePolicy().hasHeightForWidth())
            self.lblYourPassword.setSizePolicy(sizePolicy)
            self.lblYourPassword.setMinimumSize(QtCore.QSize(400, 0))
            self.lblYourPassword.setSizeIncrement(QtCore.QSize(0, 0))
            self.lblYourPassword.setBaseSize(QtCore.QSize(0, 0))
            self.lblYourPassword.setText("")
            self.lblYourPassword.setFont(font)
            self.lblYourPassword.setStyleSheet("color:white;")
            self.lblYourPassword.setAlignment(QtCore.Qt.AlignCenter)
            self.lblYourPassword.setWordWrap(False)
            self.lblYourPassword.setObjectName("lblYourPassword")
            self.gridLayout_4.addWidget(self.lblYourPassword, 5, 1, 1, 1)
            spacerItem2 = QtWidgets.QSpacerItem(
                20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Preferred)
            self.gridLayout_4.addItem(spacerItem2, 8, 1, 1, 1)
            spacerItem3 = QtWidgets.QSpacerItem(
                150, 20, QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Minimum)
            self.gridLayout_4.addItem(spacerItem3, 9, 0, 1, 1)
            self.slider = QtWidgets.QSlider(self.frameGenreratePass)
            sizePolicy = QtWidgets.QSizePolicy(
                QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
            sizePolicy.setHorizontalStretch(0)
            sizePolicy.setVerticalStretch(0)
            sizePolicy.setHeightForWidth(
                self.slider.sizePolicy().hasHeightForWidth())
            self.slider.setSizePolicy(sizePolicy)
            self.slider.setStyleSheet("""
                QSlider::groove:horizontal {
                    height:5px;
                    background-color:#000;
                    }
                QSlider::handle:horizontal {
                    background-color: #002b4a;
                    border:none;
                    height: 30px;
                    width: 10px;
                    margin: -15px 0px;
    }
                """)
            self.slider.setMinimumSize(QtCore.QSize(400, 0))
            self.slider.setOrientation(QtCore.Qt.Horizontal)
            self.slider.setObjectName("slider")
            self.slider.setMinimum(6)
            self.slider.setMaximum(50)
            self.slider.setValue(8)
            self.slider.setSingleStep(1)
            self.slider.valueChanged.connect(self.valuechange)
            self.gridLayout_4.addWidget(self.slider, 3, 1, 1, 1)
            spacerItem4 = QtWidgets.QSpacerItem(
                20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Preferred)
            self.gridLayout_4.addItem(spacerItem4, 10, 1, 1, 1)
            self.labelTitle = QtWidgets.QLabel(self.frameGenreratePass)
            sizePolicy = QtWidgets.QSizePolicy(
                QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
            sizePolicy.setHorizontalStretch(0)
            sizePolicy.setVerticalStretch(0)
            sizePolicy.setHeightForWidth(
                self.labelTitle.sizePolicy().hasHeightForWidth())
            self.labelTitle.setSizePolicy(sizePolicy)
            self.labelTitle.setMinimumSize(QtCore.QSize(400, 80))
            font.setBold(False)
            font.setPointSize(14)
            self.labelTitle.setFont(font)
            self.labelTitle.setAlignment(QtCore.Qt.AlignCenter)
            self.labelTitle.setText(
                f"{self.language['how many character should be your password']}\n\n8")
            self.labelTitle.setObjectName("labelTitle")
            self.labelTitle.setStyleSheet("color:#000;")
            self.gridLayout_4.addWidget(self.labelTitle, 1, 1, 1, 1)
            spacerItem5 = QtWidgets.QSpacerItem(
                20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Preferred)
            self.gridLayout_4.addItem(spacerItem5, 0, 1, 1, 1)
            self.lineEditResult = QtWidgets.QLineEdit(self.frameGenreratePass)
            sizePolicy = QtWidgets.QSizePolicy(
                QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
            sizePolicy.setHorizontalStretch(0)
            sizePolicy.setVerticalStretch(0)
            sizePolicy.setHeightForWidth(
                self.lineEditResult.sizePolicy().hasHeightForWidth())
            self.lineEditResult.setSizePolicy(sizePolicy)
            self.lineEditResult.setMinimumSize(QtCore.QSize(450, 30))
            font.setPointSize(12)
            self.lineEditResult.setFont(font)

            self.lineEditResult.setContextMenuPolicy(
                QtCore.Qt.CustomContextMenu)
            self.lineEditResult.customContextMenuRequested.connect(
                self.contextmenu)

            self.lineEditResult.setStyleSheet(
                "background-color:white;padding:10px;color:#00455c;")
            self.lineEditResult.setText(
                self.language["your password will be display here"])
            self.lineEditResult.setObjectName("lineEditResult")
            self.gridLayout_4.addWidget(self.lineEditResult, 7, 1, 1, 1)
            spacerItem6 = QtWidgets.QSpacerItem(
                20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Preferred)
            self.gridLayout_4.addItem(spacerItem6, 6, 1, 1, 1)
            spacerItem7 = QtWidgets.QSpacerItem(
                40, 20, QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Minimum)
            self.gridLayout_4.addItem(spacerItem7, 8, 2, 1, 1)
            self.frameBtnGenerate = QtWidgets.QFrame(self.frameGenreratePass)
            self.frameBtnGenerate.setFrameShape(QtWidgets.QFrame.StyledPanel)
            self.frameBtnGenerate.setFrameShadow(QtWidgets.QFrame.Raised)
            self.frameBtnGenerate.setObjectName("frameBtnGenerate")

            self.btnGenerate = QtWidgets.QPushButton(self.frameBtnGenerate)
            self.btnGenerate.setGeometry(QtCore.QRect(100, 10, 220, 50))
            font.setPointSize(14)
            self.btnGenerate.setFont(font)
            sizePolicy = QtWidgets.QSizePolicy(
                QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
            sizePolicy.setHorizontalStretch(0)
            sizePolicy.setVerticalStretch(0)
            sizePolicy.setHeightForWidth(
                self.btnGenerate.sizePolicy().hasHeightForWidth())
            self.btnGenerate.setSizePolicy(sizePolicy)
            self.btnGenerate.setText(self.language["generate password"])
            self.btnGenerate.clicked.connect(self.generatePass)
            self.btnGenerate.setStyleSheet(self.otherButtons_style)

            self.btnGenerate.setObjectName("btnGenerate")
            self.gridLayout_4.addWidget(self.frameBtnGenerate, 9, 1, 1, 1)
            self.gridLayout_4.setRowStretch(0, 1)
            self.gridLayout_4.setRowStretch(1, 1)
            self.gridLayout_4.setRowStretch(2, 1)
            self.gridLayout_4.setRowStretch(3, 1)
            self.gridLayout_4.setRowStretch(4, 3)
            self.gridLayout_4.setRowStretch(5, 1)
            self.gridLayout_4.setRowStretch(7, 1)
            self.gridLayout_4.setRowStretch(8, 1)
            self.gridLayout_4.setRowStretch(9, 1)
            self.gridLayout_4.setRowStretch(10, 2)
            if not self.checkForGenPass:
                self.lineEditResult.setEnabled(False)
            else:
                self.lineEditResult.setEnabled(True)
                font.setPointSize(11)
                self.lineEditResult.setFont(font)
                self.lineEditResult.setText(self.lastPassword)
                self.labelTitle.setText(str(self.lastLength))
                self.slider.setValue(self.lastLength)
            self.verticalLayout_6.addWidget(self.frameGenreratePass)
            self.activeButton = self.btnGeneratePassword
            self.changeButtonStyle()

            self.currentFrame = newLayout

    def valuechange(self):
        font = QtGui.QFont()
        font.setPointSize(16)
        font.setFamily("Roboto Mono")
        self.labelTitle.setFont(font)
        self.labelTitle.setText(str(self.slider.value()))
        self.lastLength = self.slider.value()

    def contextmenu(self, position):
        contextMenu = QMenu()
        contextMenu.setStyleSheet(
            "QMenu{padding:5px}QMenu::item::selected{background-color:#838485;color:white;}")

        copy = contextMenu.addAction(self.language["copy"])

        action = contextMenu.exec_(self.lineEditResult.mapToGlobal(position))

        if action == copy:
            QtWidgets.QApplication.clipboard().setText(self.lineEditResult.text())

    def generatePass(self):
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(12)
        self.lineEditResult.setFont(font)
        self.lineEditResult.setEnabled(True)
        finalPassword = ''
        length = self.slider.value()
        password = random.choice(self.digits) + random.choice(self.lowercaseChar) + random.choice(
            self.uperCaserChaer) + random.choice(self.symbols)
        passList = [x for x in list(password)]
        for i in range(length - 4):
            password += random.choice(self.combinded)
            passList = [x for x in list(password)]
            random.shuffle(passList)
        for x in passList:
            finalPassword += x

        self.lineEditResult.setText(finalPassword)
        self.lastPassword = finalPassword
        self.checkForGenPass = True

    def updateItem(self, button):
        name = button.objectName()
        typeOfButton_ID = name.split("-")
        if typeOfButton_ID[0] == "password":
            self.showAddPasswordPage(
                self.frameSideRight, "addPassword", typeOfButton_ID[1])
        elif typeOfButton_ID[0] == "login":
            self.showAddLoginPage(self.frameSideRight,
                                  "addLogin", typeOfButton_ID[1])
        elif typeOfButton_ID[0] == "note":
            self.showAddNotePage(self.frameSideRight,
                                 "addNote", typeOfButton_ID[1])

    def setDefualtBtnStyles(self):
        self.btnStyle = """
                        QPushButton{
                                outline:none;
                                padding-left:20px;
                                text-align:left;
                                border: 0px;
                           }
                        QPushButton::hover {
                            background-color:#002b4a;
                            color:#fff;
                        }
                    """
        self.btnStyle += f"background-color:{self.settings['theme']['bgColorFrameLeftSide']};color:{self.settings['theme']['sidebar-textColor']};"
        # Styling of sidebar button which is active
        self.btnStyleActive = """
                            QPushButton{
                                    outline:none;
                                    padding-left:20px;
                                    text-align:left;
                                    background-color:#002b4a;
                                    color: White;
                                    border: 0px;
                               }
                        """

    def setButtonsText(self):
        self.btnAll_Item.setText(self.language["all items"])
        self.btnPassword.setText(self.language["password"])
        self.btnLogin.setText(self.language["login"])
        self.btnGeneratePassword.setText(self.language["generate password"])
        self.btnNote.setText(self.language["note"])
        self.btnSettings.setText(self.language["settings"])
        self.btnAbout.setText(self.language["about"])

