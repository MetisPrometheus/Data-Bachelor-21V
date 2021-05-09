#Standard Libraries
import os
import json

#3rd Party Libraries
from PyQt5 import QtWidgets as qtw
from PyQt5 import QtCore as qtc

#Local Classes
from MW_Controls import MW_Controls
from MW_GraphCollection import MW_GraphCollection
from GraphWidget import GraphWidget

class MainWindow(qtw.QWidget):

	graph_toggle = qtc.pyqtSignal(str, bool)
	slider_incs_submitted = qtc.pyqtSignal(int)
	span_submitted = qtc.pyqtSignal(int)
	overlay_submitted = qtc.pyqtSignal(bool, str)

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

		#Receive the x_position from the timeline-bar and replot the graphs from that position
		self.MW_GraphCollection.tags.x_submitted.connect(self.MW_GraphCollection.receiveTimelineXPos)

		# -------- Layouts --------
		#Wrap a main_layout around the top-, body- and bottom part of the GUI
		self.main_layout = qtw.QHBoxLayout()
		self.graph_layout = qtw.QVBoxLayout()
		self.left_bar_layout = qtw.QVBoxLayout()
		
		self.checkbox1 = qtw.QCheckBox("QRS", clicked=lambda:self.emitCheckboxState(self.checkbox1, 's_ecg'))
		self.checkbox2 = qtw.QCheckBox("VENT WF", clicked=lambda:self.emitCheckboxState(self.checkbox2, 's_vent'))
		self.checkbox3 = qtw.QCheckBox("CO2 ANNOT", clicked=lambda:self.emitCheckboxState(self.checkbox3, 's_CO2'))
		#self.checkbox4 = qtw.QCheckBox("TERMINATION", clicked=lambda:self.emitCheckboxState(self.checkbox4, ''))

		self.left_bar_layout.addWidget(self.checkbox1)
		self.left_bar_layout.addWidget(self.checkbox2)
		self.left_bar_layout.addWidget(self.checkbox3)
		#self.left_bar_layout.addWidget(self.checkbox4)
		
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

	def emitCheckboxState(self, signal, data):
		state = signal.isChecked()
		self.overlay_submitted.emit(state, data)
