#Standard Libraries
import os
import time
import json

#3rd Party Libraries
from PyQt5 import QtWidgets as qtw
from PyQt5 import QtCore as qtc
from mat4py import loadmat


class DataController(qtw.QWidget):

	DATASET_FILEPATH = None
	SUBSET1 = "1 LP15/MAT"
	SUBSET2 = "2 BCG/MAT"
	CSV = "2 BCG/CSV"

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

		#Explain later
		self.filenames_submitted.emit(self.getCaseNames())

		#Since this is the first case -> new_index = False (default value)
		case = self.getCase()


	def getCaseNames(self):
		path_LP = f"{self.DATASET_FILEPATH}/{self.SUBSET1}"
		path_BCP = f"{self.DATASET_FILEPATH}/{self.SUBSET2}"
		_, _, case_files = next(os.walk(path_LP))
		# _, _, casePaths2 = next(os.walk(path_BCP))  #(not needed if you assume LP and BCP files are matching)
		
		#Remove non ("%CASE%".mat) files from the (case_files) list
		case_files[:] = [x for x in case_files if "CASE" in x]
		return case_files

	def getCase(self, new_case_index=False, filetype="mat"):
		case = {}
		#Get case info from the original csv files
		case["info"] = self.getCaseInfo()

		#Get case data from either the mat files or csv files
		if filetype == "mat":
			case["data"] = self.getMatData(new_case_index)
		elif filetype == "csv":
			case["data"] = self.getCsvData(new_case_index)
		case["new_index"] = new_case_index #False if first case

		#New data signals will be saved to the settings for ease of later plotting
		self.saveCheckboxStates(list(case["data"].keys()))

		#Pass along the settings received from 
		case["settings"] = self.settings
		
		#Submit the case to the mainwindow for the GUI to be created using the data provided
		self.case_submitted.emit(case)

	def saveCheckboxStates(self, checkboxes):
		with open("settings.txt", "w") as f:
			for element in checkboxes:
				#New data signals are added and set to False and will not overwrite previously saved signals
				if element not in self.settings["checkboxes"]:
					self.settings["checkboxes"][element] = False
			#Save the settings to a txt.file in JSON format located in the same directory as the .exe file
			json.dump(self.settings, f)

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