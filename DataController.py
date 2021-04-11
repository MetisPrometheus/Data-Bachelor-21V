#Standard Libraries
import os
import time
import json

#3rd Party Libraries
from PyQt5 import QtWidgets as qtw
from PyQt5 import QtCore as qtc
from mat4py import loadmat
import numpy as np

class DataController(qtw.QWidget):
	DATASET_FILEPATH = None
	ANNOTATIONS_FILEPATH = None
	SUBSET1 = "/1 LP15/MAT/"
	SUBSET2 = "/2 BCG/MAT/"
	SUBSET3 = "/1 GUI data/"

	#Loading the metadata.mat file, since it contains all cases.
	ANNOTATIONS_DATASET = dict()
	
	#Based on the casefiles in the metadata.mat structure,  
	#create a sorted list of case names.
	CASE_NAMES = []

	#Initial Case
	filenames_submitted = qtc.pyqtSignal(list)

	#Every Case
	case_submitted = qtc.pyqtSignal(dict)

	settings = {}

	def __init__(self):
		super().__init__()
		print("--- DataController Initialized ---")

	def receiveSettings(self, saved_settings):
		self.settings = saved_settings
		self.DATASET_FILEPATH = self.settings["dataset"]
		self.ANNOTATIONS_FILEPATH = self.settings["annotations"]
		annotations = loadmat(self.ANNOTATIONS_FILEPATH + self.SUBSET3 + "metadata.mat").get("metadata")
		#Sorting the case files in metadata.mat
		for i in range(len(annotations) - 1):
			key = annotations["reg_name"][i]
			newDict = dict()
			for k in annotations:
				if k == "reg_name":
					continue
				newDict.update({k: annotations[k][i]})
			self.ANNOTATIONS_DATASET.update({key: newDict})
		self.CASE_NAMES = list(self.ANNOTATIONS_DATASET.keys())
		self.getCaseNames().sort()
		print(self.getCaseNames())

		#Explain later
		self.filenames_submitted.emit(self.getCaseNames())

		#Since this is the first case -> new_index = False (default value)
		self.getCase()

	def getCaseNames(self):
		return self.CASE_NAMES

	def getCase(self, new_case_index = False):
		dataset = { "new_index": new_case_index }
		if not new_case_index:
			new_case_index = 0
		caseName = self.getCaseNames()[new_case_index]
		#Create a case file containing BCG, LP15 and metadata data.
		dataset.update(loadmat(self.DATASET_FILEPATH + self.SUBSET1 + caseName + ".mat").get("rec"))
		dataset.update(loadmat(self.DATASET_FILEPATH + self.SUBSET2 + caseName + ".mat").get("rec"))
		dataset.update(self.ANNOTATIONS_DATASET[caseName])
	
		#Since MatLab stores some arrays in columns, these 2D-arrays need
		#to be flattened into vectors. All arrays will also be converted
		#to Numpty arrays for faster iteration and manipulation.
		for key, value in dataset.items():
			#print("key =" + str(key) + " & value = " + str(type(value)))
			if type(value) is list and type(value[0]) is list and len(value[0]) is 1:
				dataset[key] = [j for sub in value for j in sub]
			if type(dataset[key]) is list:
				dataset[key] = np.array(dataset[key])

		#TODO: Signals should perhaps be implemented as is in Matlab? Used in MW_Controls.py implicitly stated checkboxes.
		#TODO: Check for new signals? If so, under what conditions and from where?
		plotSignals = [
			"s_ecg",
			"s_CO2",
			"s_ppg",
			"s_imp",
			"s_vent",
			"s_bcg1",
			"s_bcg2"
		]
		self.saveCheckboxStates(plotSignals)

		#Pass along the settings received from 
		dataset["settings"] = self.settings
		
		#Submit the case to the mainwindow for the GUI to be created using the data provided
		self.case_submitted.emit(dataset)

	def saveCheckboxStates(self, checkboxes):
		with open("settings.txt", "w") as f:
			for element in checkboxes:
				#New data signals are added and set to False and will not overwrite previously saved signals
				if element not in self.settings["checkboxes"]:
					self.settings["checkboxes"][element] = False
			#Save the settings to a txt.file in JSON format located in the same directory as the .exe file
			json.dump(self.settings, f)
"""
##	### ###	 ##
#For deletion.# -Sebastian
##	#######  ##
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