# PyQt4 imports
from PyQt5 import QtWidgets as qtw


class MainGLWidget(qtw.QMainWindow):
    # default window size

    def __init__(self):
        super().__init__()
        self.show()
        pass