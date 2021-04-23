#Standard Libraries
import os
import json

#3rd Party Libraries
from PyQt5 import QtWidgets as qtw
from PyQt5 import QtCore as qtc
from PyQt5 import QtGui as qtg


class TimelineSettings(qtw.QWidget):

	option = ""

	timeline_submitted = qtc.pyqtSignal(str, str)

	def __init__(self):
		super().__init__()
		print("--- Timeline Window Created ---")

		self.label = qtw.QLabel()

		self.input = qtw.QLineEdit()
		# regex = qtc.QRegExp("[a-z-A-Z_]")
		# validator = qtg.QRegExpValidator(regex)
		# self.input.setValidator(validator)

		self.ok_btn = qtw.QPushButton("Confirm", clicked=self.submit)
		self.cancel_btn = qtw.QPushButton("Cancel", clicked=self.close)

		self.button_layout = qtw.QHBoxLayout()
		self.button_layout.addWidget(self.ok_btn)
		self.button_layout.addWidget(self.cancel_btn)

		self.main_layout = qtw.QVBoxLayout()
		self.main_layout.addWidget(self.label)
		self.main_layout.addWidget(self.input)
		self.main_layout.addLayout(self.button_layout)
		self.setLayout(self.main_layout)
		

	def openWindow(self, option, current_timeline):
		self.option = option

		if self.option == "Add":
			self.label.setText("Add New Timeline")
			self.input.show()
			self.input.setText("")

		elif self.option == "Edit":
			self.label.setText("Change Timeline Name")
			self.input.show()
			self.input.setText(f"{current_timeline}")

		elif self.option == "Delete":
			self.label.setText(f"Delete Current Timeline?")
			self.input.hide()

		self.show()

	def submit(self):
		if len(self.input.text()) == 0:
			self.label.setText("This field can't be left empty!")
		else:
			self.timeline_submitted.emit(self.option, self.input.text())
			self.close()

	def closeEvent(self, argv):
		super().closeEvent(argv)
		print(f"||| {self.option} Timeline Window Closed |||")