#Standard Libraries
import os
import json
import math

#3rd Party Libraries
from PyQt5 import QtWidgets as qtw
from PyQt5 import QtCore as qtc
from PyQt5 import QtGui as qtg


class InitialWindow(qtw.QWidget):

	settings_submitted = qtc.pyqtSignal(dict)

	#Static variables, this is what the dataset folders are expected to be named
	DIRECTORY_NAME_DATASET = "2 DATASET" 
	DIRECTORY_NAME_ANNOTATIONS = "5 ANNOTATIONS"

	def __init__(self):
		super().__init__()
		print("--- Initial Window Created ---")
		self.setWindowTitle(" ")
		self.setObjectName("initialWindow") #For styling

		self.startBtn = qtw.QPushButton("Start", clicked=self.launchGUI, objectName="launchBtn")
		self.startBtn.setFixedHeight(70)
		self.directoryBtn = qtw.QPushButton("Select\nDirectories", clicked=self.requestDirectory, objectName="directoryBtn")
		self.directoryBtn.setFixedHeight(80)

		self.setLayout(qtw.QVBoxLayout())
		self.layout().addWidget(self.startBtn)
		self.layout().addWidget(self.directoryBtn)
		self.initializeWindowSize()

	def initializeWindowSize(self):
			desktop_screen = qtw.QDesktopWidget().screenGeometry(-1)
			screen_width = desktop_screen.width()
			screen_heigth = desktop_screen.height()
			gui_width = 200
			gui_height = 200
			gui_left = math.floor((screen_width-gui_width)/3.3)
			gui_top = math.floor((screen_heigth-gui_height)/3.3)

			#Enter new QRect values
			desktop_screen.setWidth(gui_width)
			desktop_screen.setHeight(gui_height)
			desktop_screen.moveLeft(gui_left)
			desktop_screen.moveTop(gui_top)
			self.setGeometry(desktop_screen)
			self.setFixedSize(self.size())

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