#Standard Libraries
import os
import json

#3rd Party Libraries
from PyQt5 import QtWidgets as qtw
from PyQt5 import QtCore as qtc



class InitialWindow(qtw.QWidget):

	settings_submitted = qtc.pyqtSignal(dict)

	#Static variable, this is what the dataset folder is expected to be named
	DIRECTORY_NAME = "2 DATASET" 

	def __init__(self):
		super().__init__()
		print("--- Initial Window Created ---")
		self.launch = qtw.QPushButton("Start", clicked=self.launchGUI)
		self.button = qtw.QPushButton("Settings", clicked=self.requestDirectory)

		self.setLayout(qtw.QVBoxLayout())
		self.layout().addWidget(self.launch)
		self.layout().addWidget(self.button)

	def launchGUI(self):
		if "settings.txt" in next(os.walk(os.getcwd()))[2]:
			with open("settings.txt", "r") as json_file:
				#If the file is empty, something is wrong -> default back to asking for a directory
				if os.path.getsize("settings.txt") <= 2:
					self.requestDirectory()
					return
				#JSON
				settings = json.load(json_file)
				#Send settings containing the directory path to the datacontroller
				self.settings_submitted.emit(settings)
		else: 
			self.requestDirectory()
		self.close()

	def requestDirectory(self):
		dataset_path = qtw.QFileDialog.getExistingDirectory()
		directory_name = dataset_path.split("/")[-1]
		if directory_name == self.DIRECTORY_NAME:
			settings = {}
			settings["dataset"] = dataset_path
			settings["annotations"] = "fix dis shit later"
			settings["checkboxes"] = {}
			#Send directory path to the datacontroller
			self.settings_submitted.emit(settings)
		else:
			print("Incorrect folder chosen")
		self.close() 

	def closeEvent(self, argv):
		super().closeEvent(argv)
		print("||| Initial Window Closed |||")