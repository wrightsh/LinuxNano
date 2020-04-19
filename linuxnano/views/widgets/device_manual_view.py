from PyQt5 import QtCore, QtGui, QtWidgets, uic
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


        #Look for any digital inputs
        for row in range(self._model.rowCount(index)):
            child_index = index.child(row,0)
            wid = None

            if child_index.internalPointer().typeInfo() == strings.D_IN_NODE:
                wid = DigitalInputManualView(child_index.internalPointer())

            elif child_index.internalPointer().typeInfo() == strings.D_OUT_NODE:
                wid = DigitalOutputManualView(child_index.internalPointer())

            elif child_index.internalPointer().typeInfo() == strings.A_IN_NODE:
                wid = AnalogInputManualView()

            elif child_index.internalPointer().typeInfo() == strings.A_OUT_NODE:
                wid = AnalogOutputManualView()

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
        self._mapper.addMapping(self.ui_status,           11, bytes("text",'ascii'))

    def model(self):
        return self._model


class DigitalInputManualView(QtWidgets.QWidget):
    '''Each digial input node is shown as a row
       Format: "Name : value"  '''
    def __init__(self, node):
        super().__init__()
        self.mapper = QtWidgets.QDataWidgetMapper()
        hbox = QtWidgets.QHBoxLayout()
        self.setLayout(hbox)

        self.name_label = QtWidgets.QLabel('unknown_name')
        self.text_label = QtWidgets.QLabel('unknown_value')
        hbox.addWidget(self.name_label)
        hbox.addWidget(QtWidgets.QLabel(': '))
        hbox.addWidget(self.text_label)
        hbox.addStretch(1)

        self._value = 0
        self._value_names = node.states

    def setRootIndex(self, index):
        self.mapper.setRootIndex(index)

    def setCurrentModelIndex(self, index):
        self.mapper.setCurrentModelIndex(index)

    @QtCore.pyqtProperty(int)
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        try:
            self.text_label.setText(self._value_names[value])
        except IndexError:
            self.text_label.setText("Error")



    def setModel(self, model):
        if hasattr(model, 'sourceModel'):model = model.sourceModel()
        self.mapper.setModel(model)
        self.mapper.addMapping(self.name_label, 0, bytes("text",'ascii'))
        self.mapper.addMapping(self, 20, bytes('value','ascii'))
        #self.mapper.addMapping(self.text_label, 22, bytes("text",'ascii'))




'''
Type 1: buttons linked to the actions
Type 2: dropdown to select it or maybe radio buttons? or buttons but they stay clicked like a radio button?
'''
class DigitalOutputManualView(QtWidgets.QWidget):
    def __init__(self, node):#hal_pins, states, is_used):
        super().__init__()

        self._node = node
        hal_pins = node.signals()
        states = node.states
        is_used = node.isUsed


        self.mapper = QtWidgets.QDataWidgetMapper()
        hbox = QtWidgets.QHBoxLayout(self)
        self.setLayout(hbox)

        self.name_label = QtWidgets.QLabel('unknown_name')
        hbox.addWidget(self.name_label)
        hbox.addWidget(QtWidgets.QLabel(': '))

        self.btn_group = QtWidgets.QButtonGroup()
        self.btn_group.setExclusive(True)
        self.via_value_setter = False

        self._hal_pins = hal_pins
        self._is_used = is_used
        self._interlock = 255

        self.btn_group.buttonClicked.connect(self.onClicked)

        for i, state in enumerate(states):
            if self._is_used[i] == True:
                btn = QtWidgets.QPushButton(state, self)
                btn.setCheckable(True)
                hbox.addWidget(btn)
                self.btn_group.addButton(btn,i)

        hbox.addStretch(1)

    def setRootIndex(self, index):
        self.mapper.setRootIndex(index)

    def setCurrentModelIndex(self, index):
        self.mapper.setCurrentModelIndex(index)

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
        self.mapper.addMapping(self.name_label, 0, bytes("text",'ascii'))
        self.mapper.addMapping(self, 22, bytes('interlock','ascii'))
        self.mapper.addMapping(self, 20, bytes('value','ascii')) #FIXME no idea why this breaks if I change the order of the addMapping



class AnalogInputManualView(QtWidgets.QWidget):
    '''Each analog input node is shown as a row
       Format: "Name : value units"  '''
    def __init__(self):
        super().__init__()
        self.mapper = QtWidgets.QDataWidgetMapper()
        hbox = QtWidgets.QHBoxLayout()
        self.setLayout(hbox)

        #QtWidgets.QLabel(item['name'] +"    -    " + "{:10.1f}".format(tmp_val ) + " " +item['units']))
        self.name_label = QtWidgets.QLabel('unknown_name')
        self.value_label = QtWidgets.QLabel('unknown_value')
        self.units_label = QtWidgets.QLabel('unknown_units')
        hbox.addWidget(self.name_label)
        hbox.addWidget(QtWidgets.QLabel(': '))
        hbox.addWidget(self.value_label)
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
        self.mapper.addMapping(self.value_label, 30, bytes("text",'ascii'))
        self.mapper.addMapping(self.units_label, 22, bytes("text",'ascii'))

class AnalogOutputManualView(QtWidgets.QWidget):
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
