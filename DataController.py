#Standard Libraries
import os
import json
import sys
from time import time
from datetime import datetime

#3rd Party Libraries
from PyQt5 import QtWidgets as qtw
from PyQt5 import QtCore as qtc

#Own classes.
from Utility import Utility
from MW_GraphCollection import MW_GraphCollection
#####################
#ClassDataController#
#####################
#DataKontrolleren laster inn tre filer: Case_XX.mat fra LP15, BCG og hele metadata.mat filen fra 5 ANNOTATIONS.
#Antall cases og deres navn hentes inn fra metadata.mat og sorteres i ei liste, da denne brukes til indeksering i drop down menyen.
#Alt av data hentet inn fra .mat filene omstruktureres til en vektor (1D array) og omgjøres til numpy arrays, som er raskere og bruker litt mindre plass (se _prepDataSet()).
#Signalene i case["data"] er paddet til lik lengde ved å legge til np.inf på slutten via Utility.equalizeLengthLists(). 
#Dette "rengjøres" så til np.nan (Not a Number) i MW_GraphCollection.py sin _normalizeSignals() funksjon.
#Hele casen struktureres i en dictionary som følger:
#case --
#		data --
#				s_bcg1		(np.array float Vektor)
#				s_bcg2		(np.array float Vektor)
#				s_CO2		(np.array float Vektor)
#				s_ppg		(np.array float Vektor)
#				s_imp		(np.array float Vektor)
#				s_ecg		(np.array float Vektor)
#				s_vent		(np.array float Vektor)
#				fs			(int)
#		metadata --
#				patient_ID	(String)
#				dev_model	(String)
#				rec_date	(String)
#				rec_time	(String)
#				o_reg_name	(String)
#				t_v			(np.array float Vektor)
#				ann			(np.array String Vektor)
#				t_ann		(np.array float Vektor)
#				t_LP15		(np.array float Vektor)
#				EtCO2		(np.array float Vektor)
#				respR		(np.array float Vektor)
#				t_CO2		(float)
#				t_start		(float)
#				t_ref		(float)
#				t_end		(int/float)
#				t_qrs		(np.array float 2D nx3)
#				t_vent		(np.array float 2D nx3)
#				t_cap		(np.array float 2D nx2)
#				t_bcg		(int)
#		new_index 			(bool)
##################
## Seb 13.04.21	##
##################
class DataController(qtw.QWidget):

	DATASET_FILEPATH = None
	ANNOTATIONS_FILEPATH = None
	SUBSET_LP15 = "/1 LP15/"
	SUBSET_BCG = "/2 BCG/"
	SUBSET_ANNOTATIONS = "/1 GUI data/"
	CASE_NAMES = None
	#Load the metadata.mat file into memory, since it contains all the cases.
	annotationsDataset = dict()
	
	#Initial Case
	filenames_submitted = qtc.pyqtSignal(list)

	#Every Case
	case_submitted = qtc.pyqtSignal(dict)

	settings = {}

	def __init__(self):
		super().__init__()
		print("--- DataController Initialized ---")

	#TODO: Legg til metode som kanskje automatisk finner frem til mat filene?
	def receiveSettings(self, saved_settings):
		self.settings = saved_settings
		self.DATASET_FILEPATH = self.settings["dataset"]
		self.ANNOTATIONS_FILEPATH = self.settings["annotations"]

		try:
			if not os.path.isdir(self.ANNOTATIONS_FILEPATH + self.SUBSET_ANNOTATIONS + "Pickle"):
				os.mkdir(self.ANNOTATIONS_FILEPATH + self.SUBSET_ANNOTATIONS + "Pickle")
			if not os.path.isdir(self.DATASET_FILEPATH + self.SUBSET_LP15 + "Pickle"):
				os.mkdir(self.DATASET_FILEPATH + self.SUBSET_LP15 + "Pickle")
			if not os.path.isdir(self.DATASET_FILEPATH + self.SUBSET_BCG + "Pickle"):
				os.mkdir(self.DATASET_FILEPATH + self.SUBSET_BCG + "Pickle")
		except IOError as e:
			print(e)

		ts = time()
		self.annotationsDataset = Utility.convertMatToPickle(self.ANNOTATIONS_FILEPATH, self.SUBSET_ANNOTATIONS, "metadata")
		print("Loading metadata took " + str(time() - ts) + " seconds.")
		
		#Make a list of case names from the metadata file and sort them for indexing.
		self.CASE_NAMES = list(self.annotationsDataset.keys())
		self.getCaseNames().sort()
		#print("self.annotationsDataset:", self.annotationsDataset)
		#Explain later
		self.filenames_submitted.emit(self.getCaseNames())

		#Since this is the first case -> new_index = False (default value)
		case = self.getCase()

	# def updateTimelines(self, option, timeline):
	# 	empty_array = []
	# 	if option == "Add":
	# 		self.case["metadata"].update({timeline: empty_array})
	# 		self.case["metadata"].update({"t_" + timeline: empty_array})
	# 		# self.annotationsDataset[self.currentCase])
	# 	elif option == "Delete":
	# 		if timeline in self.case["metadata"]:
	# 			self.case["metadata"].popitem()
	# 			self.case["metadata"].popitem()
	# 		else:
	# 			print("This timeline does not exist.")
	# 	elif option == "Edit":
	# 		self.case["metadata"].update({timeline: empty_array})
	# 		self.case["metadata"].update({"t_" + timeline: empty_array})

	# 	print(self.case["metadata"])
	# 	self.timeline_submitted.emit(self.case)


	def getCaseNames(self):
		return self.CASE_NAMES

	def getCase(self, new_case_index=False):
		case = dict()
		self.currentCase = self.getCaseNames()[new_case_index]
		caseName = self.getCaseNames()[new_case_index]

		#CaseData
		datasetLP15 = Utility.convertMatToPickle(self.DATASET_FILEPATH, self.SUBSET_LP15, caseName)
		datasetBCG = Utility.convertMatToPickle(self.DATASET_FILEPATH, self.SUBSET_BCG, caseName)
		datasetAnnotations = self.annotationsDataset[caseName]

		case["data"] = datasetLP15
		case["data"].update(datasetBCG)
		case["metadata"] = datasetAnnotations
		case["data"]["s_bcg1"], bcg1Displacement = Utility.displaceSignal(case["data"]["s_bcg1"], case["metadata"]["t_bcg"], case["data"]["fs"])
		case["data"]["s_bcg2"], bcg2Displacement = Utility.displaceSignal(case["data"]["s_bcg2"], case["metadata"]["t_bcg"], case["data"]["fs"])
		case["data"]["s_CO2"], CO2Displacement = Utility.displaceSignal(case["data"]["s_CO2"], case["metadata"]["t_CO2"], case["data"]["fs"])
		Utility.equalizeLengthLists(case["data"])

		#TODO: Denne er vel ikke nødvendig lenger?
		case["new_index"] = new_case_index
		
		#New data signals will be saved to the settings for ease of later plotting
		self.saveCheckboxStates(list(case["data"].keys()))

		#Pass along the settings received from 
		case["settings"] = self.settings
		#Submit the case to the mainwindow for the GUI to be created using the data provided
		self.case_submitted.emit(case)

	def saveCheckboxStates(self, checkboxes):
		with open("settings.txt", "w") as f:
			for element in checkboxes:
				#New data signals are added and set to True and will not overwrite previously saved signals
				#Frequency is not a signal, so do NOT add it to checkboxes.
				if element != "fs" and element != "s_imp" and element not in self.settings["checkboxes"]:
					self.settings["checkboxes"][element] = True
			#Save the settings to a txt.file in JSON format located in the same directory as the .exe file
			json.dump(self.settings, f)
	
	def saveMetadata(self, toSave):
		if toSave:
			Utility.savePickleFile(
				self.ANNOTATIONS_FILEPATH, self.SUBSET_ANNOTATIONS, 
				str(datetime.now()).replace(":", "-").replace(" ", "") + "metadata", self.annotationsDataset
				)