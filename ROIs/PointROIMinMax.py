import pyqtgraph as pg
import numpy as np

from ROIs.PointROI import PointROI

from PyQt5 import QtCore as qtc

class PointROIMinMax(PointROI):
    index = None
    pairIndex = None

    def __init__(self, caseArray, index, viewRange, pos, delay, size=None, radius=None, **args):
        self.index = index[0]
        self.pairIndex = index[1]
        if size is None:
            if radius is None:
                raise TypeError("Must provide either size or radius.")
            size = (radius*2, radius*2)

        PointROI.__init__(self, caseArray, self.index, viewRange, pos, size, delay, **args)
        self.maxBounds = {}        
        #Am i the point farthest to the left?
        if self.index == 0 and self.pairIndex == 0:
            self.maxBounds["left"] = viewRange[0][0]
        else:
            if self.pairIndex == 0:
                self.maxBounds["left"] = viewRange[0][0] if viewRange[0][0] > self.caseArray[self.index - 1][-1]*250 + delay else self.caseArray[self.index - 1][-1]*250 + delay
            else:
                self.maxBounds["left"] = viewRange[0][0] if viewRange[0][0] > self.caseArray[self.index][self.pairIndex - 1]*250 + delay else self.caseArray[self.index][self.pairIndex - 1]*250 + delay
        #Am i the point farthest to the right?
        if self.index == len(self.caseArray) - 1 and self.pairIndex == 1:
            self.maxBounds["right"] = viewRange[0][1]
        else:
            if self.pairIndex == 0:
                self.maxBounds["right"] = viewRange[0][1] if viewRange[0][1] < self.caseArray[self.index][self.pairIndex + 1]*250 + delay else self.caseArray[self.index][self.pairIndex + 1]*250 + delay
            else:
                self.maxBounds["right"] = viewRange[0][1] if viewRange[0][1] < self.caseArray[self.index + 1][0]*250 + delay else self.caseArray[self.index + 1][0]*250 + delay
        
        self.maxBounds["bottom"] = viewRange[1][0]
        self.maxBounds["top"] = viewRange[1][1]