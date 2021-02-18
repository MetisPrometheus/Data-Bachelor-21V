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

	case_data_submitted = qtc.pyqtSignal(dict, bool)
	case_files_submitted = qtc.pyqtSignal(list)

	def __init__(self):
		super().__init__()
		print("DataController Initialized")

	def setDir(self, dirPath):
		if dirPath is not None:
			self.DATASET_FILEPATH = dirPath
			self.getCaseData(False)
		else:
			pass

	def getCaseData(self, new_case_index=False):
		path_LP = f"{self.DATASET_FILEPATH}/{self.SUBSET1}"
		path_BCP = f"{self.DATASET_FILEPATH}/{self.SUBSET2}"
		_, _, case_files = next(os.walk(path_LP))
		# _, _, casePaths2 = next(os.walk(path_BCP))  (No need if you assume LP and BCP files match)

		#Remove non (case.mat) files from the (case_files) list
		case_files[:] = [x for x in case_files if "CASE" in x]

		#Store all the data from the first file or a specified one
		if not new_case_index:
			data1 = loadmat(f"{path_LP}/{case_files[0]}")
			data2 = loadmat(f"{path_BCP}/{case_files[0]}")
			#Send filenames to MainApp --> Sends to a dropdown menu in MainWindow
			self.case_files_submitted.emit(case_files)
		else: 
			data1 = loadmat(f"{path_LP}/{case_files[new_case_index]}")
			data2 = loadmat(f"{path_BCP}/{case_files[new_case_index]}")

		#Merge both dictionaries
		data = {**data1["rec"], **data2["rec"]}

		#Remove non-lists, and the length of the longest list
		max_length = len(data["s_ecg"])
		for key in data.copy().keys():
			if isinstance(data[key], list):
				if (len(data[key]) >= max_length):
					max_length = len(data[key])
			else:
				del data[key]


		# #For loop to inspect dict hierarchy
		# for key in data.keys():
		# 	if isinstance(data[key], list):
		# 		print("{} - arraylength: {}".format(key, len(data[key])))
		# 	elif type(data[key]) == int:
		# 		print("{} - value: {}".format(key, data[key]))


		#Flatten lists from:   [[1], [3], [6], [2]]  --> [1,3,6,2]
		for key, value in data.items():
			data[key] = [item for sublist in value for item in sublist]


		#Extend all lists to equal the longest in length
		for key, value in data.copy().items():
			length = len(data[key])
			diff = max_length - length
			if diff > 0:
				for i in range(0, diff):
					data[key].append(float('nan'))



		# date = time.ctime(os.path.getmtime(f"{path_LP}/{case_files[0]}"))

		#Send a signal containing the data back to MainApp
		self.case_data_submitted.emit(data, new_case_index)
		self.close()