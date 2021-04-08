#Standard Libraries
import math

#3rd Party Libraries
import pyqtgraph as pg

# import vispy.mpl_plot as plt
from vispy import scene


class GraphWidget(pg.PlotWidget):

	values = None
	frequency = 250
	start_time = None

	span = 60

	window_length = None
	total_increments = None

	def __init__(self):
		super().__init__()
		#Fix graphwidget settings

		# pg.setConfigOption("background", "w")
		# pg.setConfigOption("foreground", "k")
		pass

	def storeData(self, values):
		self.values = values
		self.plotSection()

	def setSpan(self, new_span):
		self.span = new_span

	def setFrequency(self, sample_rate):
		frequency = int(sample_rate.replace("Hz",""))
		self.frequency = frequency

	def setStartTime(self, date_time):
		date, time = date_time.split(" ", 1)
		print(f"date: {date}, time: {time}")
		self.start_time = time

		

	def computeIncrements(self):
		data_length = len(self.values) #(~550_000)
		#Calculate window_length based on frequency (250) and timeframe (60)
		self.window_length = self.frequency*self.span
		complete_sections = math.floor(data_length/self.window_length) - 1
		self.total_increments = complete_sections*5 #Increments will slide graph by 20%

		incomplete_section = ((data_length/self.window_length)-(complete_sections+1))*10 #[0-10]
		self.total_increments += math.ceil(incomplete_section/2)

	def plotSection(self, slider_value=0):
		self.computeIncrements()
		self.clear()
		low = math.floor(slider_value/5)
		remainder = slider_value%5

		y_start = low*self.window_length + math.floor(remainder*(self.window_length/5))
		y_end = y_start + self.window_length

		if slider_value == self.total_increments:
			y_end = len(self.values)
			y_start = y_end - self.window_length

		time = list(range(y_start, y_end))
		self.plot(time, self.values[y_start:y_end])