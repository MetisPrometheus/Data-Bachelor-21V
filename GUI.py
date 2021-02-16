import sys
import os
import pyqtgraph as pg
from PyQt5 import QtWidgets as qtw
from PyQt5 import QtCore as qtc
from mat4py import loadmat

# from vispy import scene


class MainApp(qtw.QApplication):
	#Main Application Object
	def __init__(self, argv):
		super().__init__(argv)

		#create datacontroller object to return case data upon request
		self.data_controller = DataController()

		#create initial window
		self.initial_window = InitialWindow()
		self.initial_window.show()

		#create main window
		self.main_window = MainWindow()

		#Signals and slots -----
		self.initial_window.dataset_path_submitted[str].connect(self.data_controller.setDir)
		self.main_window.new_case[int].connect(self.data_controller.getCaseData)
		self.main_window.graph_toggle.connect(self.main_window.showGraph)
		self.data_controller.case_data_submitted.connect(self.main_window.createGraphs)
		self.data_controller.case_data_submitted.connect(self.main_window.createCheckboxes)
		self.data_controller.case_data_submitted.connect(self.main_window.show)
		self.data_controller.case_files_submitted.connect(self.main_window.showCases)
		
	

class InitialWindow(qtw.QWidget):

	dataset_path_submitted = qtc.pyqtSignal(str)

	def __init__(self):
		super().__init__()
		self.button = qtw.QPushButton("Test", clicked=self.getDirectory)

		self.setLayout(qtw.QVBoxLayout())
		self.layout().addWidget(self.button)

	def getDirectory(self):
		if "folders.txt" in next(os.walk(os.getcwd()))[2]:
			with open("folders.txt", "r") as f:
				dir_path = f.readlines()[0]
				self.dataset_path_submitted.emit(dir_path)
			pass
		else: 
			with open("folders.txt", "w") as f:
				dir_path = qtw.QFileDialog.getExistingDirectory()
				dir_name = dir_path.split("/")[-1]
				if dir_name == "2 DATASET":
					f.write(dir_path)
					self.dataset_path_submitted.emit(dir_path)
				else:
					print("Incorrect folder chosen") 
				self.close()	



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
		# _, _, casePaths2 = next(os.walk(path_BCP))

		#Remove non (case.mat) files from the (case_files) list
		case_files[:] = [x for x in case_files if "CASE" in x]

		if not new_case_index:
			data1 = loadmat(f"{path_LP}/{case_files[0]}")
			data2 = loadmat(f"{path_BCP}/{case_files[0]}")
			self.case_files_submitted.emit(case_files)
		else: 
			data1 = loadmat(f"{path_LP}/{case_files[new_case_index]}")
			data2 = loadmat(f"{path_BCP}/{case_files[new_case_index]}")


		#Merge both dictionaries and remove nonlist entries
		data = {**data1["rec"], **data2["rec"]}
		for key in data.copy().keys():
			if not isinstance(data[key], list):
				del data[key]

		#For loop to inspect dict hierarchy
		for key in data.keys():
			if isinstance(data[key], list):
				print("{} - arraylength: {}".format(key, len(data[key])))
			elif type(data[key]) == int:
				print("{} - value: {}".format(key, data[key]))


		#Flatten lists from:   [[1], [3], [6], [2]]  --> [1,3,6,2]
		for key, value in data.items():
			data[key] = [item for sublist in value for item in sublist]



		#Send a signal containing the data back to MainApp
		self.case_data_submitted.emit(data, new_case_index)
		self.close()



class PlotGraph(pg.PlotWidget):

	def __init__(self, data):
		super().__init__()
		self.plotData(data)

	def plotData(self, data):
		self.time = list(range(1,len(data)+1))
		self.plot(self.time, data)



