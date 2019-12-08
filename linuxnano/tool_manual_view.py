# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtGui, uic, QtWidgets
import os

from linuxnano.views.widgets.tool_tree_view import ToolTreeView
from linuxnano.tool_model import LeafFilterProxyModel

from linuxnano.strings import strings

tool_manual_view_base, tool_manual_view_form  = uic.loadUiType("linuxnano/views/ToolManualView.ui")


class ToolManualView(tool_manual_view_base, tool_manual_view_form):
    def __init__(self, model, parent=None):
        super(tool_manual_view_base, self).__init__(parent)
        self.setupUi(self)

        self._model = model
        self._proxy_model =  LeafFilterProxyModel(self) #maybe not self?

        """VIEW <------> PROXY MODEL <------> DATA MODEL"""
        self._proxy_model.setSourceModel(self._model)
        self._proxy_model.setDynamicSortFilter(True)
        self._proxy_model.setFilterCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self.ui_filter.textChanged.connect(self._proxy_model.setFilterRegExp)


        self.ui_tree.setModel(self._proxy_model) #maybe not self?)
        self.ui_tree.selectionModel().currentChanged.connect(self.setGraphicSelection)
        self.ui_system_manual_view.setModel(self._proxy_model)
        self.ui_system_manual_view.selectionModel().currentChanged.connect(self.setTreeSelection)

        self.ui_splitter_horizontal.setSizes([self.width()*0.6, self.width()*0.4])
        self.ui_splitter_vertical.setSizes([self.height()*0.4, self.height()*0.6])
        self.ui_tree.setColumnWidth(0,300)

        self.vlayout = QtWidgets.QVBoxLayout()
        #self.hideEditors()


    #def hideEditors(self):
    #    self._a_out_editor.setVisible(False)


    def setTreeSelection(self, index):
        if not hasattr(index.model(), 'mapToSource'):
            # not are a proxy model
            index = self._proxy_model.mapFromSource(index)

        self.ui_tree.setCurrentIndex(index)
        #self.ui_tree.selectionModel().setCurrentIndex(index, QtCore.QItemSelectionModel.ClearAndSelect)

    def setGraphicSelection(self, index):
        self.ui_system_manual_view.setSelection(index)
        self.dig_ins(index)


    def dig_ins(self, device_index):
        if hasattr(device_index.model(), 'mapToSource'):
            device_index = device_index.model().mapToSource(device_index)

        self.ui_button_group.setLayout(self.vlayout)
        for i in reversed(range(self.vlayout.count())):
            self.vlayout.itemAt(i).widget().setParent(None)

        node = device_index.internalPointer()
        if node.typeInfo() == strings.DEVICE_NODE:
            print('its a device node')
            for row in range(self._model.rowCount(device_index)):
                child_index = device_index.child(row,0)
                if child_index.internalPointer().typeInfo() == strings.D_IN_NODE:

                    my_label = QtWidgets.QLineEdit('need_to_set')
                    my_label2 = QtWidgets.QLabel('need_to_set')

                    self.vlayout.addWidget(my_label)
                    self.vlayout.addWidget(my_label2)

                    mapper = QtWidgets.QDataWidgetMapper()

                    model = child_index.model()
                    if hasattr(child_index.model(), 'sourceModel'):
                        model = model.sourceModel()

                    mapper.setModel(model)

                    mapper.addMapping(my_label, 0)
                    mapper.addMapping(my_label2,0, bytes("text",'ascii'))
                    mapper.addMapping(my_label2, 0)

                    mapper.setRootIndex(device_index)
                    mapper.setCurrentModelIndex(child_index)
                    print('its a d in node')

        self.ui_button_group.show()



#        system_indexes.append(tool_index.child(row, 0))
#        node = index.internalPointer()
#        if node.typeInfo() == strings.DEVICE_NODE:
#            for child in node.children():
#                if child.typeInfo() == strings.D_IN_NODE:
#                    vlayout = QtWidgets.QVBoxLayout(self.ui_button_group)
#                    my_label = QtWidgets.QLabel('need_to_set')
#                    vlayout.addWidget(my_label)
#
#                    mapper = QtWidgets.QDataWidgetMapper()
#                    mapper.setModel(self._model)
#                    mapper.addMapping(my_label, 0)
#                    mapper.setCurrentModelIndex(index)
#
#


class DigitalInputGroup(QtWidgets.QWidget):
    '''Each digial input node is shown as a row
       Format: "Name : value"
    '''

    def __init__(self, parent=None):
        super(DigitalInputGroup, self).__init__(parent)

        self._digitalInputs = []
        self.layoutGroupBox = QtGui.QVBoxLayout(self)
        self.update()


    def setDigitalInputs(self, value):
        self._digitalInputs =  value[0]
        self.update()

    def getDigitalInputs(self):
        return (self._digitalInputs, )


    def update(self):

        #Remove all old
        for i in reversed(range(self.layoutGroupBox.count())):
            self.layoutGroupBox.itemAt(i).widget().setParent(None)

        #Add a label for each new
        if len(self._digitalInputs):
            self.layoutGroupBox.addWidget(QtGui.QLabel("Digital Inputs"))

        self._myList = []
        for i, item in enumerate(self._digitalInputs):
            if item['value'] == None:
                tmp_val = 'not yet read...'
            else:
                tmp_val = str(item['value'])

            self._myList.append(QtGui.QLabel(item['name'] +"    -    " +tmp_val ))
            self.layoutGroupBox.addWidget(self._myList[i])



    tmpList = ([1,2,5], ) # tuple
    digitalInputs = QtCore.pyqtProperty(type(tmpList),getDigitalInputs,setDigitalInputs)
