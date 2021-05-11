import numpy as np

class AddROI(object):
    graphRangeCircleROIs = ["s_ecg", "s_vent"]
    graphMinMaxCircleROIs = ["s_CO2"]

    @staticmethod
    def addRoi(rawSignal, metaSignal, case, pos, sizeX, viewRange, widthPixels):
        #Offset due to graph y-axis padding from left and mouse pointer size.
        diffValues = abs(viewRange[1] - viewRange[0])
        valuesPerPixel = diffValues/widthPixels
        pos += 26.0 * valuesPerPixel
        if rawSignal in AddROI.graphRangeCircleROIs:
            return AddROI._addRangeCircleROIs(rawSignal, metaSignal, case, pos, sizeX)
        elif rawSignal in AddROI.graphMinMaxCircleROIs:
            return AddROI._addMinMaxCircleROIs(rawSignal, metaSignal, case, pos, sizeX)
        else:
            return "Graph does not have ROIs."
        
    @staticmethod
    def _addRangeCircleROIs(rawSignal, metaSignal, case, pos, sizeX):
        
        rawSignalList = case["data"][rawSignal]
        metaSignalList = case["metadata"][metaSignal]*250

        if (
            (pos - 2*sizeX >= 0.0 and not np.isnan(rawSignalList[int(np.round(pos - 2*sizeX))])) and 
            (pos + 2*sizeX <= len(rawSignalList) and not np.isnan(rawSignalList[int(np.round(pos + 2*sizeX))]))
            ):
            #Check for empty list since this requires special attention, i.e. initiating list.
            if len(metaSignalList) == 0:
                case["metadata"][metaSignal] = np.empty([1, 3])
                case["metadata"][metaSignal][0] = (pos-sizeX)/250
                case["metadata"][metaSignal][1] = pos/250
                case["metadata"][metaSignal][-1] = (pos+sizeX)/250
                return "Roi Successfully added!"
            else:
                result = AddROI._calculatePosition(rawSignalList, metaSignalList, pos, sizeX)
                if "pos" in result and "myIndex" in result:
                    pos = result["pos"]
                    myIndex = result["myIndex"]
                    case["metadata"][metaSignal] = np.insert(case["metadata"][metaSignal], myIndex, [(pos - sizeX)/250, pos/250, (pos + sizeX)/250], axis=0)
                return result["msg"]
        else:
            return "Can't add ROIs outside of graph."

    @staticmethod
    def _addMinMaxCircleROIs(rawSignal, metaSignal, case, pos, sizeX):
        rawSignalList = case["data"][rawSignal]
        metaSignalList = case["metadata"][metaSignal]*250
        delay = case["metadata"]["t_CO2"]
        if (
            (pos - 2*sizeX >= 0.0 and not np.isnan(rawSignalList[int(np.round(pos - 2*sizeX))])) and 
            (pos + 2*sizeX <= len(rawSignalList) and not np.isnan(rawSignalList[int(np.ceil(pos + 2*sizeX))]))
            ):
            #Check for empty list since this requires special attention, i.e. initiating list.
            if len(metaSignalList) == 0:
                case["metadata"][metaSignal] = np.empty([1, 2])
                case["metadata"][metaSignal][0] = (pos-sizeX)/250 - delay
                case["metadata"][metaSignal][-1] = (pos+sizeX)/250 - delay
                return "Roi Successfully added!"
            else:
                result = AddROI._calculatePosition(rawSignalList, metaSignalList, pos, sizeX)
                if "pos" in result and "myIndex" in result:
                    pos = result["pos"]
                    myIndex = result["myIndex"]
                    case["metadata"][metaSignal] = np.insert(case["metadata"][metaSignal], myIndex, [(pos - sizeX)/250 - delay, (pos + sizeX)/250 - delay], axis=0)
                return result["msg"]
        else:
            return "Can't add ROIs outside of graph."

    @staticmethod
    def _calculatePosition(rawSignalList, metaSignalList, pos, sizeX):
        leftBorder = None
        rightBorder = None
        myIndex = None
        
        #Am I first?
        if pos <= metaSignalList[0][0]:
            leftBorder = 0.0
            rightBorder = metaSignalList[0][0]
            myIndex = 0
        #Am I last?
        elif pos >= metaSignalList[-1][-1]:
            leftBorder = metaSignalList[-1][-1]
            rightBorder = len(rawSignalList)
            myIndex = len(metaSignalList)
        #If there's only one point in metadata list, we can't iterate through the for loop below. 
        elif len(metaSignalList) == 1:
            if pos < metaSignalList[0][0]:
                leftBorder = 0.0
                rightBorder = metaSignalList[0][0]
                myIndex = 0
            if pos > metaSignalList[0][-1]:
                leftBorder = metaSignalList[0][-1]
                rightBorder = len(rawSignalList)
                myIndex = 1
            else:
                return { "msg": "Cannot add ROI on top of another one." }
        else:
            for i in range(len(metaSignalList)):
                if pos >= metaSignalList[i][0] and pos <= metaSignalList[i][-1]:
                    #MinMaxROIs don't have RegionROIs, thus click-event can occur between min and max points.
                    return { "msg": "Cannot add ROI on top of another one." }
                #Check for space between any two Regions of Interests.
                if pos > metaSignalList[i][-1] and pos < metaSignalList[i + 1][0]:
                    if pos - 2*sizeX >= metaSignalList[i][-1] and pos + 2*sizeX <= metaSignalList[i + 1][0]:
                        leftBorder = metaSignalList[i][-1]
                        rightBorder = metaSignalList[i + 1][0]
                        myIndex = i + 1
                        break
                    else:
                        return { "msg": "Not enough space between existing ROIs. Try zooming in or resizing existing ROIs." }   
        if leftBorder == None or rightBorder == None or myIndex == None:
                return { "msg": "Something went wrong" }
            
        if pos - 2*sizeX < leftBorder:
            pos += abs(pos - 2*sizeX - leftBorder)
        if pos + 2*sizeX > rightBorder:
            pos -= abs(pos + 2*sizeX - rightBorder)
        
        return { "msg": "Roi successfully added!", "pos": pos, "myIndex": myIndex }