# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtGui, uic, QtWidgets
import os

from linuxnano.views.widgets.tool_tree_view import ToolTreeView
from linuxnano.tool_model import LeafFilterProxyModel

from linuxnano.strings import col, typ

d_in_base,  d_in_form  = uic.loadUiType("linuxnano/views/DigitalInputEditor.ui")
d_out_base, d_out_form = uic.loadUiType("linuxnano/views/DigitalOutputEditor.ui")

a_in_base,  a_in_form  = uic.loadUiType("linuxnano/views/AnalogInputEditor.ui")
a_out_base, a_out_form = uic.loadUiType("linuxnano/views/AnalogOutputEditor.ui")

bool_var_base,  bool_var_form  = uic.loadUiType("linuxnano/views/BoolVarEditor.ui")
float_var_base, float_var_form = uic.loadUiType("linuxnano/views/FloatVarEditor.ui")

device_icon_base, device_icon_form  = uic.loadUiType("linuxnano/views/DeviceIconEditor.ui")
device_base, device_form  = uic.loadUiType("linuxnano/views/DeviceEditor.ui")
system_base, system_form  = uic.loadUiType("linuxnano/views/SystemEditor.ui")
node_base, node_form  = uic.loadUiType("linuxnano/views/NodeEditor.ui")

tool_editor_base, tool_editor_form  = uic.loadUiType("linuxnano/views/ToolEditor.ui")


class ToolEditor(tool_editor_base, tool_editor_form):
    def __init__(self, parent=None):
        super(tool_editor_base, self).__init__(parent)
        self.setupUi(self)

        #The node editor is common for every node in a tool
        self._node_editor = NodeEditor(self)
        self.ui_common_box.addWidget(self._node_editor)

        #Only one of these is shown at a time
        self._specific_editors = { typ.SYSTEM_NODE      : SystemEditor(self),
                                   typ.DEVICE_NODE      : DeviceEditor(self),
                                   typ.DEVICE_ICON_NODE : DeviceIconEditor(self),
                                   typ.D_IN_NODE        : DigitalInputEditor(self),
                                   typ.D_OUT_NODE       : DigitalOutputEditor(self),
                                   typ.A_IN_NODE        : AnalogInputEditor(self),
                                   typ.A_OUT_NODE       : AnalogOutputEditor(self),
                                   typ.BOOL_VAR_NODE    : BoolVarEditor(self),
                                   typ.FLOAT_VAR_NODE   : FloatVarEditor(self) }

        for editor in self._specific_editors.values():
            self.ui_specific_box.addWidget(editor)

        self.hideEditors()
        self.ui_splitter.setSizes([self.width()*0.6, self.width()*0.4])


    def hideEditors(self):
        for editor in self._specific_editors.values():
            editor.setVisible(False)


    """INPUTS: QModelIndex, QModelIndex"""
    def setSelection(self, current, old):
        model = current.model()

        if hasattr(model, 'mapToSource') : current_index = model.mapToSource(current)
        else                             : current_index = current

        node = current_index.internalPointer()
        self.hideEditors()

        # Always set it for the common parts to the node
        if node is not None:
            self._node_editor.setSelection(current_index)
            typeInfo = node.typeInfo()

            if typeInfo in self._specific_editors:
                self._specific_editors[typeInfo].setSelection(current_index)
                self._specific_editors[typeInfo].setVisible(True)


    def setModel(self, model):
        self._model = model
        self._proxy_model =  LeafFilterProxyModel(self) #maybe not self?

        """VIEW <------> PROXY MODEL <------> DATA MODEL"""
        self._proxy_model.setSourceModel(self._model)
        self._proxy_model.setDynamicSortFilter(True)
        self._proxy_model.setFilterCaseSensitivity(QtCore.Qt.CaseInsensitive)

        self.ui_tree.setModel(self._proxy_model) #maybe not self?)
        self.ui_filter.textChanged.connect(self._proxy_model.setFilterRegExp)
        self.ui_tree.selectionModel().currentChanged.connect(self.setSelection)#self._property_editor.setSelection)
        self.ui_tree.setColumnWidth(0,200)

        self._node_editor.setModel(self._proxy_model)

        for editor in self._specific_editors.values():
            editor.setModel(self._proxy_model)



