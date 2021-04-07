#3rd Party Libraries
from PyQt5 import QtWidgets as qtw
from PyQt5 import QtCore as qtc

#Local Classes
from PlotGraph import PlotGraph

class MW_GraphCollection(qtw.QWidget):

	slider_incs_submitted = qtc.pyqtSignal(int)
	graph_toggle = qtc.pyqtSignal()

	def __init__(self):
		super().__init__()

		#MIDDLE PART OF GUI (Various Graphs)
		self.graphs = {}
		self.body_layout = qtw.QVBoxLayout()

		#BOTTOM PART OF GUI (Slider and Info)
		self.slider = qtw.QSlider(qtc.Qt.Horizontal, valueChanged=self.sliderMoved)

		self.bot_layout = qtw.QHBoxLayout()
		self.bot_layout.addWidget(self.slider)

		#Wrap a main_layout around the top-, body- and bottom part of the GUI
		self.main_layout = qtw.QVBoxLayout()
		self.main_layout.addLayout(self.body_layout)
		self.main_layout.addLayout(self.bot_layout)
		self.setLayout(self.main_layout)


	def sliderMoved(self, slider_value):
		for key, graphObj in self.graphs.items():
			graphObj.clear()
			graphObj.plotSection(slider_value)

	def setSlider(self, increments):
		self.slider_max = increments
		self.slider.setMaximum(self.slider_max)

	def setIncrements(self, increments):
		self.slider_incs_submitted.emit(increments)

	def plotSpan(self, new_span_value):
		for key, graphObj in self.graphs.items():
			graphObj.setSpan(new_span_value)	

	#case received from mainapp
	def plotGraphs(self, case, new_case_index):
		if not new_case_index:
			for key, value in case["data"].items():
				self.graphs[key] = PlotGraph(value)
				self.graphs[key].slider_incs_submitted.connect(self.setIncrements)
				self.body_layout.addWidget(self.graphs[key])
				self.graphs[key].hide()
		else:
			#Loop through existing graphwidgets and pass in new data
			for key, graphObj in self.graphs.items():
				graphObj.clear()
				graphObj.storeData(case[key])		

	def toggleGraph(self, checkvalue, state):
		if state:
			self.graphs[checkvalue].show()
		else: 
			self.graphs[checkvalue].hide()