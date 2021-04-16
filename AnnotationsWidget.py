import pyqtgraph as pg

class AnnotationsWidget(pg.PlotWidget):
    def __init__(self, useOpenGL=True):
        super().__init__()
        self.hideAxis('bottom')
        self.hideAxis('left')
        self.setBackground('w')
        self.setMouseEnabled(x=False, y=False)
        self.important_annotations = {'Power On': 'S', 
                                    'Generic':' G',
                                    'Oxygen': 'O',
                                    'Nitroglycerin': 'N',
                                    'Morphine': 'M',
                                    'Epinephrine': 'Ep',
                                    'Atropine': 'A',
                                    'Lidocaine': 'L',
                                    'Power Off': 'E'
                                    }

    def _setTags(self, case):
        for i in range(len(case["metadata"]["ann"])):
            if case["metadata"]["ann"][i] in self.important_annotations:
                tag = case["metadata"]["ann"][i]
                if i == 0:
                    self.addItem(pg.InfiniteLine(pos=i, label=self.important_annotations[tag], pen=pg.mkPen('g', width=2), labelOpts={'color': 'w', 'position': 0.6, 'fill': 'g'}))
                elif i == len(case["metadata"]["ann"])-1:
                    self.addItem(pg.InfiniteLine(pos=i, label=self.important_annotations[tag], pen=pg.mkPen('r', width=2), labelOpts={'color': 'w', 'position': 0.6, 'fill': 'r'}))
                else:
                    self.addItem(pg.InfiniteLine(pos=i, label=self.important_annotations[tag], pen=pg.mkPen('b', width=2), labelOpts={'color': 'w', 'position': 0.6, 'fill': 'b'}))

        
