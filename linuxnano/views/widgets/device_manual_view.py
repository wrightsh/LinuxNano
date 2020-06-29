#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtCore import pyqtProperty
from linuxnano.strings import strings
import subprocess

manual_device_view_base, manual_device_view_form = uic.loadUiType("linuxnano/views/DeviceManualView.ui")


class DeviceManualView(manual_device_view_base, manual_device_view_form):
    def __init__(self, parent=None):
        super(manual_device_view_base, self).__init__()
        self.setupUi(self)

        self._model = None
        self._mapper = QtWidgets.QDataWidgetMapper()

    def setSelection(self, index):
        self._sub_mappers = []

        #Clear out the layout with the Hal Nodes
        for i in reversed(range(self.ui_wids.count())):
            wid = self.ui_wids.takeAt(i).widget()
            if wid is not None:
                wid.deleteLater()

        if hasattr(index.model(), 'mapToSource'):
            index = index.model().mapToSource(index)

        node = index.internalPointer()
        if node is not None:
            typeInfo = node.typeInfo()

        parent_index = index.parent()
        self._mapper.setRootIndex(parent_index)
        self._mapper.setCurrentModelIndex(index)


        #Look for any BoolVarNode or FloatVarNodes
        for row in range(self._model.rowCount(index)):
            child_index = index.child(row,0)
            wid = None

            node =  child_index.internalPointer()

            if node.typeInfo() in [strings.D_IN_NODE, strings.D_OUT_NODE]:
                wid = ManualBoolView()

            elif node.typeInfo() in [strings.A_IN_NODE, strings.A_OUT_NODE]:
                wid = ManualFloatView()

            elif node.typeInfo() == strings.BOOL_VAR_NODE:
                if node.allowManual:
                    wid = ManualBoolSet()
                else:
                    wid = ManualBoolView()

            if wid is not None:
                wid.setModel(child_index.model())
                wid.setRootIndex(index)
                wid.setCurrentModelIndex(child_index)
                self.ui_wids.addWidget(wid)

        self.ui_wids.addStretch(1)

    def setModel(self, model):
        if hasattr(model, 'mapToSource'):
            model = model.sourceModel()
        self._model = model

        self._mapper.setModel(model)
        self._mapper.addMapping(self.ui_name,              0, bytes("text",'ascii'))
        self._mapper.addMapping(self.ui_description,       2, bytes("text",'ascii'))
        self._mapper.addMapping(self.ui_status,           10, bytes("text",'ascii'))

    def model(self):
        return self._model



class ManualBoolView(QtWidgets.QWidget):
    #Format: "Name : value"
    def __init__(self):
        super().__init__()
        self.mapper = QtWidgets.QDataWidgetMapper()
        hbox = QtWidgets.QHBoxLayout()
        self.setLayout(hbox)

        self.ui_name = QtWidgets.QLabel('unknown')
        self.ui_val = QtWidgets.QLabel('?')

        hbox.addWidget(self.ui_name)
        hbox.addWidget(QtWidgets.QLabel(': '))
        hbox.addWidget(self.ui_val)
        hbox.addStretch(1)

    def setRootIndex(self, index):
        self.mapper.setRootIndex(index)

    def setCurrentModelIndex(self, index):
        self.mapper.setCurrentModelIndex(index)
        node = index.internalPointer()

        #These aren't updating a lot so they can just be set
        self.ui_name.setText(str(node.name))

    def setModel(self, model):
        if hasattr(model, 'sourceModel'):model = model.sourceModel()
        self.mapper.setModel(model)
        self.mapper.addMapping(self.ui_val , 21, bytes("text",'ascii'))


class ManualFloatView(QtWidgets.QWidget):
    #Format: "Name : value units"
    def __init__(self):
        super().__init__()
        self.mapper = QtWidgets.QDataWidgetMapper()

        hbox = QtWidgets.QHBoxLayout()
        self.setLayout(hbox)

        self._val = 0
        self._display_digits = 3
        self._display_scientific = False

        self.ui_name = QtWidgets.QLabel('unknown')
        self.ui_val = QtWidgets.QLabel('?')
        self.ui_units = QtWidgets.QLabel('')

        hbox.addWidget(self.ui_name)
        hbox.addWidget(QtWidgets.QLabel(': '))
        hbox.addWidget(self.ui_val)
        hbox.addWidget(self.ui_units)
        hbox.addStretch(1)

    def setRootIndex(self, index):
        self.mapper.setRootIndex(index)

    def setCurrentModelIndex(self, index):
        self.mapper.setCurrentModelIndex(index)
        node = index.internalPointer()

        #These aren't updating a lot so they can just be set
        self.ui_name.setText(str(node.name))
        self.ui_units.setText(str(node.units))
        self._display_digits = index.internalPointer().displayDigits
        self._display_scientific = index.internalPointer().displayScientific

    @pyqtProperty(QtCore.QVariant)
    def val(self): return self._val

    @val.setter
    def val(self, value):
        try:
            self._val = value

            if self._display_scientific:
                txt = "%.*e"%(self._display_digits, self._val)
            else:
                txt = "%0.*f"%(self._display_digits, self._val)

            self.ui_val.setText(txt)

        except:
            self.ui_val.setText('')

    def setModel(self, model):
        if hasattr(model, 'sourceModel'):model = model.sourceModel()
        self.mapper.setModel(model)
        self.mapper.addMapping(self, 21, bytes('val','ascii')) #Only one mapping of 'self' allowed per mapper









