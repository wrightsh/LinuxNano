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
    
    def setModel(self, value):
        super().setModel(value)
        self.__setupGUI()
       
    def getModel(self):
        return self.model()

    def __setupGUI(self):
        header = self.horizontalHeader()
        
        for column in range(header.count()):
            header.setSectionResizeMode(column, QtWidgets.QHeaderView.ResizeToContents)
       
        for row in range(1, self.model().rowCount()):
            if self.model().isUsedColumn():
                self.openPersistentEditor(self.model().index(row, self.model().isUsedColumn())) #This I think bases the editor on the datatype 

        font = QtGui.QFont("Helvetica", 14)
        self.setFont(font)


    def addBit(self):
        self.model().setNumberOfBits(self.model().numberOfBits() + 1)
        self.__setupGUI()


    def removeBit(self):
        self.model().setNumberOfBits(self.model().numberOfBits() - 1)
        self.__setupGUI()
      

    def contextMenuEvent(self, event):
        if self.selectionModel().selection().indexes():
 
            menu = QtWidgets.QMenu(self)
            
            if self.model().numberOfBits() < 4:
                menu.addAction(self.menu_add_bit)
            
            if self.model().numberOfBits() > 1:
                menu.addAction(self.menu_remove_bit)
           
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






