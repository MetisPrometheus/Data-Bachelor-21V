#Standard Libraries
import os
import time
import json
import sys
from time import time

#3rd Party Libraries
from PyQt5 import QtWidgets as qtw
from mat4py import loadmat


from PyQt5 import QtCore as qtc

#Own classes.
from Utility import Utility
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
	SUBSET_LP15 = "/1 LP15/MAT/"
	SUBSET_BCG = "/2 BCG/MAT/"
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
		ts = time()
		annotations = loadmat(self.ANNOTATIONS_FILEPATH + self.SUBSET_ANNOTATIONS + "metadata.mat").get("metadata")
		print("Loading metadata.mat file took " + str(time() - ts) + " seconds.")
		#Assigning correct variables to each case from metadata.mat
		for i in range(len(annotations) - 1):
			key = annotations["reg_name"][i]
			newDict = dict()
			for k in annotations:
				if k == "reg_name":
					continue
				newDict.update({k: annotations[k][i]})
			self.annotationsDataset.update({key: newDict})
		
		#Make a list of case names from the metadata file and sort them for indexing.
		self.CASE_NAMES = list(self.annotationsDataset.keys())
		self.getCaseNames().sort()

		#Explain later
		self.filenames_submitted.emit(self.getCaseNames())

		#Since this is the first case -> new_index = False (default value)
		case = self.getCase()
		
	def updateTimelines(self, option, timeline):
		if option == "Add":
			#TODO (Emil/Sebbi)
			'''
			case["annotaitons"][timeline] = {} idk kaslags format det e lagra i men du fatte
			'''

		elif option == "Delete":
			#TODO (Emil/Sebbi)
			'''
			del case["annotations"][timeline]
			'''

		elif option == "Edit":
			#TODO (Emil/Sebbi)
			'''
			eksempel:
			case["annotations"][new_timeline] = case["annotations"][old_timeline]
			del case["annotations"][old_timeline]
			'''

	def getCaseNames(self):
		return self.CASE_NAMES

	def getCase(self, new_case_index=False):
		case = dict()
		caseName = self.getCaseNames()[new_case_index]
		ts = time()
		datasetLP15 = loadmat(self.DATASET_FILEPATH + self.SUBSET_LP15 + caseName + ".mat").get("rec")
		print("Loading LP15 case file took " + str(time() - ts) + " seconds.")
		ts = time()
		datasetBCG = loadmat(self.DATASET_FILEPATH + self.SUBSET_BCG + caseName + ".mat").get("rec")
		print("Loading BCG case file took " + str(time() - ts) + " seconds.")
		ts = time()
		datasetAnnotations = self.annotationsDataset[caseName]

		self._prepDataset(datasetLP15)
		self._prepDataset(datasetBCG)
		self._prepDataset(datasetAnnotations)

		case["data"] = datasetLP15
		case["data"].update(datasetBCG)
		Utility.equalizeLengthLists(case["data"])
		case["metadata"] = datasetAnnotations
		print("Adding metadata to local variable, prepping all datasets and creating case file took " + str(time() - ts) + " seconds.")
		
		#TODO: Denne er vel ikke nødvendig lenger?
		case["new_index"] = new_case_index
		
		#New data signals will be saved to the settings for ease of later plotting
		self.saveCheckboxStates(list(case["data"].keys()))

		#Pass along the settings received from 
		case["settings"] = self.settings
		print("Size of case dictionary is " + str((sys.getsizeof(case) / 2**10)) + "KBs.")
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
	#TODO: Disse kan kanskje legges til en egen statisk utility klasse?
	
	def _prepDataset(self, dataset):
		Utility.flattenVector(dataset)
		Utility.array2NumpyArray(dataset)
		
"""Slett når programmet er ferdig.
	def getMatData(self, new_case_index=False):
		path_LP = f"{self.DATASET_FILEPATH}/{self.SUBSET1}"
		path_BCP = f"{self.DATASET_FILEPATH}/{self.SUBSET2}"
		case_files = self.getCaseNames()	
		
		#Store all the data from the first file or a specified one
		if not new_case_index:
			LP_data = loadmat(f"{path_LP}/{case_files[0]}")
			BCP_data = loadmat(f"{path_BCP}/{case_files[0]}")
			# self.filenames_submitted.emit(case_files) #Emit filenames to MainApp (Used for dropdown menu)
		else: 
			LP_data = loadmat(f"{path_LP}/{case_files[new_case_index]}")
			BCP_data = loadmat(f"{path_BCP}/{case_files[new_case_index]}")

		#Merge both dictionaries
		data = {**LP_data["rec"], **BCP_data["rec"]}

		#For loop to inspect dict hierarchy
		# for key in data.keys():
		# 	if isinstance(data[key], list):
		# 		print("{} - arraylength: {}".format(key, len(data[key])))
		# 	elif type(data[key]) == int:
		# 		print("{} - value: {}".format(key, data[key]))

		#Find the length of the longest list
		max_length = len(data["s_ecg"])
		for key in data.copy().keys():
			if isinstance(data[key], list):
				if (len(data[key]) >= max_length):
					max_length = len(data[key])
			else:
				del data[key] #Remove non-lists from the dictionary

		#Flatten lists from:   [[1], [3], [6], [2]]  --> [1,3,6,2]
		for key, value in data.items():
			data[key] = [item for sublist in value for item in sublist]

		#Extends all lists to equal the longest one (for easier plotting)
		for key, value in data.copy().items():
			length = len(data[key])
			diff = max_length - length
			if diff > 0:
				for i in range(0, diff):
					data[key].append(float('nan'))

		self.saveCheckboxStates(data.keys())
		return data

	def getCsvData(self, new_case_index=False):
		pass

	#Find and return case information from the original CSV case files
	def getCaseInfo(self, new_case_index=False):
		path = f"{self.DATASET_FILEPATH}/{self.CSV}"

		if not new_case_index:
			path = f"{path}/T1V_1.csv"
		else:
			path = f"{path}/T{new_case_index}V_1.csv"

		info = {}
		with open(path) as csv_file:
			csv_info = [next(csv_file) for x in range(9)]

		info["title"] = csv_info[0].replace("#","").replace("\n", "")
		csv_info.pop(0)

		for line in csv_info:
			key = line.split(":", 1)[0].replace("#", "").replace(" ", "_").lower()
			value = line.split(": ", 1)[1].replace("\n","")
			info[key] = value
		return info #dict
"""