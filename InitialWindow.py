#Standard Libraries
import os
import json

#3rd Party Libraries
from PyQt5 import QtWidgets as qtw
from PyQt5 import QtCore as qtc


class InitialWindow(qtw.QWidget):

	settings_submitted = qtc.pyqtSignal(dict)

	#Static variables, this is what the dataset folders are expected to be named
	DIRECTORY_NAME_DATASET = "2 DATASET" 
	DIRECTORY_NAME_ANNOTATIONS = "5 ANNOTATIONS"

	def __init__(self):
		super().__init__()
		print("--- Initial Window Created ---")
		self.launch = qtw.QPushButton("Start", clicked=self.launchGUI)
		self.button = qtw.QPushButton("Settings", clicked=self.requestDirectory)
		self.setWindowTitle('Initial Window')

		self.setLayout(qtw.QVBoxLayout())
		self.layout().addWidget(self.launch)
		self.layout().addWidget(self.button)

	def launchGUI(self):
		if "settings.txt" in next(os.walk(os.getcwd()))[2]:
			with open("settings.txt", "r") as json_file:
				#If the file is empty, something is wrong -> default back to asking for a directory
				print(os.path.getsize("settings.txt"))
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
		datasetPath = qtw.QFileDialog.getExistingDirectory(self, "Select 2 DATASET folder.")
		datasetName = datasetPath.split("/")[-1] 
		annotationsPath = qtw.QFileDialog.getExistingDirectory(self, "Select 5 ANNOTATIONS folder.")
		annotationsName = annotationsPath.split("/")[-1]
		if (datasetName == self.DIRECTORY_NAME_DATASET and 
			annotationsName == self.DIRECTORY_NAME_ANNOTATIONS):
			settings = {}
			settings["dataset"] = datasetPath
			settings["annotations"] = annotationsPath
			settings["checkboxes"] = {}
			#Send directory path to the datacontroller
			self.settings_submitted.emit(settings)
		else:
			print("Incorrect folder chosen")
		self.close() 

	def closeEvent(self, argv):
		super().closeEvent(argv)
		print("||| Initial Window Closed |||")