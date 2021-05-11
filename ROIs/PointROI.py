import pyqtgraph as pg
import numpy as np

from PyQt5 import QtCore as qtc

class PointROI(pg.EllipseROI):
    r"""
    Circular ROI subclass. Behaves exactly as EllipseROI, but may only be scaled
    proportionally to maintain its aspect ratio.
    
    ============== =============================================================
    **Arguments**
    pos            (length-2 sequence) The position of the ROI's origin.
    size           (length-2 sequence) The size of the ROI's bounding rectangle.
    \**args        All extra keyword arguments are passed to ROI()
    ============== =============================================================
    
    """
    #Override signals
    sigRegionChangeFinished = qtc.pyqtSignal(int, float, float)
    sigHoverEvent = qtc.pyqtSignal(bool)
    sigRemoveRequested = qtc.Signal(int)

    caseArray = None
    index = None
    maxBounds = None
    
    def __init__(self, caseArray, index, viewRange, pos, size=None, radius=None, delay=0.0, **args):
        if size is None:
            if radius is None:
                raise TypeError("Must provide either size or radius.")
            size = (radius*2, radius*2)
        self.caseArray = caseArray
        self.index = index
        self.delay = delay
        
        pg.EllipseROI.__init__(self, pos, size, resizable=False, rotatable=False, **args)
        self.aspectLocked = True
        self.maxBounds = {}
        self.maxBounds["left"] = viewRange[0][0] if viewRange[0][0] > caseArray[index][0]*250 else caseArray[index][0]*250
        self.maxBounds["right"] = viewRange[0][1] if viewRange[0][1] < caseArray[index][-1]*250 else caseArray[index][-1]*250
        self.maxBounds["bottom"] = viewRange[1][0]
        self.maxBounds["top"] = viewRange[1][1]
    
    #Override methods
    def _addHandles(self):
        pass

    def translate(self, *args, **kargs):
        """
        Move the ROI to a new position.
        Accepts either (x, y, snap) or ([x,y], snap) as arguments
        If the ROI is bounded and the move would exceed boundaries, then the ROI
        is moved to the nearest acceptable position instead.
        
        *snap* can be:
        
        =============== ==========================================================================
        None (default)  use self.translateSnap and self.snapSize to determine whether/how to snap
        False           do not snap
        Point(w,h)      snap to rectangular grid with spacing (w,h)
        True            snap using self.snapSize (and ignoring self.translateSnap)
        =============== ==========================================================================
           
        Also accepts *update* and *finish* arguments (see setPos() for a description of these).
        """

        if len(args) == 1:
            pt = args[0]
        else:
            pt = args
            
        newState = self.stateCopy()
        newState['pos'] = newState['pos'] + pt
        
        snap = kargs.get('snap', None)
        if snap is None:
            snap = self.translateSnap
        if snap is not False:
            newState['pos'] = self.getSnapPosition(newState['pos'], snap=snap)
        
        if self.maxBounds is not None:
            r = self.stateRect(newState)
            d = pg.Point(0,0)
            offsetX = 0.5*self.getState()["size"].x()
            offsetY = 0.5*self.getState()["size"].y()
            if self.maxBounds["left"] > r.left() + offsetX:
                d[0] = self.maxBounds["left"] - r.left() + offsetX
            elif self.maxBounds["right"] < r.right() - offsetX:
                d[0] = self.maxBounds["right"] - r.right() - offsetX
            if self.maxBounds["top"] < r.top() - offsetY:
                d[1] = self.maxBounds["top"] - r.top() - offsetY
            elif self.maxBounds["bottom"] > r.bottom() + offsetY:
                d[1] = self.maxBounds["bottom"] - r.bottom() + offsetY
            newState['pos'] += d
        
        update = kargs.get('update', True)
        finish = kargs.get('finish', True)
        self.setPos(newState['pos'], update=update, finish=finish)

    def stateChangeFinished(self):
        self.sigRegionChangeFinished.emit(self.index, self.getState()["pos"].x() - self.delay, self.getState()["size"].x())

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

    def _emitRemoveRequest(self):
        self.sigRemoveRequested.emit(self.index)