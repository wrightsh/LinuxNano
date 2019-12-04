# -*- coding: utf-8 -*-
from PyQt5 import QtGui, QtCore, QtSvg, QtWidgets
import strings


class DeviceIconWidget(QtWidgets.QWidget):
    def __init__(self,  svg):
        super().__init__(parent)

        self._svg = svg
        self._layer = ''
        self._hovering      = False
        self._selected      = False


        #self._index = index
        #icon_node   = index.internalPointer()
        #self._svg_file = icon_node.iconSVG

        #self._layers          = ['normal', 'normal-selected'] #QtCore.QLatin1String('normal')

        #self._current_state = 0
        #self._layer = self._layers[self._current_state]
        #self._hovering      = False
        #self._selected      = False


    #TODO do we need a new painter and renderer each time?
    def paintEvent(self, event):
        painter  = QtGui.QPainter(self)
        renderer = QtSvg.QSvgRenderer(self._svg)
        bounding_rect = renderer.boundsOnElement(self._layer)

        painter.fillRect(event.rect(), QtGui.QBrush(QtCore.Qt.blue))
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        self.setGeometry(0,0,bounding_rect.width(), bounding_rect.height())
        renderer.render(painter, self._layer, bounding_rect)

        if self._hovering:
            painter.setPen(QtGui.QPen(QtGui.QBrush(QtCore.Qt.cyan), 4, QtCore.Qt.DotLine))
            painter.drawRect(bounding_rect)

        if self._selected:
            painter.setPen(QtGui.QPen(QtGui.QBrush(QtCore.Qt.cyan), 4, QtCore.Qt.SolidLine))
            painter.drawRect(bounding_rect)

        event.accept()

    def mouseDoubleClickEvent(self, event):
        print('double click event')
        event.accept()

    def mouseReleaseEvent(self, event):
        print('mouse release event')
        event.accept()

    def mousePressEvent(self, event):
        print('it was clicked so send that signal to the parent')
        event.accept()

    def setSelected(self):
        self._selected = True
        self.repaint()

    def clearSelected(self):
        self._selected = False
        self.repaint()

    def enterEvent(self, event):
        self._hovering = True
        print('entered bounding box')
        self.repaint()
        event.accept()

    def leaveEvent(self, event):
        self._hovering = False
        print('leave bounding box')
        self.repaint()
        event.accept()

    def getLayer(self):
        return self._layer

    def setLayer(self, new_layer):
        self._layer = new_layer
        self.repaint()

    current_state = QtCore.pyqtProperty(int,fget=getLyaer, fset=setLayer)

    #def getCurrentState(self):
    #    print('in deep  ', str(self._current_state))
    #    return self._current_state
#
    #def setCurrentState(self, new_state):
    #    self._current_state = new_state
    #    self._current_layer = self._layers[self._current_state]
    #    self.repaint()
#
#
    #current_state = QtCore.pyqtProperty(int,fget=getCurrentState, fset=setCurrentState)