class ManualBoolSet(QtWidgets.QWidget):
    #Format "Name : bnt_off btn_on", buttons get grayed out if they aren't allowed
    def __init__(self):
        super().__init__()
        self.mapper = QtWidgets.QDataWidgetMapper()
        hbox = QtWidgets.QHBoxLayout(self)
        self.setLayout(hbox)

        self.ui_name = QtWidgets.QLabel('unknown')

        self.btn_group = QtWidgets.QButtonGroup()
        self.btn_group.setExclusive(True)
        self.btn_group.buttonClicked.connect(self.onClicked)

        self.ui_btn1 = QtWidgets.QPushButton('?', self)
        self.ui_btn2 = QtWidgets.QPushButton('?', self)
        self.ui_btn1.setCheckable(True)
        self.ui_btn2.setCheckable(True)

        self.btn_group.addButton(self.ui_btn1)
        self.btn_group.addButton(self.ui_btn2)

        hbox.addWidget(self.ui_name)
        hbox.addWidget(QtWidgets.QLabel(': '))
        hbox.addWidget(self.ui_btn1)
        hbox.addWidget(self.ui_btn2)
        hbox.addStretch(1)

    def setRootIndex(self, index):
        self.mapper.setRootIndex(index)

    def setCurrentModelIndex(self, index):
        self.mapper.setCurrentModelIndex(index)
        node = index.internalPointer()

        #These aren't updating a lot so they can just be set
        self.ui_name.setText(str(node.name))
        self.ui_btn1.setText(str(node.offName))
        self.ui_btn2.setText(str(node.onName))

    def onClicked(self, btn):
        if self.via_value_setter:
            self.via_value_setter = False
            return

        state = self.btn_group.checkedId()
        self._node.manualQueuePut(state)

    @QtCore.pyqtProperty(int)
    def value(self):
        return self.btn_group.checkedId()

    @value.setter
    def value(self, value):
        if self.btn_group.checkedId() != value and value is not None:
            self.via_value_setter = True
            #this is needed until we change to using the hal streamer incase the outputs dont switch fast enough
            if self.btn_group.button(value) is not None:
                self.btn_group.button(value).click()

    @QtCore.pyqtProperty(int)
    def interlock(self):
        pass
        #return self._interlock

    @interlock.setter
    def interlock(self, value):
        print("interlock_setter")
        try:
            for btn in self.btn_group.buttons():
                if (value>>self.btn_group.id(btn))&1 != 0:
                #if value & self.btn_group.id(btn):
                    btn.setEnabled(True)
                else:
                    btn.setEnabled(False)
        except:
            print("exception!")

    def setModel(self, model):
        if hasattr(model, 'sourceModel'):model = model.sourceModel()
        self.mapper.setModel(model)
        #self.mapper.addMapping(self.name_label, 0, bytes("text",'ascii'))
        #self.mapper.addMapping(self, 22, bytes('interlock','ascii'))
        #self.mapper.addMapping(self, 20, bytes('value','ascii')) #FIXME no idea why this breaks if I change the order of the addMapping


class ManualFloatSet(QtWidgets.QWidget):
    '''Each analog output node is shown as a row
       Format: "Name : value units"  '''
    def __init__(self):
        super().__init__()
        self.mapper = QtWidgets.QDataWidgetMapper()
        hbox = QtWidgets.QHBoxLayout()
        self.setLayout(hbox)

        #QtWidgets.QLabel(item['name'] +"    -    " + "{:10.1f}".format(tmp_val ) + " " +item['units']))
        self.name_label = QtWidgets.QLabel('unknown_name')
        self.value = QtWidgets.QSpinBox()
        self.units_label = QtWidgets.QLabel('unknown_units')
        hbox.addWidget(self.name_label)
        hbox.addWidget(QtWidgets.QLabel(': '))
        hbox.addWidget(self.value)
        hbox.addWidget(self.units_label)
        hbox.addStretch(1)

    def setRootIndex(self, index):
        self.mapper.setRootIndex(index)

    def setCurrentModelIndex(self, index):
        self.mapper.setCurrentModelIndex(index)

    def setModel(self, model):
        if hasattr(model, 'sourceModel'):model = model.sourceModel()
        self.mapper.setModel(model)
        self.mapper.addMapping(self.name_label, 0, bytes("text",'ascii'))
        self.mapper.addMapping(self.value, 30)# bytes("text",'ascii'))
        self.mapper.addMapping(self.units_label, 22, bytes("text",'ascii'))
