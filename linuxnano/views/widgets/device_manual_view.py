#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtGui, QtWidgets, uic
from linuxnano.strings import col, typ
from linuxnano.views.widgets.scientific_spin import ScientificDoubleSpinBox

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
        try:
            for row in range(self._model.rowCount(index)):
                child_index = index.child(row,0)
                wid = None

                node =  child_index.internalPointer()

                #A user never directly sets IO
                if node.typeInfo() in [typ.D_IN_NODE, typ.D_OUT_NODE]:
                    wid = ManualBoolView()

                elif node.typeInfo() in [typ.A_IN_NODE, typ.A_OUT_NODE]:
                    wid = ManualFloatView()

                elif node.typeInfo() == typ.BOOL_VAR_NODE:
                    wid = ManualBoolView() if node.viewOnly else ManualBoolSet()

                elif node.typeInfo() == typ.FLOAT_VAR_NODE:
                    wid = ManualFloatView() if node.viewOnly else ManualFloatSet()

                if wid is not None:
                    wid.setModel(child_index.model())
                    wid.setRootIndex(index)
                    wid.setCurrentModelIndex(child_index)
                    self.ui_wids.addWidget(wid)
        except:
            pass

        self.ui_wids.addStretch(1)

    def setModel(self, model):
        if hasattr(model, 'mapToSource'):
            model = model.sourceModel()
        self._model = model

        self._mapper.setModel(model)
        self._mapper.addMapping(self.ui_name, col.NAME, bytes("text",'ascii'))
        self._mapper.addMapping(self.ui_description, col.DESCRIPTION, bytes("text",'ascii'))
        self._mapper.addMapping(self.ui_status, col.STATUS, bytes("text",'ascii'))

    def model(self):
        return self._model



class ManualBoolView(QtWidgets.QWidget):
    #Format: "Name : value"
    def __init__(self):
        super().__init__()
        self.mapper = QtWidgets.QDataWidgetMapper()
        hbox = QtWidgets.QHBoxLayout()
        self.setLayout(hbox)

        self._val = False
        self.ui_name = QtWidgets.QLabel('unknown')
        self.ui_val = QtWidgets.QLabel('?')
        self._off_name = ""
        self._on_name = ""

        hbox.addWidget(self.ui_name)
        hbox.addWidget(QtWidgets.QLabel(': '))
        hbox.addWidget(self.ui_val)
        hbox.addStretch(1)

    def setRootIndex(self, index):
        self.mapper.setRootIndex(index)

    def setCurrentModelIndex(self, index):
        self.mapper.setCurrentModelIndex(index)
        node = index.internalPointer()

        #These aren't changing often so they can just be set
        self.ui_name.setText(str(node.name))
        self._off_name = node.offName
        self._on_name = node.onName

        txt = self._on_name if node.value() else self._off_name
        self.ui_val.setText(txt)


    @QtCore.pyqtProperty(int)
    def value(self):
        return self._val

    @value.setter
    def value(self, value):
        self._val = value
        txt = self._on_name if value else self._off_name
        self.ui_val.setText(txt)

    def setModel(self, model):
        if hasattr(model, 'sourceModel'):model = model.sourceModel()
        self.mapper.setModel(model)
        self.mapper.addMapping(self, col.VALUE, bytes('value','ascii'))


