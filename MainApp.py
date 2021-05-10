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
from TimelineSettings import TimelineSettings
from GraphWidget import GraphWidget

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

		#create window for adding/deleting timelines
		self.timeline_window = TimelineSettings()

		#create datacontroller object to return case data upon request
		self.data_controller = DataController()

		# -------- Signals & Slots --------
		#Receive filepath from initial window and send it to the datacontroller
		self.initial_window.settings_submitted[dict].connect(self.data_controller.receiveSettings)

		#Receive case filenames and pass on to mainwindow to fill the dropdown menu
		self.data_controller.filenames_submitted.connect(self.main_window.receiveFilenames)

		#Receive the case dict from the controller and pass on to mainwindow for the GUI creation/update
		self.data_controller.case_submitted.connect(self.main_window.receiveNewCase)
		self.data_controller.case_submitted.connect(self.main_window.show)

		#Receives the index for the new patient file chosen and sends it to the datacontroller
		self.main_window.MW_Controls.new_case_index[int].connect(self.data_controller.getCase)

		#When the application is closed, save the checkstates of the checkboxes in settings.txt
		self.main_window.MW_Controls.checkbox_dict.connect(self.data_controller.saveCheckboxStates)
		self.main_window.sigSaveMetadata.connect(self.data_controller.saveMetadata)
		
		self.main_window.MW_Controls.overlay_submitted.connect(self.main_window.MW_GraphCollection.toggleOverlay)
		# self.main_window.overlay_submitted.connect(self.main_window.MW_GraphCollection.toggleOverlay)
		

		#Timeline stuff

		''' (Emil/Sebbi)
		# TODO: Get timeline names from datacontroller to populate the dropdown menu
		self.data_controller.timelines_submitted.connect(self.main_window.receiveTimelines)
		'''
		#This signal is caught from MW_Controls when Add/Delete/Edit has been clicked
		self.main_window.MW_Controls.request_timeline_window.connect(self.timeline_window.openWindow)
		#self.main_window.MW_Controls.timeline_changed.connect(self.data_controller.updateTimeline)
		self.data_controller.timeline_submitted.connect(self.main_window.MW_GraphCollection.refreshTimeline)




		#Send a signal from the timeline window back to MW_Controls to update the dropdown menu
		self.timeline_window.timeline_submitted.connect(self.main_window.MW_Controls.updateTimelines)
		''' (Emil/Sebbi)
		#TODO: Send parameters ("Add", "Delete", "Edit") & (timeline_name) back to the datacontroller to update the saved timelines
		self.timeline_window.timeline_submitted.connect(self.data_controller.updateTimelines)
		'''
 

if __name__ == "__main__":
	app = MainApp(sys.argv)	
	sys.exit(app.exec())