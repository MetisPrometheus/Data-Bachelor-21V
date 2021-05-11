#Standard Libraries
import json

#3rd Party Libraries
from PyQt5 import QtWidgets as qtw
from PyQt5 import QtCore as qtc
from PyQt5 import QtGui as qtg

class MW_Controls(qtw.QWidget):

	request_timeline_window = qtc.pyqtSignal(str, str)

	new_span = qtc.pyqtSignal(int)
	new_case_index = qtc.pyqtSignal(int)
	checkbox_signal = qtc.pyqtSignal(str, bool)
	overlay_submitted = qtc.pyqtSignal(bool, str)
	timeline_changed = qtc.pyqtSignal(int)
	checkbox_dict = qtc.pyqtSignal(dict)
	co2_input_submitted = qtc.pyqtSignal(float)
	bcg_input_submitted = qtc.pyqtSignal(int)
	console_msg_submitted = qtc.pyqtSignal(str, int)
	settings = {}
	co2 = None
	bcg = None

	def __init__(self):
		super().__init__()

		#TOP PART OF GUI (Controllers)
		self.dropdown_cases = qtw.QComboBox(currentIndexChanged=self.emitNewCaseIndex)
		self.dropdown_span = qtw.QComboBox(currentTextChanged=self.emitNewSpan)

		span = ["60s", "30s", "10s", "5s", "2s"]
		self.dropdown_cases.blockSignals(True)
		self.dropdown_span.insertItems(0, span)
		self.dropdown_cases.blockSignals(False)

		self.co2_label = qtw.QLabel("CO2:")
		self.co2_label.setFixedWidth(25)
		self.co2_input = qtw.QLineEdit(returnPressed=self.co2InputEntered)
		self.double_validator = qtg.QDoubleValidator(bottom=0, top=2, decimals=3)
		self.double_validator.setNotation(qtg.QDoubleValidator.StandardNotation)
		self.co2_input.setValidator(self.double_validator)
		self.co2_input.setFixedWidth(25)

		self.bcg_label = qtw.QLabel("BCG:")
		self.bcg_label.setFixedWidth(25)
		self.bcg_input = qtw.QLineEdit(returnPressed=self.bcgInputEntered)
		self.bcg_input.setValidator(qtg.QIntValidator())
		self.bcg_input.setFixedWidth(25)

		self.roi_checkbox1 = qtw.QCheckBox("QRS", clicked=lambda:self.emitRoiCheckboxState(self.roi_checkbox1, 's_ecg'))
		self.roi_checkbox2 = qtw.QCheckBox("VENT WF", clicked=lambda:self.emitRoiCheckboxState(self.roi_checkbox2, 's_vent'))
		self.roi_checkbox3 = qtw.QCheckBox("CO2 ANNOT", clicked=lambda:self.emitRoiCheckboxState(self.roi_checkbox3, 's_CO2'))

		self.dropdown_timelines = qtw.QComboBox(currentIndexChanged=self.changeTimeline)
		self.dropdown_timelines.insertItems(0, ["Timeline 1", "Timeline 2", "Timeline 3"])

		add_icon = qtg.QIcon(qtg.QPixmap("add.png"))
		self.add_timeline = qtw.QPushButton(icon=add_icon, clicked=lambda:self.requestTimelineSettings("Add"))
		remove_icon = qtg.QIcon(qtg.QPixmap("remove.png"))
		self.remove_timeline= qtw.QPushButton(icon=remove_icon, clicked=lambda:self.requestTimelineSettings("Delete"))
		edit_icon = qtg.QIcon(qtg.QPixmap("edit.png"))
		self.edit_timeline = qtw.QPushButton(icon=edit_icon, clicked=lambda:self.requestTimelineSettings("Edit"))

		self.checkboxes = {}
		self.checkboxes["s_ecg"] = qtw.QCheckBox("ECG (mV)", clicked=lambda:self.emitCheckboxState("s_ecg"))
		self.checkboxes["s_CO2"] = qtw.QCheckBox("CO2 (mmHg)", clicked=lambda:self.emitCheckboxState("s_CO2"))
		self.checkboxes["s_ppg"] = qtw.QCheckBox("PPG (SpO2)", clicked=lambda:self.emitCheckboxState("s_ppg"))
		self.checkboxes["s_vent"] = qtw.QCheckBox("TTI (\u03A9)", clicked=lambda:self.emitCheckboxState("s_vent"))
		self.checkboxes["s_bcg1"] = qtw.QCheckBox("BCG1 (V)", clicked=lambda:self.emitCheckboxState("s_bcg1"))
		self.checkboxes["s_bcg2"] = qtw.QCheckBox("BCG1 (V)", clicked=lambda:self.emitCheckboxState("s_bcg2"))

		self.check_layout = qtw.QHBoxLayout()
		self.check_layout.addWidget(self.checkboxes["s_ecg"])
		self.check_layout.addWidget(self.checkboxes["s_CO2"])
		self.check_layout.addWidget(self.checkboxes["s_ppg"])
		self.check_layout.addWidget(self.checkboxes["s_vent"])
		self.check_layout.addWidget(self.checkboxes["s_bcg1"])
		self.check_layout.addWidget(self.checkboxes["s_bcg2"])

		self.dropdown_layout = qtw.QHBoxLayout()
		self.dropdown_layout.addWidget(self.dropdown_cases)
		self.dropdown_layout.addWidget(self.dropdown_span)

		self.dropdown_layout.addWidget(self.roi_checkbox1)
		self.dropdown_layout.addWidget(self.roi_checkbox2)
		self.dropdown_layout.addWidget(self.roi_checkbox3)

		self.dropdown_layout.addWidget(self.co2_label)
		self.dropdown_layout.addWidget(self.co2_input)
		self.dropdown_layout.addWidget(self.bcg_label)
		self.dropdown_layout.addWidget(self.bcg_input)

		self.dropdown_layout.addWidget(self.dropdown_timelines)
		self.dropdown_layout.addWidget(self.add_timeline)
		self.dropdown_layout.addWidget(self.remove_timeline)
		self.dropdown_layout.addWidget(self.edit_timeline)

		self.top_layout = qtw.QHBoxLayout()
		self.top_layout.addLayout(self.dropdown_layout)
		self.top_layout.addLayout(self.check_layout)
		self.setLayout(self.top_layout)

	def receiveInputValues(self, co2, bcg):
		self.co2 = co2
		self.bcg = bcg
		self.co2_input.setText(f"{self.co2}")
		self.bcg_input.setText(f"{self.bcg}")

	def co2InputEntered(self):
		number = float(self.co2_input.text())
		self.co2_input.setText(str(number))
		if 0 <= number <= 2:
			print("CO2 input successfully emitted")
			self.co2 = number
			self.co2_input_submitted.emit(number)
		else:
			self.co2_input.setText(f"{self.co2}")
			self.console_msg_submitted.emit("Invalid CO2 value submitted. Allowed values are between -1.5 to 1.5.", 5000)
		print(f"The user has entered value: {number} in the co2 input field")

	def bcgInputEntered(self):
		number = int(self.bcg_input.text())
		self.bcg_input.setText(str(number))
		if number >= 0:
			print("bcg input successfully emitted")
			self.bcg = number
			self.bcg_input_submitted.emit(number)
		else:
			self.bcg_input.setText(f"{self.bcg}")
			self.console_msg_submitted.emit("Invalid BCG value submitted. Only positive integers allowed.", 5000)
		print(f"The user has entered value: {number} in the bcg input field")

	def emitRoiCheckboxState(self, signal, data):
		state = signal.isChecked()
		self.overlay_submitted.emit(state, data)
		
	def requestTimelineSettings(self, option):
		current_timeline = self.dropdown_timelines.currentText()
		self.request_timeline_window.emit(option, current_timeline)

	def updateTimelines(self, option, timeline):
		if option == "Add":
			last_index = self.dropdown_timelines.count()
			self.dropdown_timelines.addItem(timeline)
			self.dropdown_timelines.setCurrentIndex(last_index)

		elif option == "Delete":
			current_index = self.dropdown_timelines.currentIndex()
			self.dropdown_timelines.removeItem(current_index)

		elif option == "Edit":
			current_index = self.dropdown_timelines.currentIndex()
			self.dropdown_timelines.blockSignals(True)
			self.dropdown_timelines.removeItem(current_index)
			self.dropdown_timelines.insertItems(current_index, [timeline])
			self.dropdown_timelines.setCurrentIndex(current_index)
			self.dropdown_timelines.blockSignals(False)
		'''
		#TODO MAKE SURE ALL THIS IS UPDATED IN ANNOTATIONS OR WHEREVER THE FUCK ITS STORED (Emil/Sebbi)
		Check MainApp.py, last comment 
		'''

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

	def showTimelines(self, timelines):
		self.dropdown_timelines.blockSignals(True)
		self.dropdown_timelines.insertItems(0, timelines)
		self.dropdown_timelines.blockSignals(False)

	def changeTimeline(self, new_index):
		print(f"Timeline index changed to: {new_index}")
		self.timeline_changed.emit(new_index)