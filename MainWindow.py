#3rd Party Libraries
from PyQt5 import QtWidgets as qtw
from PyQt5 import QtCore as qtc

#Local Classes
from PlotGraph import PlotGraph


class MainWindow(qtw.QWidget):

	new_case_index = qtc.pyqtSignal(int)
	graph_toggle = qtc.pyqtSignal(str, bool)
	slider_incs_submitted = qtc.pyqtSignal(int)

	def __init__(self):
		super().__init__()

		#TOP PART OF GUI (Controllers)
		self.dropdown_cases = qtw.QComboBox(currentIndexChanged=self.changeCase)
		self.dropdown_span = qtw.QComboBox(currentTextChanged=self.changeSpan)

		span = ["60s", "30s", "10s", "5s", "2s"]
		self.dropdown_cases.blockSignals(True)
		self.dropdown_span.insertItems(0, span)
		self.dropdown_cases.blockSignals(False)

		self.checkboxes = {}
		self.checkboxes["s_ecg"] = qtw.QCheckBox("ecg", clicked=lambda:self.graphToggler("s_ecg"))
		self.checkboxes["s_CO2"] = qtw.QCheckBox("CO2", clicked=lambda:self.graphToggler("s_CO2"))
		self.checkboxes["s_ppg"] = qtw.QCheckBox("ppg", clicked=lambda:self.graphToggler("s_ppg"))
		self.checkboxes["s_imp"] = qtw.QCheckBox("imp", clicked=lambda:self.graphToggler("s_imp"))
		self.checkboxes["s_vent"] = qtw.QCheckBox("vent", clicked=lambda:self.graphToggler("s_vent"))
		self.checkboxes["s_bcg1"] = qtw.QCheckBox("bcg1", clicked=lambda:self.graphToggler("s_bcg1"))
		self.checkboxes["s_bcg2"] = qtw.QCheckBox("bcg2", clicked=lambda:self.graphToggler("s_bcg2"))

		self.check_layout = qtw.QHBoxLayout()
		self.check_layout.addWidget(self.checkboxes["s_ecg"])
		self.check_layout.addWidget(self.checkboxes["s_CO2"])
		self.check_layout.addWidget(self.checkboxes["s_ppg"])
		self.check_layout.addWidget(self.checkboxes["s_imp"])
		self.check_layout.addWidget(self.checkboxes["s_vent"])
		self.check_layout.addWidget(self.checkboxes["s_bcg1"])
		self.check_layout.addWidget(self.checkboxes["s_bcg2"])

		self.dropdown_layout = qtw.QHBoxLayout()
		self.dropdown_layout.addWidget(self.dropdown_cases)
		self.dropdown_layout.addWidget(self.dropdown_span)

		self.top_layout = qtw.QHBoxLayout()
		self.top_layout.addLayout(self.dropdown_layout)
		self.top_layout.addLayout(self.check_layout)

		#MIDDLE PART OF GUI (Various Graphs)
		self.graphs = {}
		self.body_layout = qtw.QVBoxLayout()

		#BOTTOM PART OF GUI (Slider and Info)
		self.slider = qtw.QSlider(qtc.Qt.Horizontal, valueChanged=self.sliderMoved)
		self.slider.setMinimum(0)
		self.slider.setMaximum(100)

		self.bot_layout = qtw.QHBoxLayout()
		self.bot_layout.addWidget(self.slider)

		#Wrap a main_layout around the top-, body- and bottom part of the GUI
		self.main_layout = qtw.QVBoxLayout()
		self.main_layout.addLayout(self.top_layout)
		self.main_layout.addLayout(self.body_layout)
		self.main_layout.addLayout(self.bot_layout)
		self.setLayout(self.main_layout)

	def setSlider(self, slider_total):
		print("hm")
		self.slider.setMaximum(slider_total)
		self.slidr.setTickInterval(0)

	def changeSpan(self, new_span_value):
		span = int(new_span_value.split("s")[0])
		print(span)

	def sliderMoved(self, slider_value):
		print(slider_value)
		for key, graphObj in self.graphs.items():
			graphObj.clear()
			graphObj.plotSection(slider_value)

	#Populate the dropdown menu with the various patient's case.mat files
	def showCases(self, filepaths):
		self.dropdown_cases.blockSignals(True)
		self.dropdown_cases.insertItems(0, filepaths)
		self.dropdown_cases.blockSignals(False)

	def changeCase(self, new_case_index):
		print(f"changed to new case, index {new_case_index}")
		self.new_case_index.emit(new_case_index)

	def createCheckboxes(self, data):
		# for key in data.keys():ar
		# 	ph = key.split("_")[-1]
		# 	self.checkboxes[key] = qtw.QCheckBox(f"{ph}", clicked=lambda:self.graphToggler(f"{key}"))
		# 	self.check_layout.addWidget(self.checkboxes[key])
		pass

	def graphToggler(self, checkvalue):
		state = self.checkboxes[checkvalue].isChecked()
		self.graph_toggle.emit(checkvalue, state)

	def plotGraphs(self, data, new_case):
		if not new_case:
			for key, value in data.items():
				self.graphs[key] = PlotGraph(value)
				self.graphs[key].slider_incs_submitted.connect(self.setIncrements)

			for key, graphObj in self.graphs.items():
				self.body_layout.addWidget(graphObj)
				self.graphs[key].hide()
		else:
			#Loop through existing graphwidgets and replot with the new data
			for key, graphObj in self.graphs.items():
				graphObj.clear()
				graphObj.plotData(data[key])		

	def setIncrements(self, increments):
		self.slider.setMaximum(increments)

	def showGraph(self, checkvalue, state):
		print(f"type:{checkvalue}, state:{state}")
		if state:
			self.graphs[checkvalue].show()
		else: 
			self.graphs[checkvalue].hide()