import pyqtgraph as pg
from PyQt5 import QtGui as qtg
from PyQt5 import QtCore as qtc

translate = qtc.QCoreApplication.translate
class CustomViewBox(pg.ViewBox):
    sigAddRoiRequest = qtc.pyqtSignal(float)

    graphName = None
    xMouseClickPosition = None

    def __init__(self, graphName, parent=None, border=None, lockAspect=False, enableMouse=True, invertY=False, enableMenu=True, name=None, invertX=False):
        self.graphName = graphName
        pg.ViewBox.__init__(self, parent=None, border=None, lockAspect=False, enableMouse=True, invertY=False, enableMenu=True, name=None, invertX=False)

    def mouseClickEvent(self, ev):
        if ev.button() == qtc.Qt.RightButton and self.menuEnabled():
            ev.accept()
            self.xMouseClickPosition = self.mapSceneToView(ev.pos()).x()
            self.raiseContextMenu(ev)
            #Save the position of the mouseclick and send it with subMenus connected signal.

    def raiseContextMenu(self, ev):
        menu = self.getMenu(ev)
        if menu is not None:
            self.scene().addParentContextMenus(self, menu, ev)
            menu.popup(ev.screenPos().toPoint())
    
    def setRoiMenuEnabled(self, setEnable):
        if setEnable:
            self.roiMenu = qtg.QMenu(translate("ViewBox", "Add ROI"))
            addPoint = qtg.QAction(translate("ViewBox", "Add ROI to " + self.graphName), self.roiMenu)
            addPoint.triggered.connect(self._emitAddRoiRequest)
            self.roiMenu.addAction(addPoint)
            self.roiMenu.addPoint = addPoint
            self.menu.addMenu(self.roiMenu)
        else:
            self.roiMenu = None

    def _getLastMouseClickPositionX(self):
        return self.xMouseClickPosition

    def _emitAddRoiRequest(self, pos):
        self.sigAddRoiRequest.emit(self._getLastMouseClickPositionX())
