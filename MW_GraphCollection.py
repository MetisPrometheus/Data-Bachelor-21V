#Standard Libraries
import math
import datetime as dt

#3rd Party Libraries
from PyQt5 import QtWidgets as qtw
from PyQt5 import QtCore as qtc

#Local Classes
from GraphWidget import GraphWidget
from OpenGLWidget import OpenGLWidget
from MainGLWidget import MainGLWidget
# from CustomPlot import CustomPlot

import sys
import numpy as np
import numpy.random as rdn

# class MW_GraphCollection(qtw.QMainWindow):
class MW_GraphCollection(qtw.QWidget):

	new_case_index = qtc.pyqtSignal(int)
	slider_incs_submitted = qtc.pyqtSignal(int)
	span_submitted = qtc.pyqtSignal(int)

	old_span = 60
	data_length = None

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
		print(f"slider moved to: {slider_value}")
		for key, graphObj in self.graphs.items():
			graphObj.clear()
			graphObj.plotSection(slider_value)


	def receiveCheckboxSignal(self, signal, state):
		if state:
			self.graphs[signal].show()
		else:
			self.graphs[signal].hide()
	

	def setSlider(self, increments):
		self.slider_max = increments
		self.slider.setMaximum(self.slider_max)


	def receiveNewSpan(self, new_span):
		print(f"changed to new span: {new_span}")
		factor = self.old_span/new_span
		self.old_span = new_span

		old_slide = self.slider.value()
		new_slide = math.floor(old_slide*factor)

		max_increment = self.computeIncrements()
		if new_slide > max_increment:
			new_slide = max_increment

		
		for key, graphObj in self.graphs.items():
			graphObj.setSpan(new_span)

		self.slider.setValue(new_slide)	
		

	def setDataLength(self, data_length):
		self.data_length = data_length
		self.computeIncrements()

	def computeIncrements(self):
		#Calculate window_length based on frequency (250) and timeframe (60)
		frequency = 250
		window_length = frequency*self.old_span
		complete_sections = math.floor(self.data_length/window_length) - 1
		total_increments = complete_sections*5 #Increments will slide graph by 20%

		incomplete_section = ((self.data_length/window_length)-(complete_sections+1))*10 #[0-10]
		total_increments += math.ceil(incomplete_section/2)
		self.slider.setMaximum(total_increments)
		return total_increments
		
	def testWidget(self):
		data = np.array(.2*rdn.randn(100_000, 1),dtype=np.float32)
		test = CustomPlot()

		### Testing QGLWidget added to body_layout ###
		# self.widget1 = OpenGLWidget()
		# self.widget1.set_data(data)
		# self.widget1.setGeometry(100, 100, self.widget1.width, self.widget1.height)
		# self.widget1.show()
		# self.body_layout.addWidget(self.widget1)

		# self.widget2 = OpenGLWidget()
		# self.widget2.set_data(data)
		# self.widget2.setGeometry(100, 100, self.widget2.width, self.widget2.height)
		# self.widget2.show()
		# self.body_layout.addWidget(self.widget2)

		# self.widget3 = OpenGLWidget()
		# self.widget3.set_data(data)
		# self.widget3.setGeometry(100, 100, self.widget3.width, self.widget3.height)
		# self.widget3.show()
		# self.body_layout.addWidget(self.widget3)

		### Testing QGLWidget inside MainWindow widgets ### 
		# self.mainWidget1 = MainGLWidget()
		# self.widget1 = OpenGLWidget()
		# self.widget1.set_data(data)
		# self.widget1.setGeometry(100, 100, self.widget1.width, self.widget1.height)
		# self.mainWidget1.setCentralWidget(self.widget1)
		# self.body_layout.addWidget(self.mainWidget1)

		# self.mainWidget2 = MainGLWidget()
		# self.widget2 = OpenGLWidget()
		# self.widget2.set_data(data)
		# self.widget2.setGeometry(100, 100, self.widget2.width, self.widget2.height)
		# self.mainWidget2.setCentralWidget(self.widget2)
		# self.body_layout.addWidget(self.mainWidget2)

		# self.mainWidget2 = MainGLWidget()
		# self.widget2 = OpenGLWidget()
		# self.widget2.set_data(data)
		# self.widget2.setGeometry(100, 100, self.widget2.width, self.widget2.height)
		# self.mainWidget2.setCentralWidget(self.widget2)
		# self.body_layout.addWidget(self.mainWidget2)

		# self.mainWidget2 = MainGLWidget()
		# self.widget2 = OpenGLWidget()
		# self.widget2.set_data(data)
		# self.widget2.setGeometry(100, 100, self.widget2.width, self.widget2.height)
		# self.mainWidget2.setCentralWidget(self.widget2)
		# self.body_layout.addWidget(self.mainWidget2)
		

	def plotGraphs(self, case):
		date = case["rec_date"]
		time = case["rec_time"]
		sample_rate = case["fs"]
		## V1.02 - Seb
		#Normaliser signaler som i Matlab fra linjer 218ish til 239.
		self._normalizeSignals(case)

		if not case["new_index"]:
			#TODO: Sjekken under blir litt knotete. Her må vi bestemme oss for
			#dynamiske variabler eller fastsatte. Grafene under forutsetter at
			#vi bare mater inn rådata. Dette stemmer ikke og må bli rettet på i V1.02.
			for key in case["settings"]["checkboxes"].keys():
				self.graphs[key] = GraphWidget(key)
				self.graphs[key].setStartTime(date, time)
				self.graphs[key].setFrequency(sample_rate)
				##V1.02 - Seb
				#Sender nå heller inn referanse til hele case som grafens verdier. Dette for å forenkle henting av riktige vektorer for de forskjellige signalene.
				##
				self.graphs[key].storeData(case)
				self.body_layout.addWidget(self.graphs[key])
		else:
			#Loop through existing graphwidgets and pass in new data
			for signal, graphObj in self.graphs.items():
				# graphObj.clear()
				graphObj.setStartTime(date, time)
				graphObj.setFrequency(sample_rate)
				graphObj.storeData(case)

			#If new case contains a signal not previously used, create a new graphwidget for it
			for key in case["settings"]["checkboxes"].keys():
				if key not in self.graphs.keys():
					self.graphs[key] = GraphWidget()
					self.graphs[key].setStartTime(date, time)
					self.graphs[key].setFrequency(sample_rate)
					self.graphs[key].storeData(case[key])
					self.body_layout.addWidget(self.graphs[key])

		#Hide or show the cases based on saved settings
		for signal in case["settings"]["checkboxes"].keys():
			if case["settings"]["checkboxes"][signal]:
				self.graphs[signal].show()
			else:
				self.graphs[signal].hide()

		#After plotting new cases set the slider value back to 0
		self.slider.setValue(0)
		
	def _normalizeSignals(self, case):
		#Denne krever at tiden fortsatt blir oppgitt H:M:S i starten og konverterer til sekunder.
		case["t_ini"] = self._getSeconds(case["rec_time"][0:8])
		#EKG
		#TODO: Ekstra verdier legges inn i dict for TTI og PPG, men dette kan unngås, ved å heller endre opprinnelige signaler.
		s_ecg = case["s_ecg"]
		case["s_ecg"] = np.where((s_ecg > 5) | (s_ecg < -5), 0, s_ecg)
		#TTI: normal and vent
		s_tti = case["s_imp"]
		case["s_tti"] = np.where((np.isnan(s_tti)), 0, s_tti)
		#PPG
		s_ibp = case["s_ppg"]
		case["s_ibp"] = np.where((np.isnan(s_ibp)) | (s_ibp < -10) | (s_ibp > 300), 0, s_ibp)
		#CO2
		s_CO2 = case["s_CO2"]
		case["s_CO2"] = np.where((np.isnan(s_CO2)) | (s_CO2 < -5) | (s_CO2 > 150), 0, s_CO2)
		#T
		case["t"] = np.arange(start=0, stop=len(case["s_ecg"] - 1), step=1)/case["fs"]
		
	#TODO: Move to a utility ->static<- class. Husk å endre denne i self._normalizeSignals()
	def _getSeconds(self, aString):
		aString = aString.split(":")
		seconds = int(aString[0])*3600 + int(aString[1])*60 + int(aString[2])
		return seconds


	def toggleGraph(self, checkvalue, state):
		print(f"type:{checkvalue}, state:{state}")
		if state:
			self.graphs[checkvalue].show()
		else: 
			self.graphs[checkvalue].hide()