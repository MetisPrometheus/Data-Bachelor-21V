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
	## V1.02 - Seb
	#Legger til navn på graf, slik at denne kan bruke riktig _plotXX.
	## Får egen get() Metode
	name = None

	span = 60

	window_length = None
	total_increments = None

	def __init__(self, name):
		super().__init__()
		self.name = name
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
		frequency = int(sample_rate)
		self.frequency = frequency

	def setStartTime(self, date, time):
		#TODO: Hva er meningen her?
		print(f"date: {date}, time: {time}")
		self.start_time = time

	def getName(self):
		return self.name

	def _getPlotCases(self):
		return self.plotCases

	def computeIncrements(self):
		data_length = len(self.values) #(~550_000)
		#Calculate window_length based on frequency (250) and timeframe (60)
		self.window_length = self.frequency*self.span
		complete_sections = math.floor(data_length/self.window_length) - 1
		self.total_increments = complete_sections*5 #Increments will slide graph by 20%

		incomplete_section = ((data_length/self.window_length)-(complete_sections+1))*10 #[0-10]
		self.total_increments += math.ceil(incomplete_section/2)

	def plotSection(self, slider_value=0):
		#Plottseleksjon.
		#TODO: Kan man kjøre dette via switch case?
		
		plotName = self.getName()
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
		### ########## ###
		#To be deleted...#
		### # ###### # ###
		"""
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
		"""
	#TODO: Felles funksjonalitet må ut av metodene og metodene må selvfølgelig implementeres i forhold til Matlab funksjoner.
	def _plotECG(self, slider_value):
		#print("Plotting EKG")
		self.computeIncrements()
		self.clear()
		low = math.floor(slider_value/5)
		remainder = slider_value%5

		y_start = low*self.window_length + math.floor(remainder*(self.window_length/5))
		y_end = y_start + self.window_length

		if slider_value == self.total_increments:
			y_end = len(self.values["s_ecg"])
			y_start = y_end - self.window_length

		time = list(range(y_start, y_end))
		self.plot(time, self.values["s_ecg"][y_start:y_end])

		self._plotQRS(slider_value)

	def _plotQRS(self, slider_value):
		#print("Plotting QRS")
		t_qrs = self.values["t_qrs"]
		i_qrs = list()
		for i in range(len(t_qrs)):
			i_qrs.append(list(t_qrs[i][j] for j in [0, 2]))
			t_qrs[i] = t_qrs[i][1]
		#Sjekk om lista er tom. Spør hva dette er til.
		if not i_qrs:
			pass
			#TODO legg til NaN eller ignorer.
		else:
			pass
			#Verdt å merke seg at vi her også må bruke handles.s_ecg for signal for y-akse.
			#graphDot(x=t_qrs, y=s_ecg[int(round(t_qrs*handles.fs)+1)])
			#TODO plott inn rektangler ved bruk av i_qrs og sirkler ved bruk av t_qrs

	def _plotTTI(self, slider_value):
		#print("Plotting TTI")
		self.computeIncrements()
		self.clear()
		low = math.floor(slider_value/5)
		remainder = slider_value%5

		y_start = low*self.window_length + math.floor(remainder*(self.window_length/5))
		y_end = y_start + self.window_length

		if slider_value == self.total_increments:
			y_end = len(self.values["s_imp"])
			y_start = y_end - self.window_length

		time = list(range(y_start, y_end))
		self.plot(time, self.values["s_imp"][y_start:y_end])

	def _plotVent(self, slider_value):
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

	def _plotCO2(self, slider_value):
		#print("Plotting CO2")
		self.computeIncrements()
		self.clear()
		low = math.floor(slider_value/5)
		remainder = slider_value%5

		y_start = low*self.window_length + math.floor(remainder*(self.window_length/5))
		y_end = y_start + self.window_length

		if slider_value == self.total_increments:
			y_end = len(self.values["s_CO2"])
			y_start = y_end - self.window_length

		time = list(range(y_start, y_end))
		self.plot(time, self.values["s_CO2"][y_start:y_end])

	def _plotCOPoints(self, slider_value):
		#print("Plotting COPoints")
		t_cap = self.values["t_cap"]
		t_CO2 = self.values["t_CO2"]
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

	def _plotPPG_SPO2(self, slider_value):
		#print("Plotting PPG_SPO2")
		self.computeIncrements()
		self.clear()
		low = math.floor(slider_value/5)
		remainder = slider_value%5

		y_start = low*self.window_length + math.floor(remainder*(self.window_length/5))
		y_end = y_start + self.window_length

		if slider_value == self.total_increments:
			y_end = len(self.values["s_ppg"])
			y_start = y_end - self.window_length

		time = list(range(y_start, y_end))
		self.plot(time, self.values["s_ppg"][y_start:y_end])

	def _plotBCG1(self, slider_value):
		#print("Plotting BCG1")
		self.computeIncrements()
		self.clear()
		low = math.floor(slider_value/5)
		remainder = slider_value%5

		y_start = low*self.window_length + math.floor(remainder*(self.window_length/5))
		y_end = y_start + self.window_length

		if slider_value == self.total_increments:
			y_end = len(self.values["s_bcg1"])
			y_start = y_end - self.window_length

		time = list(range(y_start, y_end))
		self.plot(time, self.values["s_bcg1"][y_start:y_end])

	def _plotBCG2(self, slider_value):
		#print("Plotting BCG2")
		self.computeIncrements()
		self.clear()
		low = math.floor(slider_value/5)
		remainder = slider_value%5

		y_start = low*self.window_length + math.floor(remainder*(self.window_length/5))
		y_end = y_start + self.window_length

		if slider_value == self.total_increments:
			y_end = len(self.values["s_bcg1"])
			y_start = y_end - self.window_length

		time = list(range(y_start, y_end))
		self.plot(time, self.values["s_bcg1"][y_start:y_end])