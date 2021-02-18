#Standard Libraries
import sys
import os

#3rd Party Libraries
import pyqtgraph as pg
from PyQt5 import QtWidgets as qtw
from PyQt5 import QtCore as qtc
from mat4py import loadmat

#Local Classes
from MainWindow import MainWindow
from InitialWindow import InitialWindow
from DataController import DataController


class MainApp(qtw.QApplication):
	#Main Application Object
	def __init__(self, argv):
		super().__init__(argv)

		# -------- Windows & Objects --------
		#create main window
		self.main_window = MainWindow()

		#create initial window
		self.initial_window = InitialWindow()
		self.initial_window.show()

		#create datacontroller object to return case data upon request
		self.data_controller = DataController()


		# -------- Signals and slots --------
		#Receives the filepath for the dataset and sends it to the datacontroller
		self.initial_window.dataset_path_submitted[str].connect(self.data_controller.setDir)

		#Receives the index for the new patient file chosen and sends it to the datacontroller
		self.main_window.new_case_index[int].connect(self.data_controller.getCaseData)

		#Receives the show/hide state of a checkbox and sends it to the mainwindow
		self.main_window.graph_toggle.connect(self.main_window.showGraph)

		#Receive case data from the controller and pass on to mainwindow
		self.data_controller.case_data_submitted.connect(self.main_window.plotGraphs)
		self.data_controller.case_data_submitted.connect(self.main_window.createCheckboxes)
		self.data_controller.case_data_submitted.connect(self.main_window.show)

		#Receive case filenames and pass on to mainwindow to fill the dropdown menu
		self.data_controller.case_files_submitted.connect(self.main_window.showCases)
		
		self.main_window.slider_incs_submitted.connect(self.main_window.setSlider)

if __name__ == "__main__":
	app = MainApp(sys.argv)	
	sys.exit(app.exec())

