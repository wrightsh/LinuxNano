#!/usr/bin/python3
# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtGui, QtWidgets
from linuxnano.digital_state_table_model import DigitalStateTableModel
from linuxnano.analog_state_table_model import AnalogStateTableModel
from linuxnano.views.widgets.scientific_spin import ScientificDoubleSpinBox

import linuxnano.strings
import sys

class DigitalStateTableView(QtWidgets.QTableView):
    """Table view of possible states of digital input"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.menu_add_bit    = "Add bit"
        self.menu_remove_bit = "Remove bit"

        self.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContents)
        self.horizontalHeader().setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.horizontalHeader().customContextMenuRequested.connect(self.halPinMenu)
        font = QtGui.QFont("Helvetica", 14)
        self.setFont(font)

    def setModel(self, value):
        super().setModel(value)
        self.__setupGUI()

    def getModel(self):
        return self.model()

    def __setupGUI(self):
        for row in range(1, self.model().rowCount()):
            if self.model().isUsedColumn():
                self.openPersistentEditor(self.model().index(row, self.model().isUsedColumn()))

        header = self.horizontalHeader()
        for section in range(header.count()):
            header.setSectionResizeMode(section, QtWidgets.QHeaderView.ResizeToContents)

    def addBit(self):
        self.model().setNumberOfBits(self.model().numberOfBits() + 1)
        self.__setupGUI()

    def removeBit(self):
        self.model().setNumberOfBits(self.model().numberOfBits() - 1)
        self.__setupGUI()

    def setHalPin(self, bit, text):
        self.model().setHalPin(bit, text)
        self.__setupGUI()

    def halPinMenu(self, pos):
        col = self.horizontalHeader().logicalIndexAt(pos)

        if col < self.model().numberOfBits():
            bit = self.model().bitAtColumn(col)

            menu = QtWidgets.QMenu()

            for value in self.model().allowedHalPins():
                menu.addAction(value)

            action = menu.exec_(self.mapToGlobal(pos))
            if action is not None:
                self.model().setHalPin(bit, action.text())

            self.__setupGUI()


    def generateContextMenu(self):
        menu = QtWidgets.QMenu(self)

        if self.model().numberOfBits() < 4:
            menu.addAction(self.menu_add_bit)

        if self.model().numberOfBits() > 1:
            menu.addAction(self.menu_remove_bit)

        return menu


    def contextMenuEvent(self, event):
        menu = self.generateContextMenu()
        action = menu.exec_(self.mapToGlobal(event.pos()))

        if action is not None:
            if   action.text() == self.menu_add_bit    : self.addBit()
            elif action.text() == self.menu_remove_bit : self.removeBit()


    digitalStateTableView = QtCore.pyqtProperty(type(DigitalStateTableModel()), getModel, setModel)


class AnalogStateTableView(QtWidgets.QTableView):
    """Table view of possible states of digital input"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.menu_add_state    = "Add state"
        self.menu_remove_state = "Remove state"

        item_delegate = ValidatedDelegate()
        self.setItemDelegate(item_delegate)

        self.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContents)

        #item_delegate = ValidatedItemDelegate()
        #item_delegate=QtWidgets.QStyledItemDelegate()
        #item_delegate.setItemEditorFactory(ItemEditorFactory())


    def setModel(self, value):
        super().setModel(value)
        self.__setupGUI()

    def getModel(self):
        return self.model()

    def __setupGUI(self):
        header = self.horizontalHeader()

        for column in range(header.count()):
            header.setSectionResizeMode(column, QtWidgets.QHeaderView.ResizeToContents)


        self.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers  |
                             QtWidgets.QAbstractItemView.DoubleClicked   |
                             QtWidgets.QAbstractItemView.SelectedClicked)

        font = QtGui.QFont("Helvetica", 14)
        self.setFont(font)


    def addState(self):
        self.model().setNumberOfStates(self.model().numberOfStates() + 1)
        self.__setupGUI()


    def removeState(self):
        self.model().setNumberOfStates(self.model().numberOfStates() - 1)
        self.__setupGUI()


    def contextMenuEvent(self, event):
        if self.selectionModel().selection().indexes():

            menu = QtWidgets.QMenu(self)

            if self.model().numberOfStates() < 4:
                menu.addAction(self.menu_add_state)

            if self.model().numberOfStates() > 1:
                menu.addAction(self.menu_remove_state)

            action = menu.exec_(self.mapToGlobal(event.pos()))

            if action is not None:
                if   action.text() == self.menu_add_state    : self.addState()
                elif action.text() == self.menu_remove_state : self.removeState()


    analogStateTableView = QtCore.pyqtProperty(type(AnalogStateTableModel()), getModel, setModel)


