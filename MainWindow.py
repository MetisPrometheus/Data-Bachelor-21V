#Standard Libraries
import os
import json

#3rd Party Libraries
from PyQt5 import QtWidgets as qtw
from PyQt5 import QtCore as qtc

#Local Classes
from MW_Controls import MW_Controls
from MW_GraphCollection import MW_GraphCollection

class MainWindow(qtw.QWidget):

	graph_toggle = qtc.pyqtSignal(str, bool)
	slider_incs_submitted = qtc.pyqtSignal(int)
	span_submitted = qtc.pyqtSignal(int)

	def __init__(self):
		super().__init__()
		print("--- Main Window (GUI) Created ---")
		# -------- Main Window Sections --------
		self.MW_Controls = MW_Controls()
		self.MW_GraphCollection = MW_GraphCollection()

		# -------- Signals & Slots -------- 
		#Receive checkbox signal from the controller widget and determine whether to toggle graphs on or off
		self.MW_Controls.checkbox_signal.connect(self.MW_GraphCollection.receiveCheckboxSignal)
		
		#Receive new span and replot the graphs with a bigger or smaller section		
		self.MW_Controls.new_span.connect(self.MW_GraphCollection.receiveNewSpan)

		# -------- Layouts --------
		#Wrap a main_layout around the top-, body- and bottom part of the GUI
		self.main_layout = qtw.QHBoxLayout()
		self.graph_layout = qtw.QVBoxLayout()
		self.left_bar_layout = qtw.QVBoxLayout()
		
		self.checkboxe1 = qtw.QCheckBox("QRS")
		self.checkboxe2 = qtw.QCheckBox("VENT WF")
		self.checkboxe3 = qtw.QCheckBox("CO2 ANNOT")
		self.checkboxe4 = qtw.QCheckBox("TERMINATION")

		self.left_bar_layout.addWidget(self.checkboxes1)
		self.left_bar_layout.addWidget(self.checkboxes2)
		self.left_bar_layout.addWidget(self.checkboxes3)
		self.left_bar_layout.addWidget(self.checkboxes4)
		
		self.main_layout.addLayout(self.left_bar_layout)
		self.main_layout.addLayout(self.graph_layout)
		self.graph_layout.addWidget(self.MW_Controls)
		self.graph_layout.addWidget(self.MW_GraphCollection)
		self.setLayout(self.main_layout)

	#Pass along the filenames to its dropdown-menu in MW_Controls
	def receiveFilenames(self, filenames):
		self.MW_Controls.showCases(filenames)

	#Pass along the timeline-names to its dropdown-menu in MW_Controls
	def receiveTimelines(self, timelines):
		self.MW_Controls.showTimelines(timelines)

	def receiveNewCase(self, case):
		#TODO: Fjern eller så må vi hente ut info i DataController.
		self.MW_Controls.createCheckboxes(case["settings"])
		self.MW_GraphCollection.setDataLength(len(case["data"]["s_ecg"])) #Can use any signal (same length)
		self.MW_GraphCollection.plotGraphs(case)

	def closeEvent(self, argv):
		super().closeEvent(argv)
		print("||| Main Window (GUI) Closed |||")
		self.MW_Controls.saveCheckboxStates()
		self.MW_GraphCollection.saveDockState()
		