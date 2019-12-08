# -*- coding: utf-8 -*-
from PyQt5 import QtGui, QtCore, QtSvg, QtWidgets
from linuxnano.strings import strings
import xml.etree.ElementTree as ET

class DeviceIconWidget(QtWidgets.QWidget):
    def __init__(self, svg, selection_call=None, index=None):
        super().__init__()

        self._svg = svg
        self._selection_call = selection_call
        self._index = index
        self._layer = ''
        self._hovering      = False
        self._selected      = False

        #Set the layer to the first one as default
        xml = ET.parse(self._svg)
        svg = xml.getroot()
        self._layer = svg[0].attrib['id']

    def paintEvent(self, event):
        painter  = QtGui.QPainter(self)
        painter.begin(self)
        renderer = QtSvg.QSvgRenderer(self._svg)
        bounding_rect = renderer.boundsOnElement(self._layer)

        #painter.fillRect(event.rect(), QtGui.QBrush(QtCore.Qt.blue))
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        self.setGeometry(0,0,bounding_rect.width(), bounding_rect.height())
        renderer.render(painter, self._layer, bounding_rect)

        if self._hovering:
            painter.setPen(QtGui.QPen(QtGui.QBrush(QtCore.Qt.cyan), 4, QtCore.Qt.DotLine))
            painter.drawRect(bounding_rect)

        if self._selected:
            painter.setPen(QtGui.QPen(QtGui.QBrush(QtCore.Qt.cyan), 4, QtCore.Qt.SolidLine))
            painter.drawRect(bounding_rect)

        painter.end()
        event.accept()

    def mouseDoubleClickEvent(self, event):
        event.accept()

    def mouseReleaseEvent(self, event):
        self.setSelected()
        self._selection_call(self._index)
        event.accept()

    def mousePressEvent(self, event):
        event.accept()

    def setSelected(self):
        self._selected = True
        self.update()#self.repaint()

    def clearSelected(self):
        self._selected = False
        self.repaint()

    def enterEvent(self, event):
        self._hovering = True
        self.update()#self.repaint()
        event.accept()

    def leaveEvent(self, event):
        self._hovering = False
        self.update()#self.repaint()
        event.accept()

    def getLayer(self):
        return self._layer

    def setLayer(self, new_layer):
        self._layer = new_layer
        self.repaint()
    layer = QtCore.pyqtProperty('QString',fget=getLayer, fset=setLayer)
