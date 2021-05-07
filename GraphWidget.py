#Standard Libraries
import math
import numpy as np

#Own libraries
from Utility import Utility
from PointROI import PointROI
from RegionROI import RegionROI
from PointROIMinMax import PointROIMinMax

#3rd Party Libraries
import pyqtgraph as pg
from PyQt5 import QtCore as qtc

class GraphWidget(pg.PlotWidget):
	#Slots
	stopPlotting = qtc.pyqtSignal(bool)

	#Class variables
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
	myCircle = None
	qrs_submitted = False
	vent_submitted = False
	co2_submitted = False

	MAX_X_RANGE = 50000
	MIN_X_RANGE = 100

	LPcodes_translations = {
			'Generic': 'Normal respiration',
			'Oxygen': 'Hyperventlation',
			'IV Access': 'Hold breath',
			'Nitroglycerin': 'Tredelenburg',
			'Morphine': 'Transport to ambulance',
			'Intubation': 'Transport in ambulance',
			'CPR': 'Transport from ambulance',
			'Epinephrine': 'IV fluid (500ml)',
			'Atropine': 'IV fluid stop',
			'Lidocaine': 'Observation'
	}

	def __init__(self, name, useOpenGL=True):
		super().__init__()
		self.name = name

		# self.setXRange(10000, 30000, 0.05)
		self.setLimits(xMin=-500, minXRange=self.MIN_X_RANGE, maxXRange=self.MAX_X_RANGE)

		# axis = pg.DateAxisItem()
		# self.setAxisItems({"bottom": axis})
		#Fix graphwidget settings
		self.pen = pg.mkPen('b')
		self.setBackground('w')
		#pg.setConfigOption("background", "w")
		pg.setConfigOption("foreground", "k")
		if self.qrs_submitted:
			print("qrs has been submitted")

	#Event triggered when a plotwidget is focused and a key is pressed
	# def keyPressEvent(self, ev):
		#Implement keyboard commands?
		# print(ev.key())

	def storeData(self, case):
		self.case = case
		self.setLimits(xMax=len(self.case["data"][self.name])+500)
		self.setYRange(np.nanmax(self.case["data"][self.name]), np.nanmin(self.case["data"][self.name]), padding=0.05)
		self.computeIncrements()
		self.plotSlider()
		self.updateAxis()

	def setSpan(self, new_span, old_slider):
		#Calculate by what factor the window has been scaled
		self.span = new_span
		old_window = self.window_length
		self.computeIncrements()
		factor = old_window/self.window_length

		#Use the factor to roughly decide where the new slider value should be
		new_slider = math.floor(old_slider*factor)
		if new_slider > self.total_increments:
			new_slider = self.total_increments		
		self.plotSlider(new_slider)
		self.updateAxis()

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

	#Do not remove. Is needed for the wheelEvent in MW_GraphCollection to execute
	def wheelEvent(self, ev):
		pass

	def replot(self):
		self.plotPosition(math.floor(self.viewRange()[0][0]))

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
		self.clear()
		data_length = len(self.case["data"][self.name])
		low = math.floor(slider_value/5)
		remainder = slider_value%5	

		#Set the range of the visible part of the graph
		viewbox_start = low*self.window_length + math.floor(remainder*(self.window_length/5))
		viewbox_end = viewbox_start + self.window_length

		if slider_value == self.total_increments:
			viewbox_end = data_length+math.floor(self.window_length/10)
			viewbox_start = viewbox_end - self.window_length
		elif slider_value == 0:
			viewbox_start = -math.floor(self.window_length/10)
			viewbox_end = viewbox_start + self.window_length
		self.setXRange(viewbox_start, viewbox_end, 0)

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
		self.plotSection()

	def plotSection(self, slider_value=0):
		#TODO: Egen funksjon med percentiles og slikt i matlab.
		self.setYRange(np.nanmax(self.case["data"][self.name]), np.nanmin(self.case["data"][self.name]), padding=0.05)
		self.clear()
		#TODO: Når nye checkboxes kommer må ifene bli endret på.
		if self.name == "s_ecg":
			self.plot(self.time, self.case["data"][self.name][self.x_start:self.x_end], pen=self.pen)
			self._setAnnotations()
			if self.qrs_submitted:
				self._plotQRS()
		elif self.name == "s_vent":
			if self.vent_submitted:
				self._plotVent()
				self.plot(self.time, self.case["data"][self.name][self.x_start:self.x_end], pen=self.pen)
			else:
				self.plot(self.time, self.case["data"]["s_imp"][self.x_start:self.x_end], pen=self.pen)
		elif self.name == "s_CO2":
			if self.co2_submitted:
				self._plotCOPoints()
			self.plot(self.time, self.case["data"][self.name][self.x_start:self.x_end], pen=self.pen)
		else:
			self.plot(self.time, self.case["data"][self.name][self.x_start:self.x_end], pen=self.pen)
		self.updateAxis()	

	def updateAxis(self):
		h, m, s = [int(string) for string in self.start_time[1:8].split(":")]
		ms = int(self.start_time[9:11])

		tick_interval = math.floor(self.window_length/5)
		tick_start = math.floor(self.x_start/tick_interval)*tick_interval
		x_ticks = np.arange(tick_start, tick_start+15*tick_interval, tick_interval)
		# x_ticks = np.arange(0, len(self.case["data"][self.name]), tick_interval)

		x_times = []
		for x in x_ticks:
			ms_total = x*4 + ms
			ms_added = ms_total%1000
			s_total = math.floor(ms_total/1000) + s
			s_added = s_total%60
			m_total = math.floor(s_total/60) + m
			m_added = m_total%60
			h_total = math.floor(m_total/60) + h
			h_added = h_total%24

			if h_added < 10:
				h_added = f"0{h_added}"
			if m_added < 10:
				m_added = f"0{m_added}"
			if s_added < 10:
				s_added = f"0{s_added}"
			if ms_added < 10:
				ms_added = f"00{ms_added}"
			elif ms_added < 100:
				ms_added = f"0{ms_added}"

			if tick_interval < 100:
				x_times.append(f"{h_added}:{m_added}:{s_added}.{ms_added}")
			else:
				x_times.append(f"{h_added}:{m_added}:{s_added}")

		ticks = [list(zip(x_ticks, x_times))]
		axis = self.getAxis("bottom")
		axis.setTicks(ticks)

	def _plotQRS(self):
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

		for i in range(len(t_qrs)):
			x0 = t_qrs[i][0]*self.frequency #Her trengs ikke int(np.round())
			x1 = t_qrs[i][2]*self.frequency
			xPoint = t_qrs[i][1]*self.frequency
			xPointIndeks = int(np.round(xPoint))
		#Hvis Entry ender i vårt område eller starter i vårt område
			if x1 >= self.x_start and x0 <= self.x_end:
				self._addRegion(x0, x1, i, "t_qrs", sizeX)
			if xPoint >= self.x_start and xPoint <= self.x_end:
				self._addPoint("s_ecg", "t_qrs", i, xPoint, sizeX, xPointIndeks, sizeY, False, (0, 0, 128))
	
	def _plotVent(self):
		t_vent = self.case["metadata"]["t_vent"]
		s_vent = self.case["data"]["s_vent"]
		
		xyRatios = Utility.getRangeRatio(self.getViewBox())
		sizeX = xyRatios["ratioX"]/np.log10(xyRatios["diff"])
		sizeY = xyRatios["ratioY"]/np.log10(xyRatios["diff"])

		for i in range(len(t_vent)):
			x0 = t_vent[i][0]*self.frequency #Her trengs ikke int(np.round())
			x1 = t_vent[i][2]*self.frequency
			xPoint = t_vent[i][1]*self.frequency
			xPointIndeks = int(np.round(xPoint))
		#Hvis Entry ender i vårt område eller starter i vårt område
			if x1 >= self.x_start and x0 <= self.x_end:
				self._addRegion(x0, x1, i, "t_vent", sizeX)
			if xPoint >= self.x_start and xPoint <= self.x_end:
				self._addPoint("s_vent", "t_vent", i, xPoint, sizeX, xPointIndeks, sizeY, False, (0, 0, 128))

	#TODO: Seb Her blir det tidsforskyvninger. Dette må implementeres bedre når vi får
	#på plass bokser for BCG/CO2 forskyvning osv.
	def _plotCOPoints(self):
		t_cap = self.case["metadata"]["t_cap"]
		t_CO2 = self.case["metadata"]["t_CO2"] #Tidsforskyvning
		s_CO2 = self.case["data"]["s_CO2"]
		
		xyRatios = Utility.getRangeRatio(self.getViewBox())
		sizeX = xyRatios["ratioX"]/np.log10(xyRatios["diff"])
		sizeY = xyRatios["ratioY"]/np.log10(xyRatios["diff"])

		for i in range(len(t_cap)):
			nMin = (t_cap[i][0])*self.frequency
			nMinIndeks = int(np.round(nMin))
			#t_min.append(item[0] + t_CO2)
			nMax = (t_cap[i][1])*self.frequency
			nMaxIndeks = int(np.round(nMax))
			#t_max.append(item[1] + t_CO2)
			if nMin <= self.x_end and nMin >= self.x_start:
				self._addPointMinMax("s_CO2", "t_cap", [i, 0], nMin, sizeX, nMinIndeks, sizeY, True, (255, 0, 0))
			if nMax <= self.x_end and nMax >= self.x_start:
				self._addPointMinMax("s_CO2", "t_cap", [i, 1], nMax, sizeX, nMaxIndeks, sizeY, True, (0, 255, 0))

	def _setAnnotations(self):
		anns = self.case["metadata"]["ann"]
		t_anns = self.case["metadata"]["t_ann"]
		if len(anns) == len(t_anns):
			for i in range(len(t_anns)):
				if t_anns[i]*self.frequency >= self.x_start and t_anns[i]*self.frequency <= self.x_end:
					if i == 0:
						self.addItem(pg.InfiniteLine(pos=t_anns[i]*self.frequency, label=anns[i], pen=pg.mkPen('g', width=2), labelOpts={'color': 'w', 'position': 0.7, 'fill': 'g'}))
					elif i == (len(t_anns)-1):
						self.addItem(pg.InfiniteLine(pos=t_anns[i]*self.frequency, label=anns[i], pen=pg.mkPen('r', width=2), labelOpts={'color': 'w', 'position': 0.7, 'fill': 'r'}))
					else:
						if anns[i] in self.LPcodes_translations:
							label = self.LPcodes_translations[anns[i]]
						else:
							label = anns[i]
						self.addItem(pg.InfiniteLine(pos=t_anns[i]*self.frequency, label=label, pen=pg.mkPen('b', width=2), labelOpts={'color': 'w', 'position': 0.7, 'fill': 'b'}))
		else:
			print("Something went wrong. (The vectors anns and t_anns are not the same length)")

	def _submitQRS(self):
		self.qrs_submitted = True

	def _unsubmitQRS(self):
		self.qrs_submitted = False

	def _submitVENT(self):
		self.vent_submitted = True

	def _unsubmitVENT(self):
		self.vent_submitted = False

	def _submitCO2(self):
		self.co2_submitted = True

	def _unsubmitCO2(self):
		self.co2_submitted = False

	@qtc.pyqtSlot(int, float, float, str, int)
	def _ROImoved(self, index, pos, size, signal, value):
		if Utility.isList(value):
			self.case["metadata"][signal][index][value[0]] = pos/250  
			self.case["metadata"][signal][index][value[1]] = (pos + size)/250
		else:
			self.case["metadata"][signal][index][value] = (pos + 0.5*size)/250
		self._blockPlotting(False)
		self.replot()

	@qtc.pyqtSlot(bool)
	def _blockPlotting(self, toBlock):
		#print("Emitting blocking signal." + str(toBlock))
		self.stopPlotting.emit(toBlock)

	@qtc.pyqtSlot(int)
	def _removeEntry(self, index, signal):
		self.case["metadata"][signal] = np.delete(self.case["metadata"][signal], index, 0)
		self.replot()

	def _addRegion(self, x0, x1, index, metaSignal, myPointROISizeX):
		mySlice = RegionROI(
			pg.Point(x0, 0), pg.Point(x1, 0), 2*(self.getViewBox().state["viewRange"][1][1] - self.getViewBox().state["viewRange"][1][0]), myPointROISizeX,
			self.case["metadata"][metaSignal], index, self.getViewBox().state["viewRange"],
			pen=(0, 200, 200)
			)
		self.addItem(mySlice)
		self._connectSignals(mySlice, metaSignal, [0, 2])

	def _addPoint(self, dataSignal, metaSignal, index, xPoint, sizeX, xPointIndeks, sizeY, isRemovable, penColour):
		myCircle = PointROI(
			self.case["metadata"][metaSignal], index, self.getViewBox().state["viewRange"],
			(xPoint - sizeX*.5, self.case["data"][dataSignal][xPointIndeks] - sizeY*.5), (sizeX, sizeY),
			removable=isRemovable, pen=penColour
			)
		self.addItem(myCircle)
		self._connectSignals(myCircle, metaSignal, 1)
	
	def _addPointMinMax(self, dataSignal, metaSignal, index, xPoint, sizeX, xPointIndeks, sizeY, isRemovable, penColour):
		myCircle = PointROIMinMax(
			self.case["metadata"][metaSignal], index, self.getViewBox().state["viewRange"],
			(xPoint - sizeX*.5, self.case["data"][dataSignal][xPointIndeks] - sizeY*.5), (sizeX, sizeY),
			removable=isRemovable, pen=penColour
			)
		self.addItem(myCircle)
		self._connectSignals(myCircle, metaSignal, index[1])

	def _connectSignals(self, roi, metaSignal, values):
		roi.sigRegionChangeStarted.connect(lambda: self._blockPlotting(True))
		roi.sigRegionChangeFinished.connect(lambda x, y, z: self._ROImoved(x, y, z, metaSignal, values))
		roi.sigHoverEvent.connect(self._blockPlotting)
		roi.sigRemoveRequested.connect(lambda x: self._removeEntry(x, metaSignal))