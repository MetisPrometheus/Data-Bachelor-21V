#Standard Libraries
import math
import numpy as np

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

	def __init__(self, name, useOpenGL=True):
		super().__init__()
		self.name = name

		# self.setXRange(10000, 30000, 0.05)
		self.setLimits(xMin=-500)

		# axis = pg.DateAxisItem()
		# self.setAxisItems({"bottom": axis})
		#Fix graphwidget settings
		self.pen = pg.mkPen('b')
		self.setBackground('w')
		#pg.setConfigOption("background", "w")
		pg.setConfigOption("foreground", "k")

	#Event triggered when a plotwidget is focused and a key is pressed
	def keyPressEvent(self, ev):
		#Implement keyboard commands?
		print(ev.key())

	def storeData(self, case):
		self.case = case
		
		self.plotSection()

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
		plotName = self.name
		if plotName == "s_ecg":
			self._plotECG(slider_value)
		elif plotName == "s_CO2":
			self._plotCO2(slider_value)
		elif plotName == "s_ppg":
			 self._plotPPG_SPO2(slider_value)
		elif plotName == "s_imp":
			self._plotTTI(slider_value)
		elif plotName == "s_vent":
			self._plotVent(slider_value)
		elif plotName == "s_bcg1":
			self._plotBCG1(slider_value)
		elif plotName == "s_bcg2":
			self._plotBCG2(slider_value)
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
	#TODO: Sett opp standard grafer slik de er i MatLab og legg felles funksjonalitet i plotSection() eller liknende. Emil.
	#Om det er en graf her som ikke skal være her, så kommenter den ut herfra og resten av koden.
	def _plotECG(self):
		#TODO:YLim må settes for hvert plott.
		self.setYRange(np.nanmax(self.case["data"][self.name]), np.nanmin(self.case["data"][self.name]), padding=0.05)	
		self.plot(self.time, self.case["data"][self.name][self.x_start:self.x_end], pen=self.pen)
		self._setAnnotations(x_start=self.x_start, x_end=self.x_end)
		#TODO: Seb
		self._plotQRS()

	def _plotQRS(self):
		#print("Plotting QRS")
		t_qrs = self.case["metadata"]["t_qrs"]
		only_qrs_points = list()
		i_qrs = list()

		for i in range(len(t_qrs)):
			i_qrs.append(list(t_qrs[i][j] for j in [0, 2]))
			only_qrs_points.append(t_qrs[i][1])

		self.roi = pg.ROI([10, 100], size=50)

		self.addItem(self.roi)
		#Sjekk om lista er tom. Spør hva dette er til.
		if not i_qrs:
			pass
			#TODO legg til NaN eller ignorer.
		else:
			pass
			#Verdt å merke seg at vi her også må bruke handles.s_ecg for signal for y-akse.
			#graphDot(x=t_qrs, y=s_ecg[int(round(t_qrs*handles.fs)+1)])
			#TODO plott inn rektangler ved bruk av i_qrs og sirkler ved bruk av t_qrs
			return only_qrs_points

	def _plotCO2(self):
		#TODO:YLim må settes for hvert plott.
		self.setYRange(np.nanmax(self.case["data"][self.name]), np.nanmin(self.case["data"][self.name]), padding=0.05)
		self.plot(self.time, self.case["data"][self.name][self.x_start:self.x_end], pen=self.pen)
		
	#TODO: Seb
	def _plotCOPoints(self, slider_value):
		#print("Plotting COPoints")
		t_cap = self.case["metadata"]["t_cap"]
		t_CO2 = self.case["metadata"]["t_CO2"]
		n_min = []
		n_max = []
		t_min = []
		t_max = []
		for item in t_cap:
			n_min.append(int(round(item[0]*self.frequency)) + 1)
			t_min.append(item[0] + t_CO2)
			n_max.append(int(round(item[1]*self.frequency)) + 1)
			t_max.append(item[1] + t_CO2)

		#TODO plott inn min og maks punkter på graf.
		#graphDot(x=t_min, y=s_CO2(n_min))
		#graphDot(x=t_max, y=s_CO2(n_max))

	def _plotPPG_SPO2(self):
		#TODO:YLim må settes for hvert plott.
		self.setYRange(np.nanmax(self.case["data"][self.name]), np.nanmin(self.case["data"][self.name]), padding=0.05)
		self.plot(self.time, self.case["data"][self.name][self.x_start:self.x_end], pen=self.pen)

	def _plotTTI(self):
		#TODO:YLim må settes for hvert plott.
		self.setYRange(np.nanmax(self.case["data"][self.name]), np.nanmin(self.case["data"][self.name]), padding=0.05)
		self.plot(self.time, self.case["data"][self.name][self.x_start:self.x_end], pen=self.pen)

	def _plotVent(self):
		#TODO:YLim må settes for hvert plott.
		self.setYRange(np.nanmax(self.case["data"][self.name]), np.nanmin(self.case["data"][self.name]), padding=0.05)
		self.plot(self.time, self.case["data"][self.name][self.x_start:self.x_end], pen=self.pen)
		
		#TODO: Seb
		"""
		#print("Plotting Vent")
		t_vent = self.values["t_vent"]
		i_vent = list()
		for i in range(len(t_vent)):
			i_vent.append(list(t_vent[i][j] for j in [0, 2]))
			i_vent[i] = t_vent[i][1]
		#Sjekk om lista er tom. Spør hva dette er til.
		if not i_vent:
			pass
			#TODO legg til NaN eller ignorer.
		else:
			pass
			#Verdt å merke seg at vi her også må bruke handles.s_vent for signal for y-akse.
			#graphDot(x=t_vent, y=s_vent[int(round(t_vent*handles.fs)+1)])
			#TODO plott inn rektangler ved bruk av i_qrs og sirkler ved bruk av t_qrs
		"""
	def _plotBCG1(self):
		#TODO:YLim må settes for hvert plott.
		self.setYRange(np.nanmax(self.case["data"][self.name]), np.nanmin(self.case["data"][self.name]), padding=0.05)
		self.plot(self.time, self.case["data"][self.name][self.x_start:self.x_end], pen=self.pen)

	def _plotBCG2(self):
		#TODO:YLim må settes for hvert plott.
		self.setYRange(np.nanmax(self.case["data"][self.name]), np.nanmin(self.case["data"][self.name]), padding=0.05)
		self.plot(self.time, self.case["data"][self.name][self.x_start:self.x_end], pen=self.pen)

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
