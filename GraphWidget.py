#Standard Libraries
import math
import numpy as np
from time import time

#Own libraries
from Utility import Utility
from ROIs.PointROI import PointROI
from ROIs.RegionROI import RegionROI
from ROIs.PointROIMinMax import PointROIMinMax
from CustomViewBox import CustomViewBox
from ROIs.AddROI import AddROI

#3rd Party Libraries
import pyqtgraph as pg
from PyQt5 import QtCore as qtc

class GraphWidget(pg.PlotWidget):
	#Slots
	stopPlotting = qtc.pyqtSignal(bool)
	sigRoiMessage = qtc.pyqtSignal(str, int)

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

	AnnotatedGraphs = {
		"s_ecg": False,
		"s_vent": False,
		"s_CO2": False,
	}

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
		self.name = name
		if self.name in self.AnnotatedGraphs:
			super().__init__(useOpenGL=True, viewBox=CustomViewBox(self.name))
			self.getViewBox().sigAddRoiRequest.connect(self._addROI)
		else:
			super().__init__()

		self.pen = pg.mkPen('b')
		self.setBackground('w')
		pg.setConfigOption("foreground", "k")

	def storeData(self, case):
		self.case = case
		self.setLimits(xMax=len(self.case["data"][self.name])+500)
		self.setYRange(np.nanmax(self.case["data"][self.name]), np.nanmin(self.case["data"][self.name]), padding=0.05)
		self.computeIncrements()
		self.plotSlider()
		self.updateAxis()

	def setSpan(self, new_span, viewbox_start):
		#Calculate by what factor the window has been scaled
		self.span = new_span
		self.computeIncrements()
		self.setXRange(viewbox_start, viewbox_start+self.window_length, 0)
		self.plotPosition(viewbox_start)

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

	#DO NOT REMOVE: This is needed to activate the wheelEvent in MW_GraphCollection
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
		self.setYRange(np.nanmax(self.case["data"][self.name]), np.nanmin(self.case["data"][self.name]), padding=0.05)
		self.clear()

		if self.name == "s_ecg":
			self.plot(self.time, self.case["data"][self.name][self.x_start:self.x_end], pen=self.pen)
			self._setAnnotations()
			if self.AnnotatedGraphs[self.name]:
				self._plotQRS()
		elif self.name == "s_vent":
			if self.AnnotatedGraphs[self.name]:
				self._plotVent()
				self.plot(self.time, self.case["data"][self.name][self.x_start:self.x_end], pen=self.pen)
			else:
				self.plot(self.time, self.case["data"]["s_imp"][self.x_start:self.x_end], pen=self.pen)
		elif self.name == "s_CO2":
			if self.AnnotatedGraphs[self.name]:
				self._plotCOPoints()
			self.plot(self.time, self.case["data"][self.name][self.x_start:self.x_end], pen=self.pen)
		else:
			self.plot(self.time, self.case["data"][self.name][self.x_start:self.x_end], pen=self.pen)
		self.updateAxis()	

	def updateAxis(self):
		#Find time given at x=0
		h, m, s = [int(string) for string in self.start_time[1:8].split(":")]
		ms = int(self.start_time[9:11])

		tick_interval = math.floor(self.window_length/5)
		tick_start = math.floor(self.x_start/tick_interval)*tick_interval
		x_ticks = np.arange(tick_start, tick_start+15*tick_interval, tick_interval)

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
				#Show milliseconds when viewbox shows < 2s
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
		sizeX = xyRatios["sizeX"]
		sizeY = xyRatios["sizeY"]
		
		xStart = self.getViewBox().state["viewRange"][0][0]
		xEnd = self.getViewBox().state["viewRange"][0][1]

		for i in range(len(t_qrs)):
			x0 = t_qrs[i][0]*self.frequency
			x1 = t_qrs[i][2]*self.frequency
			xPoint = t_qrs[i][1]*self.frequency
			xPointIndeks = int(np.round(xPoint))
		#If Entry ends after viewRange start and begins before viewRange end
			if x1 >= xStart and x0 <= xEnd:
				self._addRegion(x0, x1, i, "t_qrs", sizeX)
			if xPoint >= xStart and xPoint <= xEnd:
				self._addPoint("s_ecg", "t_qrs", i, xPoint, sizeX, xPointIndeks, sizeY, False, (64, 128, 128))
			if x0 > xEnd:
				break


	def _plotVent(self):
		t_vent = self.case["metadata"]["t_vent"]
		s_vent = self.case["data"]["s_vent"]
		
		xyRatios = Utility.getRangeRatio(self.getViewBox())
		sizeX = xyRatios["sizeX"]
		sizeY = xyRatios["sizeY"]

		xStart = self.getViewBox().state["viewRange"][0][0]
		xEnd = self.getViewBox().state["viewRange"][0][1]

		for i in range(len(t_vent)):
			x0 = t_vent[i][0]*self.frequency #Her trengs ikke int(np.round())
			x1 = t_vent[i][2]*self.frequency
			xPoint = t_vent[i][1]*self.frequency
			xPointIndeks = int(np.round(xPoint))
		#Hvis Entry ender i vårt område eller starter i vårt område
			if x1 >= xStart and x0 <= xEnd:
				self._addRegion(x0, x1, i, "t_vent", sizeX)
			if xPoint >= xStart and xPoint <= xEnd:
				self._addPoint("s_vent", "t_vent", i, xPoint, sizeX, xPointIndeks, sizeY, False, (64, 128, 128))
			if x0 > xEnd:
				break

	def _plotCOPoints(self):
		t_cap = self.case["metadata"]["t_cap"]
		t_CO2 = self.case["metadata"]["t_CO2"] #Tidsforskyvning
		s_CO2 = self.case["data"]["s_CO2"]
		
		xyRatios = Utility.getRangeRatio(self.getViewBox())
		sizeX = xyRatios["sizeX"]
		sizeY = xyRatios["sizeY"]

		xStart = self.getViewBox().state["viewRange"][0][0]
		xEnd = self.getViewBox().state["viewRange"][0][1]

		for i in range(len(t_cap)):
			nMin = (t_cap[i][0] + t_CO2)*self.frequency
			nMinIndeks = int(np.round(nMin))
			#t_min.append(item[0] + t_CO2)
			nMax = (t_cap[i][1] + t_CO2)*self.frequency
			nMaxIndeks = int(np.round(nMax))
			#t_max.append(item[1] + t_CO2)
			if nMin <= xEnd and nMin >= xStart:
				self._addPointMinMax("s_CO2", "t_cap", [i, 0], nMin, sizeX, nMinIndeks, sizeY, True, (255, 0, 0))
			if nMax <= xEnd and nMax >= xStart:
				self._addPointMinMax("s_CO2", "t_cap", [i, 1], nMax, sizeX, nMaxIndeks, sizeY, True, (0, 255, 0))
			if nMax > xEnd:
				break

	def _setAnnotations(self):
		anns = self.case["metadata"]["ann"]
		t_anns = self.case["metadata"]["t_ann"]
		if len(anns) == len(t_anns):
			for i in range(len(t_anns)):
				if t_anns[i]*self.frequency >= self.x_start and t_anns[i]*self.frequency <= self.x_end:
					if i == 0:
						self.addItem(pg.InfiniteLine(pos=t_anns[i]*self.frequency, label=anns[i], pen=pg.mkPen('g', width=2), labelOpts={'color': 'w', 'position': 0.88, 'fill': 'g'}))
					elif i == (len(t_anns)-1):
						self.addItem(pg.InfiniteLine(pos=t_anns[i]*self.frequency, label=anns[i], pen=pg.mkPen('r', width=2), labelOpts={'color': 'w', 'position': 0.88, 'fill': 'r'}))
					else:
						if anns[i] in self.LPcodes_translations:
							label = self.LPcodes_translations[anns[i]]
						else:
							label = anns[i]
						self.addItem(pg.InfiniteLine(pos=t_anns[i]*self.frequency, label=label, pen=pg.mkPen('b', width=2), labelOpts={'color': 'w', 'position': 0.88, 'fill': 'b'}))
		else:
			print("Something went wrong. (The vectors anns and t_anns are not the same length)")

	def _submitQRS(self):
		self.AnnotatedGraphs[self.name] = True
		self.getViewBox().setRoiMenuEnabled(True)

	def _unsubmitQRS(self):
		self.AnnotatedGraphs[self.name] = False
		self.getViewBox().setRoiMenuEnabled(False)

	def _submitVENT(self):
		self.AnnotatedGraphs[self.name] = True
		self.getViewBox().setRoiMenuEnabled(True)

	def _unsubmitVENT(self):
		self.AnnotatedGraphs[self.name] = False
		self.getViewBox().setRoiMenuEnabled(False)

	def _submitCO2(self):
		self.AnnotatedGraphs[self.name] = True
		self.getViewBox().setRoiMenuEnabled(True)

	def _unsubmitCO2(self):
		self.AnnotatedGraphs[self.name] = False
		self.getViewBox().setRoiMenuEnabled(False)

	def _addRegion(self, x0, x1, index, metaSignal, myPointROISizeX):
		mySlice = RegionROI(
			pg.Point(x0, 0), pg.Point(x1, 0), 2*(self.getViewBox().state["viewRange"][1][1] - self.getViewBox().state["viewRange"][1][0]), myPointROISizeX,
			self.case["metadata"][metaSignal], index, self.getViewBox().state["viewRange"],
			pen=(0, 200, 200)
			)
		self.addItem(mySlice)
		self._connectSignals(mySlice, metaSignal, [0, 2])
		
		if self.name in self.AnnotatedGraphs and self.AnnotatedGraphs[self.name] == True:
			mySlice.sigHoverEvent.connect(self._disableRoiMenu)
		

	def _addPoint(self, dataSignal, metaSignal, index, xPoint, sizeX, xPointIndeks, sizeY, isRemovable, penColour):
		myCircle = PointROI(
			self.case["metadata"][metaSignal], index, self.getViewBox().state["viewRange"],
			pg.Point(xPoint - sizeX*.5, self.case["data"][dataSignal][xPointIndeks] - sizeY*.5), (sizeX, sizeY),
			removable=isRemovable, pen=penColour
			)
		self.addItem(myCircle)
		self._connectSignals(myCircle, metaSignal, 1)
	
	def _addPointMinMax(self, dataSignal, metaSignal, index, xPoint, sizeX, xPointIndeks, sizeY, isRemovable, penColour):
		myCircle = PointROIMinMax(
			self.case["metadata"][metaSignal], index, self.getViewBox().state["viewRange"],
			pg.Point(xPoint - sizeX*.5, self.case["data"][dataSignal][xPointIndeks] - sizeY*.5), 
			self.case["metadata"]["t_CO2"]*250,	(sizeX, sizeY),	removable=isRemovable, pen=penColour
			)
		self.addItem(myCircle)
		self._connectSignals(myCircle, metaSignal, index[1])

	def _connectSignals(self, roi, metaSignal, values):
		roi.sigRegionChangeStarted.connect(lambda: self._blockPlotting(True))
		roi.sigRegionChangeFinished.connect(lambda x, y, z: self._ROImoved(x, y, z, metaSignal, values))
		roi.sigHoverEvent.connect(self._blockPlotting)
		roi.sigRemoveRequested.connect(lambda x: self._removeEntry(x, metaSignal))
	
	@qtc.pyqtSlot(int, float, float, str, int)
	def _ROImoved(self, index, pos, size, signal, value):
		msg = "ROI has been moved successfully."
		metaData = self.case["metadata"][signal][index]
		rawData = self.case["data"][self.name]
		try:
			if Utility.isList(value):
				if np.isnan(rawData[int(np.round(pos))]) or np.isnan(rawData[int(np.round(pos+size))]):
					#What's moved? Values are being multiplied/divided by frequency, this might result in inaccuracy.
					#Thus we have to check for biggest movement.
					movement = {
						"leftBorder": metaData[value[0]]*250 - pos,#Positive value: movement to the left.
						"rightBorder": metaData[value[1]]*250 - (pos+size)#Negative value: movement to the right.
					}
					result = Utility.snapRoiIntoValidPosition(movement, metaData, rawData, pos, size)
					msg = "ROI has been snapped back into graph."
					self.case["metadata"][signal][index][result[0]] = result[1]/250
				else:
					self.case["metadata"][signal][index][value[0]] = pos/250  
					self.case["metadata"][signal][index][value[1]] = (pos + size)/250
			else:
				pos += 0.5*size
				if( 
					(value == 0 and np.isnan(rawData[int(np.round(pos))]) or pos < 0.0) or 
					(value == 1 and np.isnan(rawData[int(np.round(pos))]))
				):
					msg = "Cannot move ROI outside the graph."
				#Er dette RegionROI med CircleROI?
				elif self.name in ["s_ecg", "s_vent"] and ((pos)/250 <= metaData[0] or (pos)/250 >= metaData[-1]):
					msg = "Cannot move CircleROI outside its RegionROI."
				#Or is it a MinMaxROI?
				elif self.name in ["s_CO2"]:
					leftBorder = None
					rightBorder = None
					delay = self.case["metadata"]["t_CO2"]
					if value == 0: #Min/left circle.
						rightBorder = metaData[-1]
						rightBorder += delay
						if index == 0:
							leftBorder = 0.0	
						else:
							leftBorder = self.case["metadata"][signal][index - 1][-1]
							leftBorder += delay
					else: #Max/right circle
						leftBorder = metaData[0]
						leftBorder += delay
						if index == len(self.case["metadata"][signal]) - 1:
							rightBorder = len(rawData) - 1
						else:
							rightBorder = self.case["metadata"][signal][index + 1][0]
							rightBorder += delay
					if (pos)/250 < leftBorder or (pos)/250 > rightBorder:
						msg = "Cannot move MinMaxROI past neighbouring points."
					else:
						self.case["metadata"][signal][index][value] = (pos)/250 - delay
				else:
					self.case["metadata"][signal][index][value] = (pos)/250
		except Exception as e:
			msg = str(e)
		finally: 
			self._emitRoiMessage(msg)
			self._blockPlotting(False)
			self.replot()

	@qtc.pyqtSlot(bool)
	def _blockPlotting(self, toBlock):
		#print("Emitting blocking signal." + str(toBlock))
		self.stopPlotting.emit(toBlock)

	@qtc.pyqtSlot(int)
	def _removeEntry(self, index, signal):
		self.case["metadata"][signal] = np.delete(self.case["metadata"][signal], index, 0)
		self._emitRoiMessage("ROI has been removed successfully.")
		self.replot()

	@qtc.pyqtSlot(float)
	def _addROI(self, positionX):
		metaSignal = None
		if self.name == "s_ecg":
			metaSignal = "t_qrs"
		if self.name == "s_vent":
			metaSignal = "t_vent"
		if self.name == "s_CO2":
			metaSignal = "t_cap"
		if metaSignal:
			message = AddROI.addRoi(
				self.name, metaSignal, self.case, positionX, Utility.getRangeRatio(self.getViewBox())["sizeX"], 
				self.getViewBox().state["viewRange"][0], self.getViewBox().boundingRect().width()
				)
			self._emitRoiMessage(message)
			self.replot()

	@qtc.pyqtSlot(bool)
	def _disableRoiMenu(self, disable):
		#print("Sending block menu signal to CustomViewBox")
		self.getViewBox().setRoiMenuEnabled(not disable)
	
	def _emitRoiMessage(self, msg, miliSeconds=5000):
		self.sigRoiMessage.emit(msg, miliSeconds)