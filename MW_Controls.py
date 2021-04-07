#3rd Party Libraries
from PyQt5 import QtWidgets as qtw
from PyQt5 import QtCore as qtc

class MW_Controls(qtw.QWidget):

	new_span = qtc.pyqtSignal(int)
	new_case_index = qtc.pyqtSignal(int)
	checkbox_state = qtc.pyqtSignal(str, bool)
	button_pressed = qtc.pyqtSignal(bool)

	def __init__(self):
		super().__init__()

		#TOP PART OF GUI (Controllers)
		self.dropdown_cases = qtw.QComboBox(currentIndexChanged=self.emitCaseIndex)
		self.dropdown_span = qtw.QComboBox(currentTextChanged=self.emitNewSpan)

		span = ["60s", "30s", "10s", "5s", "2s"]
		self.dropdown_cases.blockSignals(True)
		self.dropdown_span.insertItems(0, span)
		self.dropdown_cases.blockSignals(False)

		self.checkboxes = {}
		self.checkboxes["s_ecg"] = qtw.QCheckBox("ecg", clicked=lambda:self.emitCheckboxState("s_ecg"))
		self.checkboxes["s_CO2"] = qtw.QCheckBox("CO2", clicked=lambda:self.emitCheckboxState("s_CO2"))
		self.checkboxes["s_ppg"] = qtw.QCheckBox("ppg", clicked=lambda:self.emitCheckboxState("s_ppg"))
		self.checkboxes["s_imp"] = qtw.QCheckBox("imp", clicked=lambda:self.emitCheckboxState("s_imp"))
		self.checkboxes["s_vent"] = qtw.QCheckBox("vent", clicked=lambda:self.emitCheckboxState("s_vent"))
		self.checkboxes["s_bcg1"] = qtw.QCheckBox("bcg1", clicked=lambda:self.emitCheckboxState("s_bcg1"))
		self.checkboxes["s_bcg2"] = qtw.QCheckBox("bcg2", clicked=lambda:self.emitCheckboxState("s_bcg2"))

		self.check_layout = qtw.QHBoxLayout()
		self.settings_button = qtw.QPushButton("Settings")
		self.check_layout.addWidget(self.checkboxes["s_ecg"])
		self.check_layout.addWidget(self.checkboxes["s_CO2"])
		self.check_layout.addWidget(self.checkboxes["s_ppg"])
		self.check_layout.addWidget(self.checkboxes["s_imp"])
		self.check_layout.addWidget(self.checkboxes["s_vent"])
		self.check_layout.addWidget(self.checkboxes["s_bcg1"])
		self.check_layout.addWidget(self.checkboxes["s_bcg2"])
		self.check_layout.addWidget(self.settings_button)
		

		self.dropdown_layout = qtw.QHBoxLayout()
		self.dropdown_layout.addWidget(self.dropdown_cases)
		self.dropdown_layout.addWidget(self.dropdown_span)
		self.dropdown_layout.addWidget(self.settings_button)

		self.top_layout = qtw.QHBoxLayout()
		self.top_layout.addLayout(self.dropdown_layout)
		self.top_layout.addLayout(self.check_layout)
		self.setLayout(self.top_layout)


	def emitCaseIndex(self, new_case_index):
		self.new_case_index.emit(new_case_index)

	def emitNewSpan(self, new_span_value):
		span = int(new_span_value.split("s")[0])
		self.new_span.emit(span)

	def emitCheckboxState(self, value):
		state = self.checkboxes[value].isChecked()
		self.checkbox_state.emit(value, state)

	#Populate the dropdown menu with the various patient's case.mat files
	def showCases(self, filenames):
		self.dropdown_cases.blockSignals(True)
		self.dropdown_cases.insertItems(0, filenames)
		self.dropdown_cases.blockSignals(False)
