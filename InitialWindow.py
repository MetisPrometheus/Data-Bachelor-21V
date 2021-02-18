import os
from PyQt5 import QtWidgets as qtw
from PyQt5 import QtCore as qtc

class InitialWindow(qtw.QWidget):

	dataset_path_submitted = qtc.pyqtSignal(str)

	def __init__(self):
		super().__init__()
		self.launch = qtw.QPushButton("Launch", clicked=self.getDirectory)
		self.button = qtw.QPushButton("ChangeDirectory", clicked=self.changeDirectory)

		self.setLayout(qtw.QVBoxLayout())
		self.layout().addWidget(self.launch)
		self.layout().addWidget(self.button)

	def getDirectory(self):
		if "folders.txt" in next(os.walk(os.getcwd()))[2]:
			with open("folders.txt", "r") as f:
				dir_path = f.readlines()[0]
				self.dataset_path_submitted.emit(dir_path)
			pass
		else: 
			with open("folders.txt", "w") as f:
				dir_path = qtw.QFileDialog.getExistingDirectory()
				dir_name = dir_path.split("/")[-1]
				if dir_name == "2 DATASET":
					f.write(dir_path)
					self.dataset_path_submitted.emit(dir_path)
				else:
					print("Incorrect folder chosen") 
		self.close()

	def changeDirectory(self):
		dir_path = qtw.QFileDialog.getExistingDirectory()
		dir_name = dir_path.split("/")[-1]
		if dir_name == "2 DATASET":
			f.write(dir_path)
			self.dataset_path_submitted.emit(dir_path)
		else:
			print("Incorrect folder chosen") 