class NodeEditor(node_base, node_form):
    def __init__(self, parent=None):
        super(node_base, self).__init__(parent)
        self.setupUi(self)
        self.mapper = QtWidgets.QDataWidgetMapper()

    def setModel(self, model):
        if hasattr(model, 'sourceModel'):
            model = model.sourceModel()

        self.mapper.setModel(model)
        self.mapper.addMapping(self.ui_name       , col.NAME)
        self.mapper.addMapping(self.ui_type       , col.TYPE_INFO)
        self.mapper.addMapping(self.ui_description, col.DESCRIPTION)


    def setSelection(self, current):
        parent = current.parent()
        self.mapper.setRootIndex(parent)
        self.mapper.setCurrentModelIndex(current)


class SystemEditor(system_base, system_form):
    file_signal = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super(system_base, self).__init__(parent)
        self.setupUi(self)
        self.mapper = QtWidgets.QDataWidgetMapper()

        #Background SVG file selection
        self.file_signal.connect(self.mapper.submit)
        self.ui_select_image.clicked.connect(self.selectSVG)
        self.ui_background_svg.textChanged.connect(lambda update_system_svg: self.ui_svg_widget.load(self.ui_background_svg.text()))

    def setModel(self, model):
        if hasattr(model, 'sourceModel'):
            model = model.sourceModel()

        self.mapper.setModel(model)
        self.mapper.addMapping(self.ui_background_svg, col.SVG)


    def setSelection(self, current):
        parent = current.parent()
        self.mapper.setRootIndex(parent)
        self.mapper.setCurrentModelIndex(current)


    def selectSVG(self,sender):
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog

        file_name = QtWidgets.QFileDialog.getOpenFileName(self,"QFileDialog.getOpenFileName()", "linuxnano/resources/icons","SVG (*.svg);;All Files (*)", options=options)
        file_name = file_name[0]

        if isinstance(file_name, str) and os.path.isfile(file_name):
            self.ui_background_svg.setText(file_name)
            self.file_signal.emit()
        else:
            pass


class DeviceEditor(device_base, device_form):
    def __init__(self, parent=None):
        super(device_base, self).__init__(parent)
        self.setupUi(self)
        self.mapper = QtWidgets.QDataWidgetMapper()

    def setModel(self, model):
        if hasattr(model, 'sourceModel'):
            model = model.sourceModel()

        self.mapper.setModel(model)
        self.mapper.addMapping(self.ui_status, col.STATUS)

    def setSelection(self, current):
        parent = current.parent()
        self.mapper.setRootIndex(parent)
        self.mapper.setCurrentModelIndex(current)


class DeviceIconEditor(device_icon_base, device_icon_form):
    file_signal = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super(device_icon_base, self).__init__(parent)
        self.setupUi(self)
        self.mapper = QtWidgets.QDataWidgetMapper()

        self.file_signal.connect(self.mapper.submit)
        self.ui_select_image.clicked.connect(self.selectSVG)
        self.ui_svg.textChanged.connect(lambda update_system_svg: self.ui_svg_widget.load(self.ui_svg.text()))
        #self.ui_svg_widget.load(self.ui_svg.text())


    def setModel(self, model):
        if hasattr(model, 'sourceModel'):
            model = model.sourceModel()
        self.mapper.setModel(model)

        self.mapper.addMapping(self.ui_svg      , col.SVG)
        #self_mapper.addMapping(self.ui_layer   , col.LAYER)
        self.mapper.addMapping(self.ui_x        , col.X)
        self.mapper.addMapping(self.ui_y        , col.Y)
        self.mapper.addMapping(self.ui_scale    , col.SCALE)
        self.mapper.addMapping(self.ui_rotation , col.ROTATION)

        self.mapper.addMapping(self.ui_has_text , col.HAS_TEXT)
        self.mapper.addMapping(self.ui_text     , col.TEXT)
        self.mapper.addMapping(self.ui_text_x   , col.TEXT_X)
        self.mapper.addMapping(self.ui_text_y   , col.TEXT_Y)
        self.mapper.addMapping(self.ui_font_size, col.FONT_SIZE)

        #self.mapper.setSubmitPolicy(QtWidgets.QDataWidgetMapper.ManualSubmit)
        #self.ui_x.valueChanged.connect(self.mapper.submit)
        #self.ui_y.valueChanged.connect(self.mapper.submit)
        #self.ui_scale.valueChanged.connect(self.mapper.submit)
        #self.ui_rotation.valueChanged.connect(self.mapper.submit)
        #self.ui_has_text.stateChanged.connect(self.mapper.submit)
        #self.ui_text_x.valueChanged.connect(self.mapper.submit)
        #self.ui_text_y.valueChanged.connect(self.mapper.submit)
        #self.ui_font_size.valueChanged.connect(self.mapper.submit)


    def setSelection(self, current):
        parent = current.parent()
        self.mapper.setRootIndex(parent)
        self.mapper.setCurrentModelIndex(current)

        #keep for reference
        #self.ui_icon_node_list.clear()
        #number_node_names = current.internalPointer().numberNodes()
        #for name in number_node_names.names:
        #    self.ui_icon_node_list.addItem(name)
        #self.ui_icon_node_list.setCurrentIndex(1)

        #index = self.ui_icon_node_list.findText(current.internalPointer().numberDisplayNodeName(), QtCore.Qt.MatchFixedString)
        #if index >= 0:
        #    self.ui_icon_node_list.setCurrentIndex(index)



    def selectSVG(self,sender):
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog

        file_name = QtWidgets.QFileDialog.getOpenFileName(self,"QFileDialog.getOpenFileName()", "linuxnano/resources/icons","SVG (*.svg);;All Files (*)", options=options)
        file_name = file_name[0]

        if os.path.isfile(file_name):
            self.ui_svg.setText(file_name)
            self.file_signal.emit()
        else:
            pass


