#Standard Libraries
import math
import numpy as np

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

	def __init__(self, useOpenGL=True):
		super().__init__()

		# self.setXRange(10000, 30000, 0.05)
		self.setLimits(xMin=-500)

		# axis = pg.DateAxisItem()
		# self.setAxisItems({"bottom": axis})
		#Fix graphwidget settings

		# pg.setConfigOption("background", "w")
		# pg.setConfigOption("foreground", "k")
		pass

	#Event triggered when a plotwidget is focused and a key is pressed
	def keyPressEvent(self, ev):
		#Implement keyboard commands?
		print(ev.key())

	def storeData(self, values):
		self.values = np.array(values)
		self.setYRange(np.nanmax(values), np.nanmin(values), padding=0.05)
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

		hms, ms = self.start_time.split(".")
		h, m, s = hms.split(":")

			#TODO USE DATETIME AS X AXIS ISNTEAD OF PLAIN NUMBERS
		# print(f"h: {h}, m: {m}, s: {s}, ms: {ms}")

		# time2 = []
		# for x in range(y_start, y_end):
		# 	ms_total = x*4
		# 	ms_added = ms_total%1000
		# 	s_total = math.floor(ms_total/1000)
		# 	s_added = s_total%60
		# 	m_total = math.floor(s_total/60)
		# 	m_added = m_total%60
		# 	h_total = math.floor(m_total/60)
		# 	h_added = h_total%24
		# 	time2.append(f"{h}:{m}:{s}.{ms}")

		# for x in range(y_start, y_end):
		# 	time2.append(time.time())


		# nums = list(range(y_start, y_end))
		# strings = []
		# for x in range(0, len(nums)):
		# 	strings.append("yaaaas")

		# ticks = [list(zip(nums, strings))]

		# xax = self.getAxis("bottom")
		# xax.setTicks(ticks)

		self.plot(time, self.values[y_start:y_end])