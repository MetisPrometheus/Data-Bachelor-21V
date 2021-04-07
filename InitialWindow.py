import os
from PyQt5 import QtWidgets as qtw
from PyQt5 import QtCore as qtc
from PyQt5 import QtGui as qtg

class InitialWindow(qtw.QWidget):

	directory_submitted = qtc.pyqtSignal(str)
	DIRECTORY_NAME = "2 DATASET" 

	def __init__(self):
		super().__init__()
		self.setWindowTitle("Menu")
		self.setFixedSize(300,300)
		self.launch = qtw.QPushButton("Launch", clicked=self.launchGUI)
		self.button = qtw.QPushButton("Change directory", clicked=self.getDirectory)
		self.welcome_text = qtw.QLabel("Welcome to our application. If you are using it for the first time, please change directory to '2 DATASET' folder, then hit launch.")
		self.welcome_text.setWordWrap(True)
		self.setLayout(qtw.QVBoxLayout())
		
		self.layout().addWidget(self.welcome_text)
		self.layout().addWidget(self.launch)
		self.layout().addWidget(self.button)
		
	def launchGUI(self):
		if "settings.txt" in next(os.walk(os.getcwd()))[2]:
			with open("settings.txt", "r") as f:
				dir_path = f.readlines()[0]
				self.directory_submitted.emit(dir_path)
		else: 
			self.getDirectory()
		self.close()

	def getDirectory(self):
		with open("settings.txt", "w") as f:
			dir_path = qtw.QFileDialog.getExistingDirectory()
			dir_name = dir_path.split("/")[-1]
			if dir_name == self.DIRECTORY_NAME:
				f.write(dir_path)
				self.directory_submitted.emit(dir_path)
			else:
				print("Incorrect folder chosen.") 