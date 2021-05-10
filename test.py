	def _snapRoiIntoValidPosition(self, movement, metaData, rawData, pos, size):
		if abs(movement["leftBorder"]) > abs(movement["rightBorder"]):
			if movement["leftBorder"] > 0.0:
				return [0, self._myIterator(pos, len(rawData) - 1, 1, rawData)]
			elif movement["leftBorder"] < 0.0:
				return [0, self._myIterator(pos, -1, -1, rawData)]
		else:
			if movement["rightBorder"] > 0.0:
				return [-1, self._myIterator(pos+size, len(rawData) - 1, 1, rawData)]
			elif movement["rightBorder"] < 0.0:
				return [-1, self._myIterator(pos+size, -1, -1, rawData)]
				
	def _myIterator(self, pos, startIndex, iteration, rawData):
		for i in range(int(np.round(pos)), startIndex, iteration):
			if not np.isnan(rawData[i]):
				return i/250

@qtc.pyqtSlot(int, float, float, str, int)
	def _ROImoved(self, index, pos, size, signal, value):
		msg = "ROI has been moved successfully."
		metaData = self.case["metadata"][signal][index]
		rawData = self.case["data"][self.name]

		if Utility.isList(value):
			if np.isnan(rawData[int(np.round(pos))]) or np.isnan(rawData[int(np.round(pos+size))]):
				#What's moved? Values are being multiplied/divided by frequency, this might result in inaccuracy.
				#Thus we have to check for biggest movement.
				movement = {
					"leftBorder": metaData[value[0]]*250 - pos,#Positive value: movement to the left.
					"rightBorder": metaData[value[1]]*250 - (pos+size)#Negative value: movement to the right.
				}
				#Left RegionROI's handle moved/left MinMaxCircleROI moved.
				result = self._snapRoiIntoValidPosition(movement, metaData, rawData, pos, size)
				self.case["metadata"][signal][index][result[0]] = result[1]/250
			else:
				self.case["metadata"][signal][index][value[0]] = pos/250  
				self.case["metadata"][signal][index][value[1]] = (pos + size)/250
		else:
			if np.isnan(rawData[int(np.round(pos+(0.5*size)))]):
				msg = "Cannot move ROI outside the graph."
			elif pos/250 <= metaData[0] or pos/250 >= metaData[-1]:
				msg = "Cannot move CircleROI outside its RegionROI."
			else:
				self.case["metadata"][signal][index][value] = (pos + 0.5*size)/250
		self._emitRoiMessage(msg)
		self._blockPlotting(False)
		self.replot()
