import pyqtgraph as pg

class AnnotationsWidget(pg.PlotWidget):
    def __init__(self, useOpenGL=True):
        super().__init__()
        self.hideAxis('bottom')
        self.hideAxis('left')
        self.setBackground('w')
        self.setMouseEnabled(x=False, y=False)
        self.important_annotations = {'Power On': 'S', 
                                    'Generic':' NR',
                                    'Oxygen': 'HV',
                                    'Nitroglycerin': 'LU',
                                    'Morphine': 'TA',
                                    'IV Access': 'HB',
                                    'Intubation': 'IA',
                                    'CPR': 'FA',
                                    'Epinephrine': 'IV',
                                    'Atropine': 'IVS',
                                    'Lidocaine': 'OB',
                                    'Power Off': 'E'
                                    }

    def _setTags(self, case):
        self.clear()
        self.setLimits(xMax=len(case["data"]["s_ecg"])-1, xMin=0)
        for i in range(len(case["metadata"]["ann"])):
            if case["metadata"]["ann"][i] in self.important_annotations:
                tag = case["metadata"]["ann"][i]
                if i == 0:
                    line = pg.InfiniteLine(pos=case["metadata"]["t_ann"][i]*250, label=self.important_annotations[tag], pen=pg.mkPen('g', width=2), labelOpts={'color': 'w', 'position': 0.6, 'fill': 'g'})
                    self.addItem(line)
                elif i == len(case["metadata"]["ann"])-1:
                    line = pg.InfiniteLine(pos=case["metadata"]["t_ann"][i]*250, label=self.important_annotations[tag], pen=pg.mkPen('r', width=2), labelOpts={'color': 'w', 'position': 0.6, 'fill': 'r'})
                    self.addItem(line)
                else:
                    line = pg.InfiniteLine(pos=case["metadata"]["t_ann"][i]*250, label=self.important_annotations[tag], pen=pg.mkPen('b', width=2), labelOpts={'color': 'w', 'position': 0.6, 'fill': 'b'})
                    self.addItem(line)

