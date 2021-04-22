#Standard Libraries
import math
import numpy as np

#Own libraries
from Utility import Utility

#3rd Party Libraries
import pyqtgraph as pg


class GraphWidget(pg.PlotWidget):
	name = None
	values = None
	frequency = 250
	start_time = None

	span = 60

	window_length = None
	total_increments = None

	time = None
	x_start = None
	x_end = None

	def __init__(self, name, useOpenGL=True):
		super().__init__()
		self.name = name

		# self.setXRange(10000, 30000, 0.05)
		self.setLimits(xMin=-500, minXRange=100, maxXRange=50000)

		# axis = pg.DateAxisItem()
		# self.setAxisItems({"bottom": axis})
		#Fix graphwidget settings
		self.pen = pg.mkPen('b')
		self.setBackground('w')
		#pg.setConfigOption("background", "w")
		pg.setConfigOption("foreground", "k")

	#Event triggered when a plotwidget is focused and a key is pressed
	# def keyPressEvent(self, ev):
		#Implement keyboard commands?
		# print(ev.key())

	def storeData(self, case):
		self.case = case
		self.setLimits(xMax=len(self.case["data"][self.name]))
		self.computeIncrements()
		self.plotSlider()

	def setSpan(self, new_span):
		self.span = new_span

	def setFrequency(self, sample_rate):
		self.frequency = sample_rate

	def setStartTime(self, date, time):
		print(f"date: {date}, time: {time}")
		self.start_time = time

	def computeIncrements(self, window_length=0):
		data_length = len(self.case["data"][self.name])
		#Calculate window_length based on frequency (250) and timeframe (60)
		if window_length == 0:
			self.window_length = self.frequency*self.span
		else:
			self.window_length = window_length
		complete_sections = math.floor(data_length/self.window_length) - 1
		self.total_increments = complete_sections*5 #Increments will slide graph by 20%

		incomplete_section = ((data_length/self.window_length)-(complete_sections+1))*10 #[0-10]
		self.total_increments += math.ceil(incomplete_section/2)

	#Plotting graphs after panning/zooming
	def plotPosition(self, viewbox_start):
		self.clear()
		data_length = len(self.case["data"][self.name])
		self.x_start = viewbox_start - self.window_length
		self.x_end = viewbox_start + self.window_length*2

		if self.x_start < 0:
			self.x_start = 0
		elif self.x_end >= data_length:
			self.x_end = data_length
			
		self.time = np.array(list(range(self.x_start, self.x_end)))
		self.plotSection()

	#Plotting graphs after moving the slider
	def plotSlider(self, slider_value=0):
		data_length = len(self.case["data"][self.name])
		low = math.floor(slider_value/5)
		remainder = slider_value%5	

		#Set the range of the visible part of the graph
		viewbox_start = low*self.window_length + math.floor(remainder*(self.window_length/5))
		viewbox_end = viewbox_start + self.window_length

		if slider_value == self.total_increments:
			viewbox_end = data_length
			viewbox_start = viewbox_end - self.window_length
		self.setXRange(viewbox_start, viewbox_end)

		#Set the range of the plotted part of the graph
		self.x_start = viewbox_start - self.window_length
		self.x_end = viewbox_start + self.window_length*2
		if viewbox_start - self.window_length < 0:
			self.x_start = 0
		elif viewbox_start + self.window_length*2 >= data_length:
			self.x_end = data_length

		self.time = list(range(self.x_start, self.x_end))

		hms = self.start_time[1:8]
		miliseconds = self.start_time[9:11]
		h, m, s = hms.split(":")
		print(f"x_start: {self.x_start}, x_end: {self.x_end}")
		self.plotSection()

	def plotSection(self, slider_value=0):
		#TODO: Egen funksjon med percentiles og slikt i matlab.
		self.setYRange(np.nanmax(self.case["data"][self.name]), np.nanmin(self.case["data"][self.name]), padding=0.05)

		#TODO: Når nye checkboxes kommer må ifene bli endret på.
		if self.name == "s_ecg":
			self.plot(self.time, self.case["data"][self.name][self.x_start:self.x_end], pen=self.pen)
			self._plotQRS(self.x_start, self.x_end)
			self._setAnnotations(x_start=self.x_start, x_end=self.x_end)
		elif self.name == "s_vent":
			if True:
				self.plot(self.time, self.case["data"][self.name][self.x_start:self.x_end], pen=self.pen)
				self._plotVent(self.x_start, self.x_end)
			if False:
				self.plot(self.time, self.case["data"]["s_imp"][self.x_start:self.x_end], pen=self.pen)
		elif self.name == "s_CO2":
			self.plot(self.time, self.case["data"][self.name][self.x_start:self.x_end], pen=self.pen)
			self._plotCOPoints(self.x_start, self.x_end)
		else:
			self.plot(self.time, self.case["data"][self.name][self.x_start:self.x_end], pen=self.pen)
				
		"""
		self.computeIncrements()
		self.clear()
		low = math.floor(slider_value/5)
		remainder = slider_value%5

		x_start = low*self.window_length + math.floor(remainder*(self.window_length/5))
		x_end = x_start + self.window_length

		if slider_value == self.total_increments:
			x_end = len(self.case["data"][self.name])
			x_start = x_end - self.window_length

		time = list(range(x_start, x_end))

		hms = self.start_time[1:8]
		miliseconds = self.start_time[9:11]
		h, m, s = hms.split(":")

			#TODO USE DATETIME AS X AXIS ISNTEAD OF PLAIN NUMBERS
		# print(f"h: {h}, m: {m}, s: {s}, ms: {ms}")

		# time2 = []
		# for x in range(x_start, x_end):
		# 	ms_total = x*4
		# 	ms_added = ms_total%1000
		# 	s_total = math.floor(ms_total/1000)
		# 	s_added = s_total%60
		# 	m_total = math.floor(s_total/60)
		# 	m_added = m_total%60
		# 	h_total = math.floor(m_total/60)
		# 	h_added = h_total%24
		# 	time2.append(f"{h}:{m}:{s}.{ms}")

		# for x in range(x_start, x_end):
		# 	time2.append(time.time())


		# nums = list(range(x_start, x_end))
		# strings = []
		# for x in range(0, len(nums)):
		# 	strings.append("yaaaas")

		# ticks = [list(zip(nums, strings))]

		# xax = self.getAxis("bottom")
		# xax.setTicks(ticks)

		self.plot(time, self.case["data"][self.name][x_start:x_end])
		"""
	def _plotQRS(self, x_start, x_end):
		#print("Plotting QRS")
		t_qrs = self.case["metadata"]["t_qrs"]
		s_ecg = self.case["data"]["s_ecg"]
		
		xyRatios = Utility.getRangeRatio(self.getViewBox())
		"""Beregning av størrelser for sirkler.
		print("PLOT QRS")
		print("ViewBox ranges:" + str(self.getViewBox().state["viewRange"]))
		print(
			"Pixels height: " + str(self.getViewBox().boundingRect().height()) + 
			" & Pixels width: " + str(self.getViewBox().boundingRect().width())
			)
		print(str(xyRatios))
		"""
		sizeX = xyRatios["ratioX"]/np.log10(xyRatios["diff"])
		sizeY = xyRatios["ratioY"]/np.log10(xyRatios["diff"])

		for entry in t_qrs:
			x0 = int(np.round(entry[0]*self.frequency) + 1)
			x1 = int(np.round(entry[2]*self.frequency) + 1)
			xPoint = int(np.round(entry[1]*self.frequency))
		#Hvis Entry ender i vårt område eller starter i vårt område
			if x1 >= x_start and x0 <= x_end:
				mySlice = pg.ROI((x0, -10), (x1 - x0, 20), pen=(0, 200, 200))
				self.addItem(mySlice)
			if xPoint >= x_start and xPoint <= x_end:
				myCircle = pg.CircleROI((xPoint - sizeX*.5, s_ecg[xPoint] - sizeY*.5), (sizeX, sizeY), pen=(150, 150, 0))
				self.addItem(myCircle)
	# def _plotCO2(self):
	# 	#TODO:YLim må settes for hvert plott.
	# 	self.setYRange(np.nanmax(self.case["data"][self.name]), np.nanmin(self.case["data"][self.name]), padding=0.05)
	# 	self.plot(self.time, self.case["data"][self.name][self.x_start:self.x_end], pen=self.pen)

	def _plotVent(self, x_start, x_end):
		t_vent = self.case["metadata"]["t_vent"]
		s_vent = self.case["data"]["s_vent"]
		
		xyRatios = Utility.getRangeRatio(self.getViewBox())
		sizeX = xyRatios["ratioX"]/np.log10(xyRatios["diff"])
		sizeY = xyRatios["ratioY"]/np.log10(xyRatios["diff"])

		for entry in t_vent:
			x0 = int(np.round(entry[0]*self.frequency) + 1)
			x1 = int(np.round(entry[2]*self.frequency) + 1)
			xPoint = int(np.round(entry[1]*self.frequency))
		#Hvis Entry ender i vårt område eller starter i vårt område
			if x1 >= x_start and x0 <= x_end:
				mySlice = pg.ROI((x0, -10), (x1 - x0, 20), pen=(0, 200, 200))
				self.addItem(mySlice)
			if xPoint >= x_start and xPoint <= x_end:
				myCircle = pg.CircleROI((xPoint - sizeX*0.5, s_vent[xPoint] - sizeY*.5), (sizeX, sizeY), pen=(150, 150, 0))
				self.addItem(myCircle)

	#TODO: Seb Her blir det tidsforskyvninger. Dette må implementeres bedre når vi får
	#på plass bokser for BCG/CO2 forskyvning osv.
	def _plotCOPoints(self, x_start, x_end):
		#print("Plotting COPoints")
		t_cap = self.case["metadata"]["t_cap"]
		t_CO2 = self.case["metadata"]["t_CO2"] #Tidsforskyvning
		s_CO2 = self.case["data"]["s_CO2"]
		
		xyRatios = Utility.getRangeRatio(self.getViewBox())
		sizeX = xyRatios["ratioX"]/np.log10(xyRatios["diff"])
		sizeY = xyRatios["ratioY"]/np.log10(xyRatios["diff"])

		for item in t_cap:
			nMin = int(round(item[0]*self.frequency) + 1)
			#t_min.append(item[0] + t_CO2)
			nMax = int(round(item[1]*self.frequency) + 1)
			#t_max.append(item[1] + t_CO2)
			if nMin <= x_end and nMin >= x_start:
				myCircle = pg.CircleROI((nMin - sizeX*.5, s_CO2[nMin] - sizeY*.5), (sizeX, sizeY), pen=(255, 0, 0))
				self.addItem(myCircle)
			if nMax <= x_end and nMax >= x_start:
				myCircle = pg.CircleROI((nMax - sizeX*.5, s_CO2[nMax] - sizeY*.5), (sizeX, sizeY), pen=(0, 255, 0))
				self.addItem(myCircle)
		#TODO plott inn min og maks punkter på graf.
		#graphDot(x=t_min, y=s_CO2(n_min))
		#graphDot(x=t_max, y=s_CO2(n_max))

	def _setAnnotations(self, x_start, x_end):
		anns = self.case["metadata"]["ann"]
		t_anns = self.case["metadata"]["t_ann"]
		if len(anns) == len(t_anns):
			for i in range(len(t_anns)):
				if t_anns[i]*self.frequency >= x_start and t_anns[i]*self.frequency <= x_end:
					if i == 0 or i == (len(t_anns)-1): # Make a different marking for the first and last item.
						self.addItem(pg.InfiniteLine(pos=t_anns[i]*self.frequency, label=anns[i], pen=pg.mkPen('g', width=2), labelOpts={'color': 'w', 'position': 0.7, 'fill': 'g'}))
					else:
						self.addItem(pg.InfiniteLine(pos=t_anns[i]*self.frequency, label=anns[i], pen=pg.mkPen('b', width=2), labelOpts={'color': 'w', 'position': 0.7, 'fill': 'b'})) # Muliplying time by frequency just so it matches our time vector. TODO: Divide all time vectors by the frequency
		else:
			print("Something went wrong. (The vectors anns and t_anns are not the same length)")
