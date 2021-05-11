#Static class with some utility methods for various classes.
#Added here not to clutter code.

#3rd party libraries
import numpy as np
from mat4py import loadmat
try:
	import cPickle as pickle
except ImportError:
	import pickle


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
        for key, value in dataset.items():
            if Utility.isList(value) and key != "fs":
                length = Utility._findRealValue(len(value) - 1, 0, -1, value) + 1
                value = value[:length]
                dataset[key] = value
                if len(value) > maxLength:
                    maxLength = len(value)

        for key, value in dataset.items():
                if Utility.isList(value) and key != "fs":
                    dataset[key] = np.pad(value, (0, maxLength - len(value)), "constant", constant_values=(0, np.inf))
        
    #Check if list is a Python list or Numpy list.
    @staticmethod
    def isList(aList):
        if isinstance(aList, list) or isinstance(aList, np.ndarray):
            return True
        else:
            return False
    
    #Set a limit?
    @staticmethod
    def displaceSignal(aList, seconds, frequency):
        finalDisplacement = int(seconds*frequency)
        resultList = None
        if finalDisplacement >= 0:
            resultList = np.pad(aList, (finalDisplacement, 0), "constant", constant_values=(np.nan, 0))
        else:
            resultList = aList[abs(finalDisplacement):]
        return [resultList, finalDisplacement]

    @staticmethod
    def convertMatToPickle(datasetFilepath, subsetFilepath, fileName):
        try:
            with open(datasetFilepath + subsetFilepath + "Pickle/" + fileName + ".p", "rb") as fp:
                dataset = pickle.load(fp)
                if "fullFile" in dataset and dataset["fullFile"] == True:
                    dataset.pop("fullFile")
                    print(subsetFilepath + " loaded with pickle.")
                    return dataset
                else:
                    raise Exception("Pickle file corrupted.")
        except (IOError, Exception) as e:
            print(e)
            #Selve metadata.mat filen krever annen håndtering, da denne inneholder data fra alle tilfeller.
            if fileName == "metadata":
                annotationsDataset = loadmat(datasetFilepath + subsetFilepath + "metadata.mat").get("metadata")
                dataset = {}
                for i in range(len(annotationsDataset) - 1):
                    key = annotationsDataset["reg_name"][i]
                    newDict = dict()
                    for k in annotationsDataset:
                        if k == "reg_name":
                            continue
                        newDict.update({k: annotationsDataset[k][i]})
                    dataset.update({key: newDict})
                    Utility.flattenVector(dataset[key])
                    Utility.array2NumpyArray(dataset[key])
                return Utility.savePickleFile(datasetFilepath, subsetFilepath, fileName, dataset)
            else:
                dataset = loadmat(datasetFilepath + subsetFilepath + "MAT/" + fileName + ".mat").get("rec")
                Utility.flattenVector(dataset)
                Utility.array2NumpyArray(dataset)
                return Utility.savePickleFile(datasetFilepath, subsetFilepath, fileName, dataset)
    
    @staticmethod
    def savePickleFile(datasetFilepath, subsetFilepath, fileName, dataset):
        try:
            with open(datasetFilepath + subsetFilepath + "Pickle/" + fileName + ".p", "wb") as fp:
                dataset["fullFile"] = True
                pickle.dump(dataset, fp, protocol=pickle.HIGHEST_PROTOCOL)
                dataset.pop("fullFile")
                return dataset
        except IOError as e:
            print(e)
            return dataset

    @staticmethod
    def normalizeSignals(case):
        #CO2
        s_CO2 = case["data"]["s_CO2"]
        case["data"]["s_CO2"] = np.where((np.isnan(s_CO2)) | (s_CO2 < -5) | ((s_CO2 > 150) & (s_CO2 < np.inf)), 0, s_CO2)
        #PPG
        s_ibp = case["data"]["s_ppg"]
        case["data"]["s_ppg"] = np.where((np.isnan(s_ibp)) | (s_ibp < -10) | ((s_ibp > 300) & (s_ibp < np.inf)), 0, s_ibp)
        #TTI: normal and vent
        s_tti = case["data"]["s_imp"]
        case["data"]["s_imp"] = np.where((np.isnan(s_tti)), 0, s_tti)
        #EKG
        s_ecg = case["data"]["s_ecg"]
        case["data"]["s_ecg"] = np.where(((s_ecg > 5) & (s_ecg < np.inf)) | (s_ecg < -5), 0, s_ecg)    
           
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
                return [0, Utility._findRealValue(pos, len(rawData) - 1, 1, rawData)]
            elif movement["leftBorder"] < 0.0:
                return [0, Utility._findRealValue(pos, -1, -1, rawData)]
        else:
            if np.isnan(rawData[int(np.round(metaData[1]*250))]):
                raise Exception("ROI initiated outside of graph. Try removing it and placing a new one.")
            if movement["rightBorder"] > 0.0:
                return [-1, Utility._findRealValue(pos+size, len(rawData) - 1, 1, rawData)]
            elif movement["rightBorder"] < 0.0:
                return [-1, Utility._findRealValue(pos+size, -1, -1, rawData)]

    @staticmethod
    def _findRealValue(pos, startIndex, iteration, rawData):
        for i in range(int(np.round(pos)), startIndex, iteration):
            if not np.isnan(rawData[i]):
                return i