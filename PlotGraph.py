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

	def plotSection(self, slider_value=0):
		print(f"slider_value: {slider_value}")
		print(f"datapoints: {len(self.data)}")

		#Find length of data set (Usually 250points per saxec)
		data_length = len(self.data) #(550_000)
		sections = math.ceil(data_length/(self.frequency*self.span))

		#Calculate total slider increments (1 increment will slide the graph by 20%)
		total_increments = sections*5
		self.slider_incs_submitted.emit(total_increments)

		#Amount of datapoints displayed in a graph window
		plot_size = self.frequency*self.span

		low = math.floor(slider_value/5)
		remain = slider_value%5


		y_start = math.floor((low*plot_size) + (remain*(plot_size/5)))
		y_end = y_start + plot_size

		if slider_value > total_increments-5:
			y_start = low*plot_size
			y_end = len(self.data)

		time = list(range(y_start, y_end))
		self.plot(time, self.data[y_start:y_end])