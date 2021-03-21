#Standard Libraries
import os
import time

#3rd Party Libraries
from PyQt5 import QtWidgets as qtw
from PyQt5 import QtCore as qtc
from mat4py import loadmat


class DataController(qtw.QWidget):

	DATASET_FILEPATH = None
	SUBSET1 = "1 LP15/MAT"
	SUBSET2 = "2 BCG/MAT"
	CSV = "2 BCG/CSV"

	filenames_submitted = qtc.pyqtSignal(list)
	case_submitted = qtc.pyqtSignal(dict, bool)

	def __init__(self):
		super().__init__()
		print("--- DataController Initialized ---")


	def setDirectory(self, directory_path):
		self.DATASET_FILEPATH = directory_path
		self.filenames_submitted.emit(self.getCaseNames())
		self.getCase()


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
		case["info"] = self.getCaseInfo()

		if filetype == "mat":
			case["data"], index = self.getMatData(new_case_index)
		elif filetype == "csv":
			case["data"], index = self.getCsvData(new_case_index)
		self.case_submitted.emit(case, index)


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

		# #For loop to inspect dict hierarchy
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

		# date = time.ctime(os.path.getmtime(f"{path_LP}/{case_files[0]}"))

		#Send a signal containing the data back to MainApp
		# self.case_data_submitted.emit(data, new_case_index)
		# self.close()
		return data, new_case_index

	def getCsvData(self, new_case_index=False):
		pass

	#Find and return case information from the original CSV case files
	def getCaseInfo(self, new_case_index=False):
		path = f"{self.DATASET_FILEPATH}/{self.CSV}"

		if not new_case_index:
			path = f"{path}/T1V_1.csv"
		else:
			path = f"{path}/T1V_1.csv"

		info = {}
		with open(path) as csv_file:
			csv_info = [next(csv_file) for x in range(9)]

		info["title"] = csv_info[0].replace("#","").replace("\n", "")
		csv_info.pop(0)

		for line in csv_info:
			key = line.split(":", 1)[0].replace("#", "").replace(" ", "_").lower()
			value = line.split(":", 1)[1].replace("\n","")
			info[key] = value
		return info #dict