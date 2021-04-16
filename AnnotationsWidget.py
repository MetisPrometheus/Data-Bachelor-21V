import pyqtgraph as pg

class AnnotationsWidget(pg.PlotWidget):
    def __init__(self, useOpenGL=True):
        super().__init__()
        self.hideAxis('bottom')
        self.hideAxis('left')
        self.setBackground('w')
        self.setMouseEnabled(x=False, y=False)
        self.important_annotations = ['Power On', 'Generic', 'Oxygen', 'Nitroglycerin', 'Morphine', 'Epinephrine', 'Atropine', 'Lidocaine','Power Off']

    def _setTags(self, case):
        for i in range(len(case["metadata"]["ann"])):
            if case["metadata"]["ann"][i] in self.important_annotations:
                self.addItem(pg.InfiniteLine(pos=i, label=case["metadata"]["ann"][i], pen=pg.mkPen('b', width=2), labelOpts={'color': 'w', 'position': 0.7, 'fill': 'b'}))

        
