#Standard Libraries
import math

#3rd Party Libraries
import pyqtgraph as pg
from PyQt5 import QtCore as qtc

# import vispy.mpl_plot as plt
from vispy import scene


class PlotGraph(pg.PlotWidget):

	data = None
	frequency = 250
	span = 60

	slider_incs_submitted = qtc.pyqtSignal(int)

	def __init__(self, data):
		super().__init__()
		# pg.setConfigOption("background", "w")
		# pg.setConfigOption("foreground", "k")
		self.storeData(data)

	def storeData(self, data):
		self.data = data
		self.plotSection()

	def setSpan(self, span_value):
		self.span = span_value
		self.clear()
		self.plotSection()

	def computeIncrements(self, data):
		pass

	def plotSection(self, slider_value=0):
		print(f"slider_value: {slider_value}")
		print(f"datapoints: {len(self.data)}")

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
		self.plot(time, self.data[y_start:y_end])