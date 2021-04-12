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
		self.main_layout = qtw.QVBoxLayout()
		self.main_layout.addWidget(self.MW_Controls)
		self.main_layout.addWidget(self.MW_GraphCollection)
		self.setLayout(self.main_layout)

	#Pass along the received filenames to the controls widget
	def receiveFilenames(self, filenames):
		self.MW_Controls.showCases(filenames)

	def receiveNewCase(self, case):
		for key, value in case["info"].items():
			print(f"infokey: {key} --- infovalue: {value}")

		self.MW_Controls.createCheckboxes(case["settings"])
		self.MW_GraphCollection.setDataLength(len(case["data"]["s_ecg"])) #Can use any signal (same length)
		self.MW_GraphCollection.plotGraphs(case)

	def closeEvent(self, argv):
		super().closeEvent(argv)
		print("||| Main Window (GUI) Closed |||")
		self.MW_Controls.saveCheckboxStates()
		self.MW_GraphCollection.saveDockState()
		