class MainWindow(qtw.QWidget):

	new_case = qtc.pyqtSignal(int)
	graph_toggle = qtc.pyqtSignal(str, bool)

	def __init__(self):
		super().__init__()

		#TOP PART OF GUI (Controllers)
		self.dropdown_cases = qtw.QComboBox(currentIndexChanged=self.changeCase)
		self.dropdown_span = qtw.QComboBox()

		self.checkboxes = {}
		self.checkboxes["s_CO2"] = qtw.QCheckBox("CO2", clicked=lambda:self.graphToggler("s_CO2"))
		self.checkboxes["s_ppg"] = qtw.QCheckBox("ppg", clicked=lambda:self.graphToggler("s_ppg"))
		self.checkboxes["s_imp"] = qtw.QCheckBox("imp", clicked=lambda:self.graphToggler("s_imp"))
		self.checkboxes["s_ecg"] = qtw.QCheckBox("ecg", clicked=lambda:self.graphToggler("s_ecg"))
		self.checkboxes["s_vent"] = qtw.QCheckBox("vent", clicked=lambda:self.graphToggler("s_vent"))
		self.checkboxes["s_bcg1"] = qtw.QCheckBox("bcg1", clicked=lambda:self.graphToggler("s_bcg1"))
		self.checkboxes["s_bcg2"] = qtw.QCheckBox("bcg2", clicked=lambda:self.graphToggler("s_bcg2"))

		self.check_layout = qtw.QHBoxLayout()
		self.check_layout.addWidget(self.checkboxes["s_CO2"])
		self.check_layout.addWidget(self.checkboxes["s_ppg"])
		self.check_layout.addWidget(self.checkboxes["s_imp"])
		self.check_layout.addWidget(self.checkboxes["s_ecg"])
		self.check_layout.addWidget(self.checkboxes["s_vent"])
		self.check_layout.addWidget(self.checkboxes["s_bcg1"])
		self.check_layout.addWidget(self.checkboxes["s_bcg2"])

		self.dropdown_layout = qtw.QHBoxLayout()
		self.dropdown_layout.addWidget(self.dropdown_cases)
		self.dropdown_layout.addWidget(self.dropdown_span)

		self.top_layout = qtw.QHBoxLayout()
		self.top_layout.addLayout(self.dropdown_layout)
		self.top_layout.addLayout(self.check_layout)

		#MIDDLE PART OF GUI (Various Graphs)
		self.graphs = {}
		self.body_layout = qtw.QVBoxLayout()

		#Wrap a main_layout around the (top part) and (body part) of the GUI
		self.main_layout = qtw.QVBoxLayout()
		self.main_layout.addLayout(self.top_layout)
		self.main_layout.addLayout(self.body_layout)
		self.setLayout(self.main_layout)



	#Populate the dropdown menu with the various patient's case.mat files
	def showCases(self, filepaths):
		self.dropdown_cases.blockSignals(True)
		self.dropdown_cases.insertItems(0, filepaths)
		self.dropdown_cases.blockSignals(False)

	def changeCase(self, new_case_index):
		print(f"changed to new case, index {new_case_index}")
		self.new_case.emit(new_case_index)

	def createCheckboxes(self, data):
		# for key in data.keys():ar
		# 	ph = key.split("_")[-1]
		# 	self.checkboxes[key] = qtw.QCheckBox(f"{ph}", clicked=lambda:self.graphToggler(f"{key}"))
		# 	self.check_layout.addWidget(self.checkboxes[key])
		pass

	def graphToggler(self, checkvalue):
		state = self.checkboxes[checkvalue].isChecked()
		self.graph_toggle.emit(checkvalue, state)

	def createGraphs(self, data, new_case):
		if not new_case:
			for key, value in data.items():
				self.graphs[key] = PlotGraph(value)

			for key, value in self.graphs.items():
				self.body_layout.addWidget(value)
				self.graphs[key].hide()
		else:
			#Loop through existing graphwidgets and replot with the new data
			for key, graphObj in self.graphs.items():
				graphObj.clear()
				graphObj.plotData(data[key])		


	def showGraph(self, checkvalue, state):
		print(f"type:{checkvalue}, state:{state}")
		if state:
			self.graphs[checkvalue].show()
		else: 
			self.graphs[checkvalue].hide()





if __name__ == "__main__":
	app = MainApp(sys.argv)	
	sys.exit(app.exec())