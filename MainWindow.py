#Standard Libraries
import os
import json
import math

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

	settings = {}
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

		#Receive statusbar updates
		# self.MW_Controls.test_signal.connect(self.setStatus) #Eksempel

		# -------- Layouts --------
		#Wrap a main_layout around the top-, body- and bottom part of the GUI
		self.main_layout = qtw.QHBoxLayout()
		self.graph_layout = qtw.QVBoxLayout()
		self.left_bar_layout = qtw.QVBoxLayout()

		self.statusBar = qtw.QStatusBar()
		self.statusBar.hide()
		
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
		self.graph_layout.addWidget(self.statusBar)
		self.setLayout(self.main_layout)

	def setStatus(self, message, timer):
		if self.statusBar.currentMessage() == "":
			self.statusBar.show()
			self.statusBar.showMessage(message, timer)

			geometry = self.geometry()
			geometry.setHeight(geometry.height()+26) #statusbar pixelheight = 26
			self.setGeometry(geometry)

			self.timer = qtc.QTimer()
			self.timer.timeout.connect(self.hideBar)
			self.timer.start(timer)

	def hideBar(self):
		self.statusBar.hide()
		geometry = self.geometry()
		geometry.setHeight(geometry.height()-26) #statusbar pixelheight = 26
		self.setGeometry(geometry)
		self.timer.stop()

	#Pass along the filenames to its dropdown-menu in MW_Controls
	def receiveFilenames(self, filenames):
		self.MW_Controls.showCases(filenames)

	#Pass along the timeline-names to its dropdown-menu in MW_Controls
	def receiveTimelines(self, timelines):
		self.MW_Controls.showTimelines(timelines)

	def receiveNewCase(self, case):
		#TODO: Fjern eller så må vi hente ut info i DataController.
		self.initializeWindowSize(case["settings"])
		self.MW_Controls.createCheckboxes(case["settings"])
		self.MW_GraphCollection.setDataLength(len(case["data"]["s_ecg"])) #Can use any signal (all same length)
		self.MW_GraphCollection.plotGraphs(case)

	def initializeWindowSize(self, saved_settings):
		self.settings = saved_settings
		if "gui_box" in self.settings.keys():
			saved_box = self.settings["gui_box"]
			current_box = self.geometry()
			current_box.setRect(saved_box[0], saved_box[1], saved_box[2], saved_box[3])
			self.setGeometry(current_box)
		else:
			desktop_screen = qtw.QDesktopWidget().screenGeometry(-1)
			screen_width = desktop_screen.width()
			screen_heigth = desktop_screen.height()
			gui_width = math.floor(screen_width*0.75)
			gui_height = math.floor(screen_heigth*0.75)
			gui_left = math.floor((screen_width-gui_width)/2)
			gui_top = math.floor((screen_heigth-gui_height)/2)

			#Enter new QRect values
			desktop_screen.setWidth(gui_width)
			desktop_screen.setHeight(gui_height)
			desktop_screen.moveLeft(gui_left)
			desktop_screen.moveTop(gui_top)
			self.setGeometry(desktop_screen)

	def closeEvent(self, argv):
		super().closeEvent(argv)
		print("||| Main Window (GUI) Closed |||")
		self.MW_Controls.saveCheckboxStates()
		self.MW_GraphCollection.saveDockState()
		self.saveWindowSize()

	def saveWindowSize(self):
		print("**The gui size and position have been saved**")
		self.settings["gui_box"] = self.geometry().getRect()
		with open("settings.txt", "w") as f:
			json.dump(self.settings, f)

	def emitCheckboxState(self, signal, data):
		state = signal.isChecked()
		self.overlay_submitted.emit(state, data)
