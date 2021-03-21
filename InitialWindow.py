import os
from PyQt5 import QtWidgets as qtw
from PyQt5 import QtCore as qtc

class InitialWindow(qtw.QWidget):

	directory_submitted = qtc.pyqtSignal(str)

	DIRECTORY_NAME = "2 DATASET" 

	def __init__(self):
		super().__init__()
		self.launch = qtw.QPushButton("Launch", clicked=self.launchGUI)
		self.button = qtw.QPushButton("ChangeDirectory", clicked=self.getDirectory)

		self.setLayout(qtw.QVBoxLayout())
		self.layout().addWidget(self.launch)
		self.layout().addWidget(self.button)

	def launchGUI(self):
		if "settings.txt" in next(os.walk(os.getcwd()))[2]:
			with open("settings.txt", "r") as f:

				#FIX JSON FORMAT

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

				#FIX JSON FORMAT

				f.write(dir_path)
				self.directory_submitted.emit(dir_path)
			else:
				print("Incorrect folder chosen") 