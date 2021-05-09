import numpy as np

r"""
The menu doesn't pop up when hovering above an existing ROI, thus
we know that the position given isn't within the range of an existing ROI.
Check for 0-max and space enough based on the circle's size.
"""
class AddROI(object):

    @staticmethod
    def addRoi(rawSignal, metaSignal, case, pos, sizeX):
        if pos - 2*sizeX >= 0.0 and pos + 2*sizeX <= len(case["data"][rawSignal]):
            print("Adding ROI for " + rawSignal + " using metadata[" + metaSignal + "] at position " + str(pos) + " with size " + str(sizeX))