class ValidatedDelegate(QtWidgets.QStyledItemDelegate):
    def __init__(self, parent=None):
        super().__init__(parent)

    def createEditor(self, parent, option, index):
        if not index.isValid():
            return 0

        if index.column() == 1:
            scienceSpinBox = ScientificDoubleSpinBox(parent)
            #scienceSpinBox.editingFinished.connect(self.checkInput)
            return scienceSpinBox

        return super().createEditor(parent, option, index)

class HorizontalHeader(QtWidgets.QHeaderView):
    def __init__(self, values, parent=None):
        super(HorizontalHeader, self).__init__(QtCore.Qt.Horizontal, parent)
        self.setSectionsMovable(True)
        self.comboboxes = []
        self.sectionResized.connect(self.handleSectionResized)
        self.sectionMoved.connect(self.handleSectionMoved)

    def showEvent(self, event):
        for i in range(self.count()):
            if i < len(self.comboboxes):
                combo = self.comboboxes[i]
                combo.clear()
                combo.addItems(["Variable", "Timestamp"])
            else:
                combo = QtWidgets.QComboBox(self)
                combo.addItems(["Variable", "Timestamp"])
                self.comboboxes.append(combo)

            combo.setGeometry(self.sectionViewportPosition(i), 0, self.sectionSize(i)-4, self.height())
            combo.show()

        if len(self.comboboxes) > self.count():
            for i in range(self.count(), len(self.comboboxes)):
                self.comboboxes[i].deleteLater()

        super(HorizontalHeader, self).showEvent(event)

    def handleSectionResized(self, i):
        for i in range(self.count()):
            j = self.visualIndex(i)
            logical = self.logicalIndex(j)
            self.comboboxes[i].setGeometry(self.sectionViewportPosition(logical), 0, self.sectionSize(logical)-4, self.height())

    def handleSectionMoved(self, i, oldVisualIndex, newVisualIndex):
        for i in range(min(oldVisualIndex, newVisualIndex), self.count()):
            logical = self.logicalIndex(i)
            self.comboboxes[i].setGeometry(self.ectionViewportPosition(logical), 0, self.sectionSize(logical) - 5, height())

    def fixComboPositions(self):
        for i in range(self.count()):
            self.comboboxes[i].setGeometry(self.sectionViewportPosition(i), 0, self.sectionSize(i) - 5, self.height())
#class HorizontalHeader(QtWidgets.QHeaderView):
#    def __init__(self, values, parent=None):
#        super(HorizontalHeader, self).__init__(QtCore.Qt.Horizontal, parent)
#        self.setSectionsMovable(True)
#        self._bits = 1
#
#        #self.sectionResized.connect(self.handleSectionResized)
#        #self.sectionMoved.connect(self.handleSectionMoved)
#
#        self.comboboxes = []
#        for i in range(self._bits):
#            combo = QtWidgets.QComboBox(self)
#            combo.addItems(hardware.D_IN_PINS.names)
#            self.comboboxes.append(combo)
#
#
#    def addBit(self):
#        pass
#        self._bits += 1
#    def removeBit(self):
#        pass
#        self._bits -= 1
#
#    def showEvent(self, event):
#        for i in range(self._bits):
#            #if i < len(self.comboboxes):
#            #    combo = self.comboboxes[i]
#            #    combo.clear()
#            #    combo.addItems(hardware.D_IN_PINS.names)
#            #else:
#            #    combo = QtWidgets.QComboBox(self)
#            #    combo.addItems(hardware.D_IN_PINS.names)
#            #    self.comboboxes.append(combo)
#
#            self.comboboxes[i].setGeometry(self.sectionViewportPosition(i), 0, self.sectionSize(i)-4, self.height())
#            self.comboboxes[i].show()
#
#        #if len(self.comboboxes) > self.count():
#        #    for i in range(self.count(), len(self.comboboxes)):
#        #        self.comboboxes[i].deleteLater()
#
#        super(HorizontalHeader, self).showEvent(event)
#
#    def handleSectionResized(self, i):
#        for i in range(self._bits):
#        #for i in range(self.count()):
#            j = self.visualIndex(i)
#            logical = self.logicalIndex(j)
#            self.comboboxes[i].setGeometry(self.sectionViewportPosition(logical), 0, self.sectionSize(logical)-4, self.height())
#
#    def handleSectionMoved(self, i, oldVisualIndex, newVisualIndex):
#        #for i in range(min(oldVisualIndex, newVisualIndex), self.count()):
#        for i in range(min(oldVisualIndex, newVisualIndex), self._bits):
#            logical = self.logicalIndex(i)
#            self.comboboxes[i].setGeometry(self.ectionViewportPosition(logical), 0, self.sectionSize(logical) - 5, height())
##
#    def fixComboPositions(self):
#        #for i in range(self.count()):
#        for i in range(self._bits):
#            self.comboboxes[i].setGeometry(self.sectionViewportPosition(i), 0, self.sectionSize(i) - 5, self.height())
