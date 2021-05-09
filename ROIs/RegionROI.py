import pyqtgraph as pg
import numpy as np

from PyQt5 import QtCore as qtc
from PyQt5 import QtGui as qtg

class RegionROI(pg.ROI):
    r"""
    Rectangular ROI subclass with scale-rotate handles on either side. This
    allows the ROI to be positioned as if moving the ends of a line segment.
    A third handle controls the width of the ROI orthogonal to its "line" axis.
    
    ============== =============================================================
    **Arguments**
    pos1           (length-2 sequence) The position of the center of the ROI's
                   left edge.
    pos2           (length-2 sequence) The position of the center of the ROI's
                   right edge.
    width          (float) The width of the ROI.
    \**args        All extra keyword arguments are passed to ROI()
    ============== =============================================================
    
    """
    sigRegionChangeFinished = qtc.pyqtSignal(int, float, float)
    sigHoverEvent = qtc.pyqtSignal(bool)
    sigRemoveRequested = qtc.Signal(int)

    caseArray = None
    index = None
    leftBounds = None
    rightBounds = None
    viewRange = None

    def __init__(self, pos1, pos2, width, myPointROISizeX, caseArray, index, viewRange, **args):
        self.caseArray = caseArray
        self.index = index
        self.leftBounds = {}
        self.rightBounds = {}
        self.viewRange = viewRange

        if index == 0:
            self.leftBounds["left"] = self.viewRange[0][0]
        else:
            self.leftBounds["left"] = self.viewRange[0][0] if self.viewRange[0][0] > caseArray[index - 1][2]*250 else caseArray[index - 1][2]*250
        self.leftBounds["right"] = self.viewRange[0][1] if self.viewRange[0][1] < caseArray[index][1]*250 else caseArray[index][1]*250
        if index == len(caseArray) - 1:
            self.rightBounds["right"] = self.viewRange[0][1]
        else:
            self.rightBounds["right"] = self.viewRange[0][1] if self.viewRange[0][1] < caseArray[index + 1][0]*250 else caseArray[index + 1][0]*250
        self.rightBounds["left"] = self.viewRange[0][0] if self.viewRange[0][0] > caseArray[index][1]*250 else caseArray[index][1]*250
        
        self.leftBounds["left"] += myPointROISizeX
        self.leftBounds["right"] -= myPointROISizeX
        self.rightBounds["left"] += myPointROISizeX
        self.rightBounds["right"] -= myPointROISizeX

        pos1 = pg.Point(pos1)
        pos2 = pg.Point(pos2)
        d = pos2-pos1
        l = d.length()
        ang = pg.Point(1, 0).angle(d)
        ra = ang * np.pi / 180.
        c = pg.Point(-width/2. * np.sin(ra), -width/2. * np.cos(ra))
        pos1 = pos1 + c
        
        pg.ROI.__init__(self, pos1, size=pg.Point(l, width), angle=ang, rotatable=False, resizable=False, removable=True, **args)
        self.addScaleRotateHandle([0, 0.5], [1, 0.5])
        self.addScaleRotateHandle([1, 0.5], [0, 0.5])

    def movePoint(self, handle, pos, modifiers=qtc.Qt.KeyboardModifiers(0), finish=True, coords='parent'):
        ## called by Handles when they are moved. 
        ## pos is the new position of the handle in scene coords, as requested by the handle.
        newState = self.stateCopy()
        index = self.indexOfHandle(handle)
        h = self.handles[index]

        p0 = self.mapToParent(h['pos'] * self.state['size'])
        p1 = pg.Point(pos)
        
        if coords == 'parent':
            pass
        elif coords == 'scene':
            p1 = self.mapSceneToParent(p1)
        else:
            raise Exception("New point location must be given in either 'parent' or 'scene' coordinates.")

        ## Handles with a 'center' need to know their local position relative to the center point (lp0, lp1)
        if 'center' in h:
            c = h['center']
            cs = c * self.state['size']
            lp0 = self.mapFromParent(p0) - cs
            lp1 = self.mapFromParent(p1) - cs
        
        if h['type'] == 't':
            snap = True if (modifiers & qtc.Qt.ControlModifier) else None
            self.translate(p1-p0, snap=snap, update=False)
        
        elif h['type'] == 'f':
            newPos = self.mapFromParent(p1)
            h['item'].setPos(newPos)
            h['pos'] = newPos
            self.freeHandleMoved = True
            
        elif h['type'] == 's':
            ## If a handle and its center have the same x or y value, we can't scale across that axis.
            if h['center'][0] == h['pos'][0]:
                lp1[0] = 0
            if h['center'][1] == h['pos'][1]:
                lp1[1] = 0
            
            ## snap 
            if self.scaleSnap or (modifiers & qtc.Qt.ControlModifier):
                lp1[0] = round(lp1[0] / self.scaleSnapSize) * self.scaleSnapSize
                lp1[1] = round(lp1[1] / self.scaleSnapSize) * self.scaleSnapSize
                
            ## preserve aspect ratio (this can override snapping)
            if h['lockAspect'] or (modifiers & qtc.Qt.AltModifier):
                #arv = Point(self.preMoveState['size']) - 
                lp1 = lp1.proj(lp0)
            
            ## determine scale factors and new size of ROI
            hs = h['pos'] - c
            if hs[0] == 0:
                hs[0] = 1
            if hs[1] == 0:
                hs[1] = 1
            newSize = lp1 / hs
            
            ## Perform some corrections and limit checks
            if newSize[0] == 0:
                newSize[0] = newState['size'][0]
            if newSize[1] == 0:
                newSize[1] = newState['size'][1]
            if not self.invertible:
                if newSize[0] < 0:
                    newSize[0] = newState['size'][0]
                if newSize[1] < 0:
                    newSize[1] = newState['size'][1]
            if self.aspectLocked:
                newSize[0] = newSize[1]
            
            ## Move ROI so the center point occupies the same scene location after the scale
            s0 = c * self.state['size']
            s1 = c * newSize
            cc = self.mapToParent(s0 - s1) - self.mapToParent(pg.Point(0, 0))
            
            ## update state, do more boundary checks
            newState['size'] = newSize
            newState['pos'] = newState['pos'] + cc
            if self.maxBounds is not None:
                r = self.stateRect(newState)
                if not self.maxBounds.contains(r):
                    return
            
            self.setPos(newState['pos'], update=False)
            self.setSize(newState['size'], update=False)
        
        elif h['type'] in ['r', 'rf']:
            if h['type'] == 'rf':
                self.freeHandleMoved = True
            
            if not self.rotatable:
                return
            ## If the handle is directly over its center point, we can't compute an angle.
            try:
                if lp1.length() == 0 or lp0.length() == 0:
                    return
            except OverflowError:
                return
            
            ## determine new rotation angle, constrained if necessary
            ang = newState['angle'] - lp0.angle(lp1)
            if ang is None:  ## this should never happen..
                return
            if self.rotateSnap or (modifiers & qtc.Qt.ControlModifier):
                ang = round(ang / self.rotateSnapAngle) * self.rotateSnapAngle
            
            ## create rotation transform
            tr = qtg.QTransform()
            tr.rotate(ang)
            
            ## move ROI so that center point remains stationary after rotate
            cc = self.mapToParent(cs) - (tr.map(cs) + self.state['pos'])
            newState['angle'] = ang
            newState['pos'] = newState['pos'] + cc
            
            ## check boundaries, update
            if self.maxBounds is not None:
                r = self.stateRect(newState)
                if not self.maxBounds.contains(r):
                    return
            self.setPos(newState['pos'], update=False)
            self.setAngle(ang, update=False)
            
            ## If this is a free-rotate handle, its distance from the center may change.
         
            if h['type'] == 'rf':
                h['item'].setPos(self.mapFromScene(p1))  ## changes ROI coordinates of handle
                h['pos'] = self.mapFromParent(p1)
                
        elif h['type'] == 'sr':
            try:
                if lp1.length() == 0 or lp0.length() == 0:
                    return
            except OverflowError:
                return

            ang = 0.0 #We don't wish changes to the angle.
            if ang is None:
                return
            if self.rotateSnap or (modifiers & qtc.Qt.ControlModifier):
                ang = round(ang / self.rotateSnapAngle) * self.rotateSnapAngle

            if self.aspectLocked or h['center'][0] != h['pos'][0]:
                newState['size'][0] = self.state['size'][0] * lp1.length() / lp0.length()
                if self.scaleSnap:  # use CTRL only for angular snap here.
                    newState['size'][0] = round(newState['size'][0] / self.snapSize) * self.snapSize

            if self.aspectLocked or h['center'][1] != h['pos'][1]:
                newState['size'][1] = self.state['size'][1] * lp1.length() / lp0.length()
                if self.scaleSnap:  # use CTRL only for angular snap here.
                    newState['size'][1] = round(newState['size'][1] / self.snapSize) * self.snapSize

            if newState['size'][0] == 0:
                newState['size'][0] = 1
            if newState['size'][1] == 0:
                newState['size'][1] = 1

            c1 = c * newState['size']
            tr = qtg.QTransform()
            tr.rotate(ang)
            
            cc = self.mapToParent(cs) - (tr.map(c1) + self.state['pos'])
            newState['angle'] = ang
            cc.setY(0.0)#We don't wish to move the region along the y-axis.

            newState['pos'] = newState['pos'] + cc
            if self.maxBounds is not None:
                r = self.stateRect(newState)
                if not self.maxBounds.contains(r):
                    return
            
            #Posisjonene må ikke overlappe med toppunkt eller naboregioner.
            if index == 0: #Venstre handle
                horizontalBounds = self.leftBounds
                if newState["pos"].x() < horizontalBounds["left"]:
                    diff = newState["pos"].x() - horizontalBounds["left"]
                    newState["size"].setX(newState["size"].x() + diff)
                    newState["pos"].setX(newState["pos"].x() - diff)
                if newState["pos"].x() > horizontalBounds["right"]:
                    diff = newState["pos"].x() - horizontalBounds["right"]
                    newState["size"].setX(newState["size"].x() + diff)
                    newState["pos"].setX(newState["pos"].x() - diff)  
            else:
                horizontalBounds = self.rightBounds
                if newState["pos"].x() + newState["size"].x() < horizontalBounds["left"]:
                    diff = newState["pos"].x() + newState["size"].x() - horizontalBounds["left"]
                    newState["size"].setX(newState["size"].x() - diff)
                if newState["pos"].x() + newState["size"].x() > horizontalBounds["right"]:
                    diff = newState["pos"].x() + newState["size"].x() - horizontalBounds["right"]
                    newState["size"].setX(newState["size"].x() - diff)

            self.setState(newState, update=False)

        self.stateChanged(finish=finish)

    def _emitRemoveRequest(self):
        self.sigRemoveRequested.emit(self.index)

    def stateChangeFinished(self):
        self.sigRegionChangeFinished.emit(self.index, self.getState()["pos"].x(), self.getState()["size"].x())

    def hoverEvent(self, ev):
        hover = False
        if not ev.isExit():
            if self.translatable and ev.acceptDrags(qtc.Qt.LeftButton):
                hover=True
                
            for btn in [qtc.Qt.LeftButton, qtc.Qt.RightButton, qtc.Qt.MiddleButton]:
                if (self.acceptedMouseButtons() & btn) and ev.acceptClicks(btn):
                    hover=True
            if self.contextMenuEnabled():
                ev.acceptClicks(qtc.Qt.RightButton)
                
        if hover:
            self.setMouseHover(True)
            ev.acceptClicks(qtc.Qt.LeftButton)  ## If the ROI is hilighted, we should accept all clicks to avoid confusion.
            ev.acceptClicks(qtc.Qt.RightButton)
            ev.acceptClicks(qtc.Qt.MiddleButton)
            self.sigHoverEvent.emit(True)
        else:
            self.setMouseHover(False)
            self.sigHoverEvent.emit(False)

    def translate(self, *args, **kargs):
        pass