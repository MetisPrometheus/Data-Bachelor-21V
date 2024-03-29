#Standard Libraries
import sys
import math
import json
import numpy as np
import numpy.random as rdn

#3rd Party Libraries
from PyQt5 import QtWidgets as qtw
from PyQt5 import QtCore as qtc
from pyqtgraph.dockarea import *

#Local Classes
from GraphWidget import GraphWidget
from AnnotationsWidget import AnnotationsWidget
from Utility import Utility
# from CustomPlot import CustomPlot

# class MW_GraphCollection(qtw.QMainWindow):
class MW_GraphCollection(qtw.QWidget):
	#Signals
	new_case_index = qtc.pyqtSignal(int)
	slider_incs_submitted = qtc.pyqtSignal(int)
	span_submitted = qtc.pyqtSignal(int)
	sigStatusMessage = qtc.pyqtSignal(str, int)
	
	#Class Variables
	span = 60
	data_length = None
	window_length = None
	settings = {}
	stopPlot = False
	timeline_index = 0

	MAX_X_RANGE = 50000
	MIN_X_RANGE = 100

	def __init__(self):
		super().__init__()
		
		#MIDDLE PART OF GUI (Various Graphs)
		self.dock_area = DockArea()
		self.docks = {}
		self.graphs = {}

		self.body_layout = qtw.QVBoxLayout()
		self.body_layout.addWidget(self.dock_area)

		#BOTTOM PART OF GUI (Slider and Info)
		self.slider = qtw.QSlider(qtc.Qt.Horizontal, valueChanged=self.sliderMoved)
		self.tags = AnnotationsWidget()
		self.tags.setMaximumHeight(30)

		self.bot_layout = qtw.QVBoxLayout()
		self.bot_layout.addWidget(self.tags)
		self.bot_layout.addWidget(self.slider)

		#Wrap a main_layout around the top-, body- and bottom part of the GUI
		self.main_layout = qtw.QVBoxLayout()
		self.main_layout.addLayout(self.body_layout)
		self.main_layout.addLayout(self.bot_layout)
		self.setLayout(self.main_layout)


	def sliderMoved(self, slider_value):
		print(f"MW_GC: slider moved to: {slider_value}")
		for key, graphObj in self.graphs.items():
			graphObj.clear()
			graphObj.plotSlider(slider_value)

	def receiveCheckboxSignal(self, signal, state):
		# print(f"state: {state}, signal: {signal}")
		if state:
			self.docks[signal].show()
			self.graphs[signal].show()
		else:
			self.docks[signal].hide()
			self.graphs[signal].hide()

	def setSlider(self, increments):
		self.slider_max = increments
		self.slider.setMaximum(self.slider_max)

	def receiveNewSpan(self, new_span):
		print(f"changed to new span: {new_span}")
		self.span = new_span

		x_range = self.graphs["s_ecg"].viewRange()[0]
		if x_range[0] < 0:
			x_range[0] = 0

		print(x_range)
		for key, graphObj in self.graphs.items():
			graphObj.setSpan(new_span, math.floor(x_range[0]))

		#Calculate total slider increments with the new window_size
		self.computeIncrements()
		#Use current x-position to set the slider value to the closest increment
		self.updateSliderPosition(x_range[0])

	def setDataLength(self, data_length):
		self.data_length = data_length
		self.computeIncrements()

	#Calculate how many slider increments for a given window_size
	def computeIncrements(self, window_length=0):
		#Calculate window_length based on frequency (250) and timeframe (60)
		frequency = 250
		if window_length == 0:
			self.window_length = frequency*self.span
		else:
			self.window_length = window_length
		complete_sections = math.floor(self.data_length/self.window_length) - 1
		total_increments = complete_sections*5 #Increments will slide graph by 20%

		incomplete_section = ((self.data_length/self.window_length)-(complete_sections+1))*10 #[0-10]
		total_increments += math.ceil(incomplete_section/2)
		self.slider.blockSignals(True)
		self.slider.setMaximum(total_increments)
		self.slider.blockSignals(False)
		return total_increments

	def receiveTimelineXPos(self, xPos):
		viewRange = self.graphs["s_ecg"].viewRange()[0]
		window_length = viewRange[1] - viewRange[0]

		#Set slider to nearest tick from the current position
		inc_step = window_length/5
		nearest_inc = math.floor(xPos/inc_step) - 2
		if nearest_inc < 0: nearest_inc = 0
		self.slider.setValue(nearest_inc)

	def wheelEvent(self, ev):
		zoom = False if ev.angleDelta().y() == 120 else True
		print("mousehweel used")
		#Increase or decrease viewbox by 10%
		x_range = self.graphs["s_ecg"].viewRange()[0]
		skew = math.floor((x_range[1]-x_range[0])*0.05)
		if zoom:
			x_range[0] = x_range[0] - skew
			x_range[1] = x_range[1] + skew
		else:
			x_range[0] = x_range[0] + skew
			x_range[1] = x_range[1] - skew

		#Exit function if new window size would exceed the preset limits
		window_length = math.floor(x_range[1] - x_range[0])
		if window_length > self.MAX_X_RANGE or window_length < self.MIN_X_RANGE:
			return
		self.computeIncrements(window_length) #move to e-82,31?

		print(x_range[1]-x_range[0])
		#Loop through the plotwidgets to update the graphs
		for signal, graphObj in self.graphs.items():
			graphObj.setXRange(x_range[0], x_range[1], 0)
			graphObj.computeIncrements(window_length)
			if x_range[0] < 0:
				x_range[0] = 0
			graphObj.plotPosition(math.floor(x_range[0]))
			graphObj.updateAxis()

		self.updateSliderPosition(x_range[0])

	def eventFilter(self, o, e):
		if not self.stopPlot:
			if e.type() == 3: #3 = MouseRelease
				print("mouse released")
				#print("Mouse released and MW_GraphCollection.py eventFilter() running")
				x_range = self.graphs["s_ecg"].viewRange()[0]
				window_length = math.floor(x_range[1] - x_range[0])
				increments = self.computeIncrements(window_length)

				#Loop through plotwidgets and fill with new case data
				for signal, graphObj in self.graphs.items():
					graphObj.computeIncrements(window_length)
					if x_range[0] < 0:
						x_range[0] = 0
					graphObj.plotPosition(math.floor(x_range[0]))

				self.updateSliderPosition(x_range[0])
			elif e.type() == 82: #82 = Zoom release but event 3 always run before 82
				print("zoom done")
				for signal, graphObj in self.graphs.items():
					graphObj.updateAxis()
			return False
		return False

	def updateSliderPosition(self, xPos):
		#Set slider to nearest tick from the current position
		inc_step = self.window_length/5
		nearest_inc = math.floor(xPos/inc_step)
		print(f"--xpos: {xPos}\n--window size: {self.window_length}\n--inc step: {inc_step}\n--nearest inc: {nearest_inc}\n\n")
		self.slider.blockSignals(True)
		self.slider.setValue(nearest_inc)
		self.slider.blockSignals(False)

	def plotGraphs(self, case):
		self.settings = case["settings"]
		date = case["metadata"]["rec_date"]
		time = case["metadata"]["rec_time"]
		sample_rate = case["data"]["fs"]
		self.case = case
		self.tags._setTags(case)
		#Utility.normalizeSignals(case)
		#Utility.clearPadding(case)

		# Make a new plotwidget for new signals
		for signal in case["data"].keys():
			if signal not in self.graphs.keys() and signal != "fs" and signal != "s_imp":
				#Prepare a dock for the graphs and add it to the dock wrapper
				dock_name = signal.split("_")[-1].upper()
				self.docks[signal] = Dock(f"{dock_name}")
				self.dock_area.addDock(self.docks[signal], "bottom")
				#Move the ecg signal to the top
				if signal == "s_ecg":
					self.dock_area.addDock(self.docks[signal], "top")
				else:
					self.dock_area.addDock(self.docks[signal], "bottom")
				#Make a graph for every signal and assign them to their own docks
				self.graphs[signal] = GraphWidget(signal)
				self.graphs[signal].setLimits(xMin=-500, minXRange=self.MIN_X_RANGE, maxXRange=self.MAX_X_RANGE)
				self.graphs[signal].stopPlotting.connect(self._blockPlotting)
				self.graphs[signal].sigRoiMessage.connect(self._setStatusMessage)
				self.graphs[signal].viewport().installEventFilter(self)
				self.graphs[signal].getAxis("left").setWidth(w=25)
				self.graphs[signal].setMouseEnabled(x=True, y=False)
				self.docks[signal].addWidget(self.graphs[signal])
		
		#Loop through plotwidgets and fill with new case data
		for signal, graphObj in self.graphs.items():
			graphObj.setStartTime(date, time)
			graphObj.setFrequency(sample_rate)
			graphObj.storeData(case)

		#Synchronize all plotwidgets
		for signal, graphObj in self.graphs.items():
				graphObj.setXLink(self.graphs["s_vent"])

		#Re-organize the docks in the order they were in when the program was closed
		if "dockstate" in self.settings.keys():
			self.dock_area.restoreState(self.settings["dockstate"])

		#Hide or show the cases based on saved settings
		for signal in case["settings"]["checkboxes"].keys():
			if case["settings"]["checkboxes"][signal]:
				self.docks[signal].show()
				self.graphs[signal].show()
			else:
				self.docks[signal].hide()
				self.graphs[signal].hide()

		#After plotting new cases set the slider value back to 0
		self.slider.setValue(0)
	
	#Executes when the program is closed and will save the order of the graphs in settings.txt
	def saveDockState(self):
		state = self.dock_area.saveState()
		dock_sizes = state["main"][2]["sizes"]
		state["main"][2]["sizes"] = [100 for element in dock_sizes]
		self.settings["dockstate"] = state
		with open("settings.txt", "w") as f:
			json.dump(self.settings, f)
		print("***The order of the graphs have been saved")

	def toggleOverlay(self, state, data):
		if data == "s_ecg":
			if state:
				self.graphs["s_ecg"]._submitQRS()
			else: 
				self.graphs["s_ecg"]._unsubmitQRS()
		if data == "s_vent":
			if state:
				self.graphs["s_vent"]._submitVENT()
			else: 
				self.graphs["s_vent"]._unsubmitVENT()
		if data == "s_CO2":
			if state:
				self.graphs["s_CO2"]._submitCO2()
			else: 
				self.graphs["s_CO2"]._unsubmitCO2()
		self.graphs[data].plotSection()
	
	@qtc.pyqtSlot(bool)
	def _blockPlotting(self, toBlock):
		self.stopPlot = toBlock

	@qtc.pyqtSlot(str, int)
	def _setStatusMessage(self, msg, miliSeconds):
		self.sigStatusMessage.emit(msg, miliSeconds)

	def refreshTimeline(self, case):
		self.tags._setTags(case)

	def chooseTimeline(self, index):
		if index == 0:
			self.tags._setTags(self.case)
		else:
			self.tags.clear()

	def getGraph(self, graphName):
		if graphName in self.graphs:
			return self.graphs[graphName]

	@qtc.pyqtSlot(float)
	def displaceCO2(self, displacement):
		oldDisplacement = self.case["metadata"]["t_CO2"]
		newDisplacement = displacement - oldDisplacement
		self.case["data"]["s_CO2"], _ = Utility.displaceSignal(self.case["data"]["s_CO2"], newDisplacement, self.case["data"]["fs"])
		self.case["metadata"]["t_CO2"] = displacement
		Utility.equalizeLengthLists(self.case["data"])
		Utility.normalizeSignals(self.case)
		Utility.clearPadding(self.case)
		self.getGraph("s_CO2").replot()

	@qtc.pyqtSlot(int)
	def displaceBCG(self, displacement):
		oldDisplacement = self.case["metadata"]["t_bcg"]
		newDisplacement = displacement - oldDisplacement
		self.case["data"]["s_bcg1"], _ = Utility.displaceSignal(self.case["data"]["s_bcg1"], newDisplacement, self.case["data"]["fs"])
		self.case["data"]["s_bcg2"], _ = Utility.displaceSignal(self.case["data"]["s_bcg2"], newDisplacement, self.case["data"]["fs"])
		self.case["metadata"]["t_bcg"] = displacement
		Utility.equalizeLengthLists(self.case["data"])
		Utility.normalizeSignals(self.case)
		Utility.clearPadding(self.case)
		self.getGraph("s_bcg1").replot()
		self.getGraph("s_bcg2").replot()