class DigitalInputEditor(d_in_base, d_in_form):
    def __init__(self, parent=None):
        super(d_in_base, self).__init__(parent)
        self.setupUi(self)
        self.mapper = QtWidgets.QDataWidgetMapper()

    def setModel(self, model):
        if hasattr(model, 'sourceModel'):
            model = model.sourceModel()

        self.mapper.setModel(model)
        self.mapper.addMapping(self.ui_hal_pin      , col.HAL_PIN,  b"currentIndex") #index of the dropdown item
        self.mapper.addMapping(self.ui_hal_pin_type , col.HAL_PIN_TYPE)
        self.mapper.addMapping(self.ui_value        , col.VALUE)
        self.mapper.addMapping(self.ui_off_name     , col.OFF_NAME)
        self.mapper.addMapping(self.ui_on_name      , col.ON_NAME)

    def setSelection(self, current):
        parent = current.parent()
        self.mapper.setRootIndex(parent)
        self.mapper.setCurrentModelIndex(current)

        self.ui_hal_pin.clear()
        pins = current.internalPointer().halPins()
        for name in pins.names:
            self.ui_hal_pin.addItem(name)

        index = self.ui_hal_pin.findText(current.internalPointer().halPin, QtCore.Qt.MatchFixedString)
        if index >= 0:
            self.ui_hal_pin.setCurrentIndex(index)


class DigitalOutputEditor(d_out_base, d_out_form):
    def __init__(self, parent=None):
        super(d_out_base, self).__init__(parent)
        self.setupUi(self)
        self.mapper = QtWidgets.QDataWidgetMapper()

    def setModel(self, model):
        if hasattr(model, 'sourceModel'):
            model = model.sourceModel()

        self.mapper.setModel(model)
        self.mapper.addMapping(self.ui_hal_pin      , col.HAL_PIN,  b"currentIndex") #index of the dropdown item
        self.mapper.addMapping(self.ui_hal_pin_type , col.HAL_PIN_TYPE)
        self.mapper.addMapping(self.ui_value        , col.VALUE)
        self.mapper.addMapping(self.ui_off_name     , col.OFF_NAME)
        self.mapper.addMapping(self.ui_on_name      , col.ON_NAME)

    def setSelection(self, current):
        parent = current.parent()
        self.mapper.setRootIndex(parent)
        self.mapper.setCurrentModelIndex(current)

        self.ui_hal_pin.clear()
        pins = current.internalPointer().halPins()
        for name in pins.names:
            self.ui_hal_pin.addItem(name)

        index = self.ui_hal_pin.findText(current.internalPointer().halPin, QtCore.Qt.MatchFixedString)
        if index >= 0:
            self.ui_hal_pin.setCurrentIndex(index)



class AnalogInputEditor(a_in_base, a_in_form):
    def __init__(self, parent=None):
        super(a_in_base, self).__init__(parent)
        self.setupUi(self)
        self.mapper = QtWidgets.QDataWidgetMapper()

    def setModel(self, model):
        if hasattr(model, 'sourceModel'):
            model = model.sourceModel()
        self.mapper.setModel(model)

        self.mapper.addMapping(self.ui_hal_pin           , col.HAL_PIN,  b"currentIndex") #index of the dropdown item
        self.mapper.addMapping(self.ui_hal_pin_type      , col.HAL_PIN_TYPE)
        self.mapper.addMapping(self.ui_hal_value         , col.HAL_VALUE)
        self.mapper.addMapping(self.ui_value             , col.VALUE)
        self.mapper.addMapping(self.ui_units             , col.UNITS)
        self.mapper.addMapping(self.ui_display_digits    , col.DISPLAY_DIGITS)
        self.mapper.addMapping(self.ui_display_scientific, col.DISPLAY_SCIENTIFIC)
        self.mapper.addMapping(self.ui_calibration_table , col.CALIBRATION_TABLE_MODEL,  b"calibrationTableView")

    def setSelection(self, current):
        parent = current.parent()
        self.mapper.setRootIndex(parent)
        self.mapper.setCurrentModelIndex(current)

        self.ui_hal_pin.clear()
        pins = current.internalPointer().halPins()
        for name in pins.names:
            self.ui_hal_pin.addItem(name)

        index = self.ui_hal_pin.findText(current.internalPointer().halPin, QtCore.Qt.MatchFixedString)
        if index >= 0:
            self.ui_hal_pin.setCurrentIndex(index)



class AnalogOutputEditor(a_out_base, a_out_form):
    def __init__(self, parent=None):
        super(a_out_base, self).__init__(parent)
        self.setupUi(self)
        self.mapper = QtWidgets.QDataWidgetMapper()

    def setModel(self, model):
        if hasattr(model, 'sourceModel'):
            model = model.sourceModel()
        self.mapper.setModel(model)

        self.mapper.addMapping(self.ui_hal_pin           , col.HAL_PIN,  b"currentIndex") #index of the dropdown item
        self.mapper.addMapping(self.ui_hal_pin_type      , col.HAL_PIN_TYPE)
        self.mapper.addMapping(self.ui_hal_value         , col.HAL_VALUE)
        self.mapper.addMapping(self.ui_value             , col.VALUE)
        self.mapper.addMapping(self.ui_units             , col.UNITS)
        self.mapper.addMapping(self.ui_display_digits    , col.DISPLAY_DIGITS)
        self.mapper.addMapping(self.ui_display_scientific, col.DISPLAY_SCIENTIFIC)
        self.mapper.addMapping(self.ui_calibration_table , col.CALIBRATION_TABLE_MODEL,  b"calibrationTableView")

    def setSelection(self, current):
        parent = current.parent()
        self.mapper.setRootIndex(parent)
        self.mapper.setCurrentModelIndex(current)

        self.ui_hal_pin.clear()
        pins = current.internalPointer().halPins()
        for name in pins.names:
            self.ui_hal_pin.addItem(name)

        index = self.ui_hal_pin.findText(current.internalPointer().halPin, QtCore.Qt.MatchFixedString)
        if index >= 0:
            self.ui_hal_pin.setCurrentIndex(index)




class BoolVarEditor(bool_var_base, bool_var_form):
    def __init__(self, parent=None):
        super(bool_var_base, self).__init__(parent)
        self.setupUi(self)
        self.mapper = QtWidgets.QDataWidgetMapper()

    def setModel(self, model):
        if hasattr(model, 'sourceModel'):
            model = model.sourceModel()
        self.mapper.setModel(model)

        self.mapper.addMapping(self.ui_value        , col.VALUE)
        self.mapper.addMapping(self.ui_off_name     , col.OFF_NAME)
        self.mapper.addMapping(self.ui_on_name      , col.ON_NAME)
        self.mapper.addMapping(self.ui_enable_manual, col.ENABLE_MANUAL)
        self.mapper.addMapping(self.ui_view_only    , col.VIEW_ONLY)

    def setSelection(self, current):
        parent = current.parent()
        self.mapper.setRootIndex(parent)
        self.mapper.setCurrentModelIndex(current)


class FloatVarEditor(float_var_base, float_var_form):
    def __init__(self, parent=None):
        super(float_var_base, self).__init__(parent)
        self.setupUi(self)
        self.mapper = QtWidgets.QDataWidgetMapper()

    def setModel(self, model):
        if hasattr(model, 'sourceModel'):
            model = model.sourceModel()
        self.mapper.setModel(model)

        self.mapper.addMapping(self.ui_value             , col.VALUE)
        self.mapper.addMapping(self.ui_min               , col.MIN)
        self.mapper.addMapping(self.ui_max               , col.MAX)
        self.mapper.addMapping(self.ui_units             , col.UNITS)
        self.mapper.addMapping(self.ui_display_digits    , col.DISPLAY_DIGITS)
        self.mapper.addMapping(self.ui_display_scientific, col.DISPLAY_SCIENTIFIC)
        self.mapper.addMapping(self.ui_enable_manual     , col.ENABLE_MANUAL)
        self.mapper.addMapping(self.ui_view_only         , col.VIEW_ONLY)



    def setSelection(self, current):
        parent = current.parent()
        self.mapper.setRootIndex(parent)
        self.mapper.setCurrentModelIndex(current)
