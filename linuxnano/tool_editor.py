# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtGui, uic, QtWidgets
import os

from linuxnano.views.widgets.state_table_views import DigitalStateTableView
from linuxnano.views.widgets.tool_tree_view import ToolTreeView
from linuxnano.tool_model import LeafFilterProxyModel

from linuxnano.strings import strings


d_in_base,  d_in_form  = uic.loadUiType("linuxnano/views/DigitalInputEditor.ui")
d_out_base, d_out_form = uic.loadUiType("linuxnano/views/DigitalOutputEditor.ui")

a_in_base,  a_in_form  = uic.loadUiType("linuxnano/views/AnalogInputEditor.ui")
a_out_base, a_out_form = uic.loadUiType("linuxnano/views/AnalogOutputEditor.ui")

device_icon_base, device_icon_form  = uic.loadUiType("linuxnano/views/DeviceIconEditor.ui")

device_base, device_form  = uic.loadUiType("linuxnano/views/DeviceEditor.ui")
system_base, system_form  = uic.loadUiType("linuxnano/views/SystemEditor.ui")
node_base, node_form  = uic.loadUiType("linuxnano/views/NodeEditor.ui")

tool_editor_base, tool_editor_form  = uic.loadUiType("linuxnano/views/ToolEditor.ui")




class ToolEditor(tool_editor_base, tool_editor_form):
    def __init__(self, model, parent=None):
        super(tool_editor_base, self).__init__(parent)
        self.setupUi(self)

        # Make all the editors
        self._node_editor        = NodeEditor(self)
        self._system_editor      = SystemEditor(self)
        self._device_editor      = DeviceEditor(self)
        self._device_icon_editor = DeviceIconEditor(self)

        self._d_in_editor        = DigitalInputEditor(self)
        self._a_in_editor        = AnalogInputEditor(self)
        self._d_out_editor       = DigitalOutputEditor(self)
        self._a_out_editor       = AnalogOutputEditor(self)


        #Add everything to their layouts
        self.ui_common_box.addWidget(self._node_editor)
        self.ui_specific_box.addWidget(self._system_editor)
        self.ui_specific_box.addWidget(self._device_editor)
        self.ui_specific_box.addWidget(self._device_icon_editor)

        self.ui_specific_box.addWidget(self._d_in_editor)
        self.ui_specific_box.addWidget(self._a_in_editor)
        self.ui_specific_box.addWidget(self._d_out_editor)
        self.ui_specific_box.addWidget(self._a_out_editor)


        self._model = model
        self._proxy_model =  LeafFilterProxyModel(self) #maybe not self?

        """VIEW <------> PROXY MODEL <------> DATA MODEL"""
        self._proxy_model.setSourceModel(self._model)
        self._proxy_model.setDynamicSortFilter(True)
        self._proxy_model.setFilterCaseSensitivity(QtCore.Qt.CaseInsensitive)

        self.ui_tree.setModel(self._proxy_model) #maybe not self?)
        self.ui_filter.textChanged.connect(self._proxy_model.setFilterRegExp)
        self.setModel(self._proxy_model)
        self.ui_tree.selectionModel().currentChanged.connect(self.setSelection)#self._property_editor.setSelection)



        self.hideEditors()
        self.ui_tree.setColumnWidth(0,300)
        self.ui_splitter.setStretchFactor(0, .25)
        self.ui_splitter.setStretchFactor(1, 4)


    def hideEditors(self):
        self._system_editor.setVisible(False)
        self._device_editor.setVisible(False)
        self._device_icon_editor.setVisible(False)

        self._d_in_editor.setVisible(False)
        self._a_in_editor.setVisible(False)
        self._d_out_editor.setVisible(False)
        self._a_out_editor.setVisible(False)



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


        #Set the selection and show the proper editor
        if typeInfo == strings.SYSTEM_NODE:
            self._system_editor.setSelection(current_index)
            self._system_editor.setVisible(True)

        elif typeInfo == strings.DEVICE_NODE:
            self._device_editor.setSelection(current_index)
            self._device_editor.setVisible(True)

        elif typeInfo == strings.DEVICE_ICON_NODE:
            self._device_icon_editor.setSelection(current_index)
            self._device_icon_editor.setVisible(True)

        elif typeInfo == strings.D_IN_NODE:
            self._d_in_editor.setSelection(current_index)
            self._d_in_editor.setVisible(True)

        elif typeInfo == strings.A_IN_NODE:
            self._a_in_editor.setSelection(current_index)
            self._a_in_editor.setVisible(True)

        elif typeInfo == strings.D_OUT_NODE:
            self._d_out_editor.setSelection(current_index)
            self._d_out_editor.setVisible(True)

        elif typeInfo == strings.A_OUT_NODE:
            self._a_out_editor.setVisible(True)
            self._a_out_editor.setSelection(current_index)


    def setModel(self, proxy_model):
        self._proxy_model = proxy_model

        self._node_editor.setModel(self._proxy_model)
        self._system_editor.setModel(self._proxy_model)
        self._device_editor.setModel(self._proxy_model)
        self._device_icon_editor.setModel(self._proxy_model)

        self._d_in_editor.setModel(self._proxy_model)
        self._a_in_editor.setModel(self._proxy_model)
        self._d_out_editor.setModel(self._proxy_model)
        self._a_out_editor.setModel(self._proxy_model)





class NodeEditor(node_base, node_form):
    def __init__(self, parent=None):
        super(node_base, self).__init__(parent)
        self.setupUi(self)
        self._data_mapper = QtWidgets.QDataWidgetMapper()


    def setModel(self, model):
        if hasattr(model, 'sourceModel'):
            model = model.sourceModel()

        self._data_mapper.setModel(model)
        self._data_mapper.addMapping(self.ui_name       , 0)
        self._data_mapper.addMapping(self.ui_type       , 1)
        self._data_mapper.addMapping(self.ui_description, 2)


    def setSelection(self, current):
        parent = current.parent()
        self._data_mapper.setRootIndex(parent)
        self._data_mapper.setCurrentModelIndex(current)


class SystemEditor(system_base, system_form):
    file_signal = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super(system_base, self).__init__(parent)
        self.setupUi(self)
        self._data_mapper = QtWidgets.QDataWidgetMapper()

        self.file_signal.connect(self._data_mapper.submit)
        self.ui_select_image.clicked.connect(self.selectSVG)

        self.ui_background_svg.textChanged.connect(lambda update_system_svg: self.ui_svg_widget.load(self.ui_background_svg.text()))



    def setModel(self, model):
        if hasattr(model, 'sourceModel'):
            model = model.sourceModel()

        self._data_mapper.setModel(model)
        self._data_mapper.addMapping(self.ui_background_svg, 10)


    def setSelection(self, current):
        parent = current.parent()
        self._data_mapper.setRootIndex(parent)
        self._data_mapper.setCurrentModelIndex(current)

    def selectSVG(self,sender):
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog

        file_name = QtWidgets.QFileDialog.getOpenFileName(self,"QFileDialog.getOpenFileName()", "linuxnano/resources/icons","SVG (*.svg);;All Files (*)", options=options)
        file_name = file_name[0]

        if os.path.isfile(file_name):
            self.ui_background_svg.setText(file_name)
            self.file_signal.emit()
        else:
            pass



class DeviceEditor(device_base, device_form):
    def __init__(self, parent=None):
        super(device_base, self).__init__(parent)
        self.setupUi(self)
        self._data_mapper = QtWidgets.QDataWidgetMapper()


    def setModel(self, model):
        if hasattr(model, 'sourceModel'):
            model = model.sourceModel()

        self._data_mapper.setModel(model)
        #self._data_mapper.addMapping(self.ui_status             , 10)
        self._data_mapper.addMapping(self.ui_device_state_table  , 15,  b"deviceStateTableView")


    def setSelection(self, current):
        parent = current.parent()
        self._data_mapper.setRootIndex(parent)
        self._data_mapper.setCurrentModelIndex(current)

        icon_layer_list = current.internalPointer().iconLayerList()
        self.ui_device_state_table.setIconLayerList(icon_layer_list)


class DeviceIconEditor(device_icon_base, device_icon_form):
    file_signal = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super(device_icon_base, self).__init__(parent)
        self.setupUi(self)
        self._data_mapper = QtWidgets.QDataWidgetMapper()

        self.file_signal.connect(self._data_mapper.submit)
        self.ui_select_image.clicked.connect(self.selectSVG)

        self.ui_svg.textChanged.connect(lambda update_system_svg: self.ui_svg_widget.load(self.ui_svg.text()))
        #self.ui_svg_widget.load(self.ui_svg.text())



    def setModel(self, model):
        if hasattr(model, 'sourceModel'):
            model = model.sourceModel()
        self._data_mapper.setModel(model)


        self._data_mapper.addMapping(self.ui_svg             , 10)
        #self._data_mapper.addMapping(self.ui_layer          , 11)
        self._data_mapper.addMapping(self.ui_x               , 14)
        self._data_mapper.addMapping(self.ui_y               , 15)
        self._data_mapper.addMapping(self.ui_scale           , 16)
        self._data_mapper.addMapping(self.ui_rotation        , 17)
        self._data_mapper.addMapping(self.ui_icon_node_list  , 18, b"currentIndex") #This is correct because we use the index of the dropdown item
        self._data_mapper.addMapping(self.ui_number_x        , 19)
        self._data_mapper.addMapping(self.ui_number_y        , 20)
        self._data_mapper.addMapping(self.ui_number_font_size, 21)


    def setSelection(self, current):
        #Number node is for a floating point number next to the icon...

        self.ui_icon_node_list.clear()
        number_node_names = current.internalPointer().numberNodes()

        for name in number_node_names.names:
            self.ui_icon_node_list.addItem(name)

        #TODO - start fixing all of your dropdowns and make them consistent with the enum thing
        self.ui_icon_node_list.setCurrentIndex(1)

        #index = self.ui_icon_node_list.findText(current.internalPointer().numberDisplayNodeName(), QtCore.Qt.MatchFixedString)
        #if index >= 0:
        #    self.ui_icon_node_list.setCurrentIndex(index)

        parent = current.parent()
        self._data_mapper.setRootIndex(parent)
        self._data_mapper.setCurrentModelIndex(current)


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
        self._data_mapper = QtWidgets.QDataWidgetMapper()

    def setModel(self, model):
        if hasattr(model, 'sourceModel'):
            model = model.sourceModel()

        self._data_mapper.setModel(model)
        self._data_mapper.addMapping(self.ui_state_table, 20, b"digitalStateTableView")

    def setSelection(self, current):
        parent = current.parent()

        self._data_mapper.setRootIndex(parent)
        self._data_mapper.setCurrentModelIndex(current)

class DigitalOutputEditor(d_out_base, d_out_form):
    def __init__(self, parent=None):
        super(d_out_base, self).__init__(parent)
        self.setupUi(self)
        self._data_mapper = QtWidgets.QDataWidgetMapper()

        for i in strings.MANUAL_DISPLAY_TYPES.names:
            self.ui_manual_display_type.addItem(i)

    def setModel(self, model):
        if hasattr(model, 'sourceModel'):
            model = model.sourceModel()
        self._data_mapper.setModel(model)

        self._data_mapper.addMapping(self.ui_state_table         , 20,  b"digitalStateTableView")
        self._data_mapper.addMapping(self.ui_manual_display_type , 21,  b"currentIndex") #This is correct because we use the index of the dropdown item

    def setSelection(self, current):
        parent = current.parent()
        self._data_mapper.setRootIndex(parent)
        self._data_mapper.setCurrentModelIndex(current)

class AnalogInputEditor(a_in_base, a_in_form):
    def __init__(self, parent=None):
        super(a_in_base, self).__init__(parent)
        self.setupUi(self)
        self._data_mapper = QtWidgets.QDataWidgetMapper()

        for i in strings.ANALOG_SCALE_TYPES.names:
            self.ui_scale_type.addItem(i)

    def setModel(self, model):
        if hasattr(model, 'sourceModel'):
            model = model.sourceModel()
        self._data_mapper.setModel(model)

        self._data_mapper.addMapping(self.ui_state_table       , 20,  b"analogStateTableView")
        self._data_mapper.addMapping(self.ui_calibration_table , 21,  b"calibrationTableView")
        self._data_mapper.addMapping(self.ui_units             , 22)
        self._data_mapper.addMapping(self.ui_display_digits    , 23)
        self._data_mapper.addMapping(self.ui_display_scientific, 24)
        self._data_mapper.addMapping(self.ui_scale_type        , 25,  b"currentIndex") #This is correct because we use the index of the dropdown item

    def setSelection(self, current):
        parent = current.parent()
        self._data_mapper.setRootIndex(parent)
        self._data_mapper.setCurrentModelIndex(current)

class AnalogOutputEditor(a_out_base, a_out_form):
    def __init__(self, parent=None):
        super(a_out_base, self).__init__(parent)
        self.setupUi(self)
        self._data_mapper = QtWidgets.QDataWidgetMapper()

        for i in strings.ANALOG_SCALE_TYPES.names:
            self.ui_scale_type.addItem(i)

        for i in strings.ANALOG_MANUAL_DISPLAY_TYPES.names:
            self.ui_manual_display_type.addItem(i)

    def setModel(self, model):
        if hasattr(model, 'sourceModel'):
            model = model.sourceModel()
        self._data_mapper.setModel(model)

        self._data_mapper.addMapping(self.ui_state_table        , 20,  b"analogStateTableView")
        self._data_mapper.addMapping(self.ui_calibration_table  , 21,  b"calibrationTableView")
        self._data_mapper.addMapping(self.ui_units              , 22)
        self._data_mapper.addMapping(self.ui_display_digits     , 23)
        self._data_mapper.addMapping(self.ui_display_scientific , 24)
        self._data_mapper.addMapping(self.ui_scale_type         , 25,  b"currentIndex") #This is correct because we use the index of the dropdown item
        self._data_mapper.addMapping(self.ui_manual_display_type, 26,  b"currentIndex") #This is correct because we use the index of the dropdown item

    def setSelection(self, current):
        parent = current.parent()
        self._data_mapper.setRootIndex(parent)
        self._data_mapper.setCurrentModelIndex(current)
