#Standard Libraries
import math
import numpy
from mat4py import loadmat

#3rd Party Libraries
import pyqtgraph as pg
from PyQt5 import QtCore as qtc


class PlotGraph(pg.PlotWidget):

	data = None
	frequency = 250
	span = 60
	slider_incs_submitted = qtc.pyqtSignal(int)
	filepath = "Z:/users/empie/5 ANNOTATIONS/"
	SUBSET_ANNOTATIONS = "1 GUI data/"
	DATASET = loadmat(filepath + SUBSET_ANNOTATIONS + "metadata.mat").get("metadata")

	def __init__(self, data):
		super().__init__()
		self.setBackground('w')
		self.storeData(data)
		

	def storeData(self, data):
		self.data = data
		self.plotSection()

	def setSpan(self, span_value):
		self.span = span_value
		self.clear()
		self.plotSection()

	def getList(self, case, variable):
		caseNumber = self.DATASET["reg_name"].index(case)
		return self.DATASET[variable][caseNumber]

	def getValue(self, case, variable):
		caseNumber = self.DATASET["reg_name"].index(case)
		return self.DATASET[variable][caseNumber]

	def plotCOPoints(self, case):
		t_cap = self.getList(case, "t_cap")
		t_CO2 = self.getValue(case, "t_CO2")
		n_min = []
		n_max = []
		t_min = []
		t_max = []
		for item in t_cap:
			n_min.append(int(round(item[0]*self.frequency)) + 1)
			t_min.append(item[0] + t_CO2)
			n_max.append(int(round(item[1]*self.frequency)) + 1)
			t_max.append(item[1] + t_CO2)
		#TODO plott inn min og maks punkter på graf. For eks: graphDot(x=t_min, y=s_CO2(n_min)), graphDot(x=t_max, y=s_CO2(n_max))


	def plotSection(self, slider_value=0):
		#Calculate window_length based on frequency (250) and timeframe (60)
		data_length = len(self.data) #(~550_000)
		window_length = self.frequency*self.span
		complete_sections = math.floor(data_length/window_length) - 1
		total_increments = complete_sections*5 #Increments will slide graph by 20%

		incomplete_section = ((data_length/window_length)-(complete_sections+1))*10 #[0-10]
		total_increments += math.ceil(incomplete_section/2)  
		self.slider_incs_submitted.emit(total_increments)

		low = math.floor(slider_value/5)
		remainder = slider_value%5

		y_start = low*window_length + math.floor(remainder*(window_length/5))
		y_end = y_start + window_length

		if slider_value == total_increments:
			y_end = len(self.data)
			y_start = y_end - window_length

		time = list(range(y_start, y_end))
		self.plot(self.data)