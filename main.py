import json
import os
import sys
from PyQt5 import QtWidgets
from utils import *
from View.Login import Login
from View.Register import RegWindow

def change_main_window ( window ):
    global MainWindow
    MainWindow = window
    MainWindow.showMaximized()
    MainWindow.txtPassword.setFocus()
    
if __name__ == "__main__":
  
	window = None
	MainWindow = None
	with open("Lang/lang.json") as file:
		loaded_file = json.load(file)
		with open("settings.json") as setting:
			settings = json.load(setting)
			lang = settings["settings"]["language"]
		language = loaded_file["languages"][lang]
	app = QtWidgets.QApplication(sys.argv)
	if os.path.isfile("key.txt"):
		with open("key.txt", "r") as file:
			masterkey = file.read().strip()
			if masterkey == "":
				MainWindowRegister = RegWindow(language,change_main_window)
				MainWindowRegister.showMaximized()
				MainWindowRegister.password.setFocus()
			else:
				MainWindow = Login(language)
				MainWindow.showMaximized()
				MainWindow.txtPassword.setFocus()
	else:
		MainWindowRegister = RegWindow(language, change_main_window)
		MainWindowRegister.showMaximized()
		MainWindowRegister.password.setFocus()

	sys.exit(app.exec_())
