#3rd Party Libraries
from PyQt5 import QtWidgets as qtw
from PyQt5 import QtCore as qtc

#Local Classes
from MW_Controls import MW_Controls
from MW_GraphCollection import MW_GraphCollection

class MainWindow(qtw.QWidget):

	graph_toggle = qtc.pyqtSignal(str, bool)
	slider_incs_submitted = qtc.pyqtSignal(int)
	span_submitted = qtc.pyqtSignal(int)

	def __init__(self):
		super().__init__()
		self.setWindowTitle("Main Window")

		# -------- Main Window Sections --------
		self.MW_Controls = MW_Controls()
		self.MW_GraphCollection = MW_GraphCollection()

		# -------- Signals & Slots -------- 
		self.MW_Controls.checkbox_state.connect(self.MW_GraphCollection.toggleGraph)


		#Wrap a main_layout around the top-, body- and bottom part of the GUI
		self.main_layout = qtw.QVBoxLayout()
		self.main_layout.addWidget(self.MW_Controls)
		self.main_layout.addWidget(self.MW_GraphCollection)
		self.setLayout(self.main_layout)


	def receiveNewCase(self, data, new_case_index):
		self.MW_GraphCollection.plotGraphs(data, new_case_index)

	def receiveFilenames(self, filenames):
		self.MW_Controls.showCases(filenames)

