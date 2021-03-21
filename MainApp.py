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

		# -------- Windows & Controllers --------
		#create main window
		self.main_window = MainWindow()

		#create initial window
		self.initial_window = InitialWindow()
		self.initial_window.show()

		#create datacontroller object to return case data upon request
		self.data_controller = DataController()


		# -------- Signals & Slots --------
		#Receive filepath from initial window and send it to the datacontroller
		self.initial_window.directory_submitted[str].connect(self.data_controller.setDirectory)

		#Receive case data from the controller and pass on to mainwindow
		self.data_controller.case_submitted.connect(self.main_window.receiveNewCase)
		self.data_controller.case_submitted.connect(self.main_window.show)

		#Receive case filenames and pass on to mainwindow to fill the dropdown menu
		self.data_controller.filenames_submitted.connect(self.main_window.receiveFilenames)

		#Receives the index for the new patient file chosen and sends it to the datacontroller
		self.main_window.MW_Controls.new_case_index[int].connect(self.data_controller.getCase)

		#Receives the show/hide state of a checkbox and sends it to the mainwindow
		self.main_window.MW_Controls.checkbox_state.connect(self.main_window.MW_GraphCollection.toggleGraph)

		# self.main_window.slider_incs_submitted.connect(self.main_window.setSlider)
		# self.main_window.span_submitted.connect(self.main_window.plotSpan)


if __name__ == "__main__":
	app = MainApp(sys.argv)	
	sys.exit(app.exec())

