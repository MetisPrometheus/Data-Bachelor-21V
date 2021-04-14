#Standard Libraries
import json

#3rd Party Libraries
from PyQt5 import QtWidgets as qtw
from PyQt5 import QtCore as qtc

class MW_Controls(qtw.QWidget):

	new_span = qtc.pyqtSignal(int)
	new_case_index = qtc.pyqtSignal(int)
	checkbox_signal = qtc.pyqtSignal(str, bool)

	checkbox_dict = qtc.pyqtSignal(dict)
	settings = {}

	def __init__(self):
		super().__init__()

		#TOP PART OF GUI (Controllers)
		self.dropdown_cases = qtw.QComboBox(currentIndexChanged=self.emitNewCaseIndex)
		self.dropdown_span = qtw.QComboBox(currentTextChanged=self.emitNewSpan)

		span = ["60s", "30s", "10s", "5s", "2s"]
		self.dropdown_cases.blockSignals(True)
		self.dropdown_span.insertItems(0, span)
		self.dropdown_cases.blockSignals(False)

		self.checkboxes = {}
		self.checkboxes["s_ecg"] = qtw.QCheckBox("ECG (mV)", clicked=lambda:self.emitCheckboxState("s_ecg"))
		self.checkboxes["s_CO2"] = qtw.QCheckBox("CO2 (mmHg)", clicked=lambda:self.emitCheckboxState("s_CO2"))
		self.checkboxes["s_ppg"] = qtw.QCheckBox("PPG (SpO2)", clicked=lambda:self.emitCheckboxState("s_ppg"))
		self.checkboxes["s_imp"] = qtw.QCheckBox("imp", clicked=lambda:self.emitCheckboxState("s_imp"))
		self.checkboxes["s_vent"] = qtw.QCheckBox("TTI (\u03A9)", clicked=lambda:self.emitCheckboxState("s_vent"))
		self.checkboxes["s_bcg1"] = qtw.QCheckBox("BCG1 (V)", clicked=lambda:self.emitCheckboxState("s_bcg1"))
		self.checkboxes["s_bcg2"] = qtw.QCheckBox("BCG1 (V)", clicked=lambda:self.emitCheckboxState("s_bcg2"))

		self.check_layout = qtw.QHBoxLayout()
		self.check_layout.addWidget(self.checkboxes["s_ecg"])
		self.check_layout.addWidget(self.checkboxes["s_CO2"])
		self.check_layout.addWidget(self.checkboxes["s_ppg"])
		self.check_layout.addWidget(self.checkboxes["s_imp"])
		self.check_layout.addWidget(self.checkboxes["s_vent"])
		self.check_layout.addWidget(self.checkboxes["s_bcg1"])
		self.check_layout.addWidget(self.checkboxes["s_bcg2"])

		self.dropdown_layout = qtw.QHBoxLayout()
		self.dropdown_layout.addWidget(self.dropdown_cases)
		self.dropdown_layout.addWidget(self.dropdown_span)

		self.top_layout = qtw.QHBoxLayout()
		self.top_layout.addLayout(self.dropdown_layout)
		self.top_layout.addLayout(self.check_layout)
		self.setLayout(self.top_layout)

	def showCheckboxes(self, checkboxes):
		for element in checkboxes:
			if element not in self.checkboxes.keys():
				self.checkbox_condition[element] = False

	def saveCheckboxStates(self):
		print("**The checkbox states have been saved**")
		with open("settings.txt", "w") as f:
			json.dump(self.settings, f)

	def emitNewCaseIndex(self, new_case_index):
		print(f"User used dropdown menu to change to a new case with index: {new_case_index}")
		self.new_case_index.emit(new_case_index)

	def emitNewSpan(self, new_span_value):
		span = int(new_span_value.split("s")[0])
		self.new_span.emit(span)

	def emitCheckboxState(self, signal):
		state = self.checkboxes[signal].isChecked()
		#Save the state of the checkbox
		self.settings["checkboxes"][signal] = state
		#Send the state of the checkbox to the graph wrapper for it to show or hide the selected graph
		self.checkbox_signal.emit(signal, state)
		
	def createCheckboxes(self, saved_settings):
		# for key in data.keys():ar
		# 	ph = key.split("_")[-1]
		# 	self.checkboxes[key] = qtw.QCheckBox(f"{ph}", clicked=lambda:self.graphToggler(f"{key}"))
		# 	self.check_layout.addWidget(self.checkboxes[key])

		#Save potential new data signals passed along with the new case 
		self.settings = saved_settings

		#Iterate through the checkboxes and cross off the enabled graphs
		for key, state in self.settings["checkboxes"].items():
			if self.settings["checkboxes"][key]:
				self.checkboxes[key].setChecked(True)
			else:
				self.checkboxes[key].setChecked(False)


	#Populate the dropdown menu with the various case.mat files found in the datasets folder provided
	def showCases(self, filenames):
		self.dropdown_cases.blockSignals(True)
		self.dropdown_cases.insertItems(0, filenames)
		self.dropdown_cases.blockSignals(False)

