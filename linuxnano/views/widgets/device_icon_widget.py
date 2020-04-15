# -*- coding: utf-8 -*-
from PyQt5 import QtGui, QtCore, QtSvg, QtWidgets
from linuxnano.strings import strings
import xml.etree.ElementTree as ET

class DeviceIconWidget(QtWidgets.QWidget):
    def __init__(self, icon_svg=None):
        super().__init__()

        self._callback = None #This method gets called on click to make the parents tree change index
        self._index = None #index of the device that owns this icon

        self._svg = 'linuxnano/resources/icons/general/unknown.svg'
        self._layer = ''
        self._hovering = False
        self._selected = False

        if icon_svg is not None:
            self.setIcon(icon_svg)

    def setCallback(self, value):
        self._callback = value

    def setIndex(self, value):
        self._index = value

    def setIcon(self, value):
        try:
            self._svg = value

            xml = ET.parse(self._svg)
            svg = xml.getroot()
            self._layer = svg[0].attrib['id']
        except:
            self._svg = 'linuxnano/resources/icons/general/unknown.svg'
            xml = ET.parse(self._svg)
            svg = xml.getroot()
            self._layer = svg[0].attrib['id']

            raise ValueError("Invalid SVG")


    def paintEvent(self, event):
        painter  = QtGui.QPainter(self)
        #painter.begin(self)
        renderer = QtSvg.QSvgRenderer(self._svg)
        bounding_rect = renderer.boundsOnElement(self._layer)

        #painter.fillRect(event.rect(), QtGui.QBrush(QtCore.Qt.blue))
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        self.setGeometry(0, 0, bounding_rect.width(), bounding_rect.height())
        renderer.render(painter, self._layer, bounding_rect)

        if self._hovering:
            painter.setPen(QtGui.QPen(QtGui.QBrush(QtCore.Qt.cyan), 4, QtCore.Qt.DotLine))
            painter.drawRect(bounding_rect)

        if self._selected:
            painter.setPen(QtGui.QPen(QtGui.QBrush(QtCore.Qt.cyan), 4, QtCore.Qt.SolidLine))
            painter.drawRect(bounding_rect)

        #painter.end()
        event.accept()

    def mouseDoubleClickEvent(self, event):
        event.accept()

    def mouseReleaseEvent(self, event):
        self._callback(self._index)
        event.accept()

    def mousePressEvent(self, event):
        event.accept()

    def setSelected(self):
        self._selected = True
        self.update()

    def clearSelected(self):
        self._selected = False
        self.repaint()

    def enterEvent(self, event):
        self._hovering = True
        self.update()
        event.accept()

    def leaveEvent(self, event):
        self._hovering = False
        self.update()
        event.accept()

    @QtCore.pyqtProperty(str)
    def layer(self):
        return self._layer

    @layer.setter
    def layer(self, new_layer):
        self._layer = new_layer
        self.repaint()

    #def getLayer(self):
    #    return self._layer
    #def setLayer(self, new_layer):
    #    self._layer = new_layer
    #    self.repaint()
    #layer = QtCore.pyqtProperty('QString',fget=getLayer, fset=setLayer)
