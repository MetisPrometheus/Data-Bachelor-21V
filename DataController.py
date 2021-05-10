#Standard Libraries
import os
import json
try:
	import cPickle as pickle
except ImportError:
	import pickle

import sys
from time import time

#3rd Party Libraries
from PyQt5 import QtWidgets as qtw
from mat4py import loadmat


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

		ts = time()
		try:
			with open(self.ANNOTATIONS_FILEPATH + self.SUBSET_ANNOTATIONS + "metadata.p", "rb") as fp:
				self.annotationsDataset = pickle.load(fp)
				print("Loaded annotations from pickle.")
		except IOError:
			annotations = loadmat(self.ANNOTATIONS_FILEPATH + self.SUBSET_ANNOTATIONS + "metadata.mat").get("metadata")
			for i in range(len(annotations) - 1):
				key = annotations["reg_name"][i]
				newDict = dict()
				for k in annotations:
					if k == "reg_name":
						continue
					newDict.update({k: annotations[k][i]})
				self.annotationsDataset.update({key: newDict})
				self._prepDataset(self.annotationsDataset[key])
			with open(self.ANNOTATIONS_FILEPATH + self.SUBSET_ANNOTATIONS + "metadata.p", "wb") as fp:
				pickle.dump(self.annotationsDataset, fp, protocol=pickle.HIGHEST_PROTOCOL)
			print("Loaded annotations from .mat and saved pickle file.")
		print("Loading metadata took " + str(time() - ts) + " seconds.")

		#Assigning correct variables to each case from metadata.mat
		
		
		#Make a list of case names from the metadata file and sort them for indexing.
		self.CASE_NAMES = list(self.annotationsDataset.keys())
		self.getCaseNames().sort()
		#print("self.annotationsDataset:", self.annotationsDataset)
		#Explain later
		self.filenames_submitted.emit(self.getCaseNames())

		#Since this is the first case -> new_index = False (default value)
		case = self.getCase()
		


	def getCaseNames(self):
		return self.CASE_NAMES

	def getCase(self, new_case_index=False):
		case = dict()
		self.currentCase = self.getCaseNames()[new_case_index]
		caseName = self.getCaseNames()[new_case_index]
		if not os.path.isdir(self.DATASET_FILEPATH + self.SUBSET_LP15 + "Pickle"):
			os.mkdir(self.DATASET_FILEPATH + self.SUBSET_LP15 + "Pickle")
		if not os.path.isdir(self.DATASET_FILEPATH + self.SUBSET_BCG + "Pickle"):
			os.mkdir(self.DATASET_FILEPATH + self.SUBSET_BCG + "Pickle")

		#LP15
		ts = time()
		try:
			with open(self.DATASET_FILEPATH + self.SUBSET_LP15 + "Pickle/" + caseName + ".p", "rb") as fp:
				datasetLP15 = pickle.load(fp)
				print("LP15 loaded with pickle.")
		except IOError:
			datasetLP15 = loadmat(self.DATASET_FILEPATH + self.SUBSET_LP15 + "MAT/" + caseName + ".mat").get("rec")
			self._prepDataset(datasetLP15)
			with open(self.DATASET_FILEPATH + self.SUBSET_LP15 + "Pickle/" + caseName + ".p", "wb") as fp:
				pickle.dump(datasetLP15, fp, protocol=pickle.HIGHEST_PROTOCOL)
			print("Loaded LP15 from .mat file and converted to pickle.")
		print("Loading LP15 case file took " + str(time() - ts) + " seconds.")

		#BCG
		ts = time()
		try:
			with open(self.DATASET_FILEPATH + self.SUBSET_BCG + "Pickle/" + caseName + ".p", "rb") as fp:
				datasetBCG = pickle.load(fp)
				print("BCG loaded with pickle.")
		except IOError:
			datasetBCG = loadmat(self.DATASET_FILEPATH + self.SUBSET_BCG + "MAT/" + caseName + ".mat").get("rec")
			self._prepDataset(datasetBCG)
			with open(self.DATASET_FILEPATH + self.SUBSET_BCG + "Pickle/" + caseName + ".p", "wb") as fp:
				pickle.dump(datasetBCG, fp, protocol=pickle.HIGHEST_PROTOCOL)
			print("Loaded BCG from .mat file and converted to pickle.")
		print("Loading BCG case file took " + str(time() - ts) + " seconds.")
		ts = time()
		datasetAnnotations = self.annotationsDataset[caseName]

		#Alt dette gjøres tidligere nå.
		#self._prepDataset(datasetLP15)
		#self._prepDataset(datasetBCG)
		#self._prepDataset(datasetAnnotations)

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
	
	def saveMetadata(self, toSave):
		if toSave:
			print("Saving metadata files.")

	def _prepDataset(self, dataset):
		Utility.flattenVector(dataset)
		Utility.array2NumpyArray(dataset)