class ManualBoolSet(QtWidgets.QWidget):
    #Format "Name : bnt_off btn_on", buttons get grayed out if enable_manual isn't true
    def __init__(self):
        super().__init__()
        self.mapper_1 = QtWidgets.QDataWidgetMapper()
        self.mapper_2 = QtWidgets.QDataWidgetMapper()

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

        self.btn_group.addButton(self.ui_btn1, 0)
        self.btn_group.addButton(self.ui_btn2, 1)

        hbox.addWidget(self.ui_name)
        hbox.addWidget(QtWidgets.QLabel(': '))
        hbox.addWidget(self.ui_btn1)
        hbox.addWidget(self.ui_btn2)
        hbox.addStretch(1)

        self.via_this_button = False
        self.btn_group.buttonClicked.connect(self.mapper_1.submit)
        self.mapper_1.currentIndexChanged.connect(self.mapper_2.setCurrentIndex)


    def setRootIndex(self, index):
        self.mapper_1.setRootIndex(index)
        self.mapper_2.setRootIndex(index)

    def setCurrentModelIndex(self, index):
        self.mapper_1.setCurrentModelIndex(index)
        self.mapper_2.setCurrentModelIndex(index)

        node = index.internalPointer()

        #These aren't changing often so they can just be set
        self.ui_name.setText(str(node.name))
        self.ui_btn1.setText(str(node.offName))
        self.ui_btn2.setText(str(node.onName))

    def onClicked(self, btn):
        self.via_this_button = True
        self.value = self.btn_group.checkedId()

    @QtCore.pyqtProperty(int)
    def value(self):
        return self.btn_group.checkedId()

    @value.setter
    def value(self, value):
        if not self.via_this_button:
            if value:
                self.ui_btn2.setChecked(True)
            else:
                self.ui_btn1.setChecked(True)

        self.via_this_button = False

    @QtCore.pyqtProperty(int)
    def enableManual(self):
        return self.ui_btn1.isEnabled()

    @enableManual.setter
    def enableManual(self, value):
        if value:
            self.ui_btn1.setEnabled(True)
            self.ui_btn2.setEnabled(True)
        else:
            self.ui_btn1.setEnabled(False)
            self.ui_btn2.setEnabled(False)

    def setModel(self, model):
        if hasattr(model, 'sourceModel'):model = model.sourceModel()
        self.mapper_1.setModel(model)
        self.mapper_2.setModel(model)

        self.mapper_1.addMapping(self, col.VALUE, bytes('value','ascii'))
        self.mapper_2.addMapping(self, col.ENABLE_MANUAL, bytes('enableManual','ascii'))


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

        #These aren't changing often so they can just be set
        self.ui_name.setText(str(node.name))
        self.ui_units.setText(str(node.units))
        self._display_digits = index.internalPointer().displayDigits
        self._display_scientific = index.internalPointer().displayScientific

    @QtCore.pyqtProperty(float)
    def val(self):
        return self._val

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
        self.mapper.addMapping(self, col.VALUE, bytes('val','ascii')) #Only one mapping of 'self' allowed per mapper


#TODO I think I need to add digits and scientific logic to this
class ManualFloatSet(QtWidgets.QWidget):
    #Format: "Name : value units"
    def __init__(self):
        super().__init__()
        self.mapper = QtWidgets.QDataWidgetMapper()
        self.mapper = QtWidgets.QDataWidgetMapper()

        hbox = QtWidgets.QHBoxLayout()
        self.setLayout(hbox)

        self.ui_name = QtWidgets.QLabel('unknown')
        self.ui_value = ScientificDoubleSpinBox()
        self.ui_units = QtWidgets.QLabel('units')
        hbox.addWidget(self.ui_name)
        hbox.addWidget(QtWidgets.QLabel(': '))
        hbox.addWidget(self.ui_value)
        hbox.addWidget(self.ui_units)
        hbox.addStretch(1)

    def setRootIndex(self, index):
        self.mapper.setRootIndex(index)

    def setCurrentModelIndex(self, index):
        self.mapper.setCurrentModelIndex(index)

        #These aren't changing often so they can just be set
        node = index.internalPointer()
        self.ui_name.setText(str(node.name))
        self.ui_units.setText(str(node.units))

    @QtCore.pyqtProperty(int)
    def enableManual(self):
        return self.ui_value.isEnabled()

    @enableManual.setter
    def enableManual(self, value):
        if value:
            self.ui_value.setEnabled(True)
        else:
            self.ui_value.setEnabled(False)

    def setModel(self, model):
        if hasattr(model, 'sourceModel'):model = model.sourceModel()
        self.mapper.setModel(model)

        self.mapper.addMapping(self.ui_value, col.VALUE)# bytes("text",'ascii'))
        self.mapper.addMapping(self, col.ENABLE_MANUAL, bytes('enableManual','ascii'))
