#Static class with some utility methods for various classes.
#Added here not to clutter code.

#3rd party libraries
import numpy as np

class Utility(object):

    #Convert Matlabs column vectors (2D-arrays) into row vectors (1D-arrays).
    @staticmethod
    def flattenVector(dataset):
        for key, value in dataset.items():
            if Utility.isList(value) and Utility.isList(value[0]) and len(value[0]) == 1:
                dataset[key] = [j for sub in value for j in sub]

    #Convert all arrays in given dictionary to numpy arrays for faster manipulation and iteration.
    @staticmethod
    def array2NumpyArray(dataset):
        for key, _ in dataset.items():
            if Utility.isList(dataset[key]):
                dataset[key] = np.array(dataset[key])

    #Pad lists to same length as longest lost in given dictionary.
    @staticmethod
    def equalizeLengthLists(dataset):
        maxLength = 0
        for _, value in dataset.items():
            if Utility.isList(value) and len(value) > maxLength:
                maxLength = len(value)

        for key, value in dataset.items():
            if Utility.isList(value):
                dataset[key] = np.pad(value, (0, maxLength - len(value)), "constant", constant_values=(0, np.inf))

    #Check if list is a Python list or Numpy list.
    @staticmethod
    def isList(aList):
        if isinstance(aList, list) or isinstance(aList, np.ndarray):
            return True
        else:
            return False

    @staticmethod
    def getRangeRatio(vb):
        #Sjekk hvilket spenn er minst. Del så begge spenn med dette.
        xyArray = vb.state["viewRange"]

        prefPixelSize = 10

        xDiff = abs(xyArray[0][1] - xyArray[0][0])
        xPixels = vb.boundingRect().width()
        xRatio = xDiff/xPixels
        
        yDiff = abs(xyArray[1][1] - xyArray[1][0])
        yPixels = vb.boundingRect().height()
        yRatio = yDiff/yPixels

        #For det meste så vil Y spennet være mindre enn X, så start med dette for å spare tid.
        #Ikke sløs tid på å beregne diffY/diffY, heller.
        if yRatio < xRatio:
            ySize = yRatio*prefPixelSize
            xSize = xRatio*prefPixelSize
        else:
            xSize = yRatio*prefPixelSize
            ySize = xRatio*prefPixelSize

        return {"sizeX": xSize/np.log10(xDiff*0.05), "sizeY": ySize/np.log10(xDiff*0.05)}