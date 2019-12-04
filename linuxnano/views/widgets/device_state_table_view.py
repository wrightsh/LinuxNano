#!/usr/bin/python3
# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtGui, QtWidgets
from linuxnano.device_state_table_model import DeviceStateTableModel
from linuxnano.views.widgets.scientific_spin import ScientificDoubleSpinBox


class DeviceStateTableView(QtWidgets.QTableView):
    """Possible states/combinations? of a device"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContents)

        self._item_delegate = ValidatedDelegate(self, self.model)
        self.setItemDelegate(self._item_delegate)


    def setModel(self, value):
        super().setModel(value)
        self.__setupGUI()

    def getModel(self):
        return self.model()
   
    def setIconLayerList(self, value):
        self._item_delegate.setIconLayerList(value.names) 


    def __setupGUI(self):
        header = self.horizontalHeader()
        
        for column in range(header.count()):
            header.setSectionResizeMode(column, QtWidgets.QHeaderView.ResizeToContents)
       

        for row in range(0, self.model().rowCount()):
            self.openPersistentEditor(self.model().index(row, self.model().isWarningColumn())) 
            self.openPersistentEditor(self.model().index(row, self.model().isAlarmColumn())) 
            self.openPersistentEditor(self.model().index(row, self.model().triggersActionColumn())) 
            self.openPersistentEditor(self.model().index(row, self.model().logEntranceColumn())) 
            


        font = QtGui.QFont("Helvetica", 14)
        self.setFont(font)



    deviceStateTableView = QtCore.pyqtProperty(type(DeviceStateTableModel()), getModel, setModel)



#FIXME can we move the columns into the init?
class ValidatedDelegate(QtWidgets.QStyledItemDelegate):
    def __init__(self, parent=None, model=None):
        super().__init__(parent)
        self._table_model = model
        self._icon_layer_list = ['']
   
    def setIconLayerList(self, icon_layer_list = ['']):
        self._icon_layer_list = icon_layer_list

    def createEditor(self, parent, option, index):
        if not index.isValid():
            return #FIXME was return 0, that throws errows
        

        if self._table_model is not None:
            if index.column() == self._table_model().iconLayerColumn():
                c = QtWidgets.QComboBox(parent)
                c.addItems(self._icon_layer_list)
                return c
                

        return super().createEditor(parent, option, index)





