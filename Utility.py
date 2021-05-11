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
    def normalizeSignals(case):
        #EKG
        s_ecg = case["data"]["s_ecg"]
        case["data"]["s_ecg"] = np.where(((s_ecg > 5) & (s_ecg < np.inf)) | (s_ecg < -5), 0, s_ecg)
        #TTI: normal and vent
        s_tti = case["data"]["s_imp"]
        case["data"]["s_imp"] = np.where((np.isnan(s_tti)), 0, s_tti)
        #PPG
        s_ibp = case["data"]["s_ppg"]
        case["data"]["s_ppg"] = np.where((np.isnan(s_ibp)) | (s_ibp < -10) | ((s_ibp > 300) & (s_ibp < np.inf)), 0, s_ibp)
        #CO2
        s_CO2 = case["data"]["s_CO2"]
        case["data"]["s_CO2"] = np.where((np.isnan(s_CO2)) | (s_CO2 < -5) | ((s_CO2 > 150) & (s_CO2 < np.inf)), 0, s_CO2)
    
    @staticmethod
    def clearPadding(case):    
        #Set padding to NaN.
        for key, value in case["data"].items():
            case["data"][key] = np.where(value == np.inf, np.nan, value)


    #ROI methods.
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

        ySize = yRatio*prefPixelSize
        xSize = xRatio*prefPixelSize

        return {"sizeX": xSize/np.log10(xDiff*0.05), "sizeY": ySize/np.log10(xDiff*0.05)}

    @staticmethod
    def snapRoiIntoValidPosition(movement, metaData, rawData, pos, size):
		#Left RegionROI's handle moved/left MinMaxCircleROI moved.
        if abs(movement["leftBorder"]) > abs(movement["rightBorder"]):
            #Some ROIs are initiated outside of graph. Inform user to remove and position new one.
            if np.isnan(rawData[int(np.round(metaData[0]*250))]):
                raise Exception("ROI initiated outside of graph. Try removing it and placing a new one.")
            elif movement["leftBorder"] > 0.0:
                return [0, Utility._snapRoiMyIterator(pos, len(rawData) - 1, 1, rawData)]
            elif movement["leftBorder"] < 0.0:
                return [0, Utility._snapRoiMyIterator(pos, -1, -1, rawData)]
        else:
            if np.isnan(rawData[int(np.round(metaData[1]*250))]):
                raise Exception("ROI initiated outside of graph. Try removing it and placing a new one.")
            if movement["rightBorder"] > 0.0:
                return [-1, Utility._snapRoiMyIterator(pos+size, len(rawData) - 1, 1, rawData)]
            elif movement["rightBorder"] < 0.0:
                return [-1, Utility._snapRoiMyIterator(pos+size, -1, -1, rawData)]

    @staticmethod
    def _snapRoiMyIterator(pos, startIndex, iteration, rawData):
        for i in range(int(np.round(pos)), startIndex, iteration):
            if not np.isnan(rawData[i]):
                return i