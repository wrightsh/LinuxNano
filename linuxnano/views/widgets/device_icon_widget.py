# -*- coding: utf-8 -*-
from PyQt5 import QtGui, QtCore, QtSvg, QtWidgets
from linuxnano.strings import strings
import xml.etree.ElementTree as ET



class DeviceIconWidget(QtSvg.QGraphicsSvgItem):
    def __init__(self, renderer=None):
        super().__init__()

        if renderer is not None:
            self.setSharedRenderer(renderer)
        self.setAcceptHoverEvents(True)
        #self.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable, True)

        self._callback = None #This method gets called on click to make the parents tree change index
        self._index = None #index of the device that owns this icon

        self._hovering = False
        self._selected = False

    def setCallback(self, value):
        self._callback = value

    def setIndex(self, value):
        self._index = value

    def paint(self, painter, option, wid):
        super().paint(painter, option, wid)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)

        if self._hovering:
            painter.setPen(QtGui.QPen(QtGui.QBrush(QtCore.Qt.cyan), 4, QtCore.Qt.DotLine))
            painter.drawRect(self.boundingRect())

        if self._selected:
            painter.setPen(QtGui.QPen(QtGui.QBrush(QtCore.Qt.cyan), 4, QtCore.Qt.SolidLine))
            painter.drawRect(self.boundingRect())

    def mouseReleaseEvent(self, event):
        self._callback(self._index)
        event.accept()

    #mouseReleaseEvent needs this
    def mousePressEvent(self, event):
        event.accept()

    def setSelected(self):
        self._selected = True
        self.update()

    def clearSelected(self):
        self._selected = False
        self.update()

    def hoverEnterEvent(self, event):
        self._hovering = True
        self.update()
        event.accept()

    def hoverLeaveEvent(self, event):
        self._hovering = False
        self.update()
        event.accept()
