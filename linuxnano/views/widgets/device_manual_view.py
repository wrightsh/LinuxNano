from PyQt5 import QtCore, QtGui, QtWidgets, uic
from linuxnano.strings import strings
#from linuxnano.table_models import DeviceStateTableModel
#from linuxnano.table_models import StateTableModel
#from linuxnano.table_models import ScaleTableModel
#import copy

manual_device_view_base, manual_device_view_form = uic.loadUiType("linuxnano/views/DeviceManualView.ui")


class DeviceManualView(manual_device_view_base, manual_device_view_form):
    def __init__(self):#, model, parent=None):
        super(manual_device_view_base, self).__init__()
        self.setupUi(self)

#class DeviceManualView(QtWidgets.QWidget):
#    def __init__(self):
#        super(DeviceManualView, self).__init__()
        self._mapper = QtWidgets.QDataWidgetMapper()

        #self._name = QtWidgets.QLabel('Unknown')
        #self._name.setFont(QtGui.QFont("Helvetica",weight=QtGui.QFont.Bold))

        #self._description = QtWidgets.QLabel('Unknown')
        #self._status = QtWidgets.QLabel('Unknown')
        self._digitalInputWid  = DigitalInputGroup()
        #self._digitalOutputWid = DigitalOutputGroup()
        #self._analogInputWid = AnalogInputGroup()
        #self._analogOutputWid = AnalogOutputGroup()



        #vBox = QtWidgets.QVBoxLayout()
        #statusHBox = QtWidgets.QHBoxLayout()
        #vBox.addWidget(self._name)
        #vBox.addWidget(self._status)
        #vBox.addWidget(self._status)
        #vBox.addStretch(1)
        #vBox.addWidget(self._digitalInputWid)
        #vBox.addWidget(self._analogInputWid)
        #vBox.addWidget(self._digitalOutputWid)
        #vBox.addWidget(self._analogOutputWid)

        #self.setLayout(vBox)


    def setSelection(self, index):
        if hasattr(index.model(), 'mapToSource'):
            index = index.model().mapToSource(index)

        node = index.internalPointer()
        if node is not None:
            typeInfo = node.typeInfo()

        parent_index = index.parent()
        self._mapper.setRootIndex(parent_index)
        self._mapper.setCurrentModelIndex(index)


    def setModel(self, model):
        if hasattr(model, 'mapToSource'):
            model = model.sourceModel()

        self._mapper.setModel(model)
        self._mapper.addMapping(self.ui_name,              0, bytes("text",'ascii'))
        self._mapper.addMapping(self.ui_description,       2, bytes("text",'ascii'))
        self._mapper.addMapping(self.ui_status,           10, bytes("text",'ascii'))
        #self._mapper.addMapping(self._digitalInputWid,  10, bytes("digitalInputs",'ascii'))
        #self._mapper.addMapping(self._digitalOutputWid, 11, bytes("digitalOutputs",'ascii'))
        #self._mapper.addMapping(self._analogInputWid,   12, bytes("analogInputs",'ascii'))
        #self._mapper.addMapping(self._analogOutputtWid, 13, "analogOutputs")


'''
Type 1: buttons linked to the actions
Type 2: dropdown to select it or maybe radio buttons? or buttons but they stay clicked like a radio button?
'''
class DigitalOutputGroup(QtWidgets.QWidget):
    '''Each digial ouptut node is shown as a row of buttons.
    '''

    def __init__(self, parent=None):
        super(DigitalOutputGroup, self).__init__(parent)

        self._digitalOutputs = []
        self.layoutGroupBox = QtWidgets.QVBoxLayout(self)
        self.update()


    #value is a list
    def setDigitalOutputs(self, value):
        try:
            self._digitalOutputs = value[0]

        except:
            print('Add error handling')

        self.update()



    def getDigitalOutputs(self):
        return (self._digitalOutputs, )


    def update(self):
        #Remove all old
        for i in reversed(range(self.layoutGroupBox.count())):
            self.layoutGroupBox.itemAt(i).widget().setParent(None)

        #Add a label for each new
        if len(self._digitalOutputs):
            self.layoutGroupBox.addWidget(QtWidgets.QLabel("Digital Outputs"))

        self._myList = []


        for i, item in enumerate(self._digitalOutputs):


            self.layoutGroupBox.addWidget(QtWidgets.QLabel(item['groupName']))

            buttons = item['buttons']


            hbox = QtWidgets.QHBoxLayout()
            widget = QtWidgets.QWidget()
            widget.setLayout(hbox)

            for btn in buttons:


                pushButton = QtWidgets.QPushButton(btn)
                pushButton.value = item['groupName']

                pushButton.clicked.connect(self.btnClicked)
                hbox.addWidget(pushButton)

                #Connect some sort of signal to set this name to this btn name or something....
            self.layoutGroupBox.addWidget(widget)


    def btnClicked(self):
        name = self.sender().value
        text = str(self.sender().text())

        #Set mannual thing to what the value and text is


        for i, item in enumerate(self._digitalOutputs):

            if self._digitalOutputs[i]['groupName'] == name:
                self._digitalOutputs[i]['manualSetting'] = text
                break


        QtGui.QApplication.postEvent(self, QtGui.QKeyEvent(QtCore.QEvent.KeyPress, QtCore.Qt.Key_Enter, QtCore.Qt.NoModifier))



    tmpList = ([1,2,5], ) # tuple
    digitalOutputs = QtCore.pyqtProperty(type(tmpList),getDigitalOutputs,setDigitalOutputs)

class DigitalInputGroup(QtWidgets.QWidget):
    '''Each digial input node is shown as a row
       Format: "Name : value"
    '''

    def __init__(self, parent=None):
        super(DigitalInputGroup, self).__init__(parent)

        self._digitalInputs = []
        self.layoutGroupBox = QtWidgets.QVBoxLayout(self)
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
            self.layoutGroupBox.addWidget(QtWidgets.QLabel("Digital Inputs"))

        self._myList = []
        for i, item in enumerate(self._digitalInputs):
            if item['value'] == None:
                tmp_val = 'not yet read...'
            else:
                tmp_val = str(item['value'])

            self._myList.append(QtWidgets.QLabel(item['name'] +"    -    " +tmp_val ))
            self.layoutGroupBox.addWidget(self._myList[i])



    tmpList = ([1,2,5], ) # tuple
    digitalInputs = QtCore.pyqtProperty(type(tmpList),getDigitalInputs,setDigitalInputs)

class AnalogInputGroup(QtWidgets.QWidget):
    '''Each digial input node is shown as a row
       Format: "Name : value"
    '''

    def __init__(self, parent=None):
        super(AnalogInputGroup, self).__init__(parent)

        self._analogInputs = []
        self.layoutGroupBox = QtWidgets.QVBoxLayout(self)
        self.update()



    def setAnalogInputs(self, value):
        self._analogInputs =  value[0]
        self.update()


    def getAnalogInputs(self):
        return (self._analogInputs, )


    def update(self):

        #Remove all old
        for i in reversed(range(self.layoutGroupBox.count())):
            self.layoutGroupBox.itemAt(i).widget().setParent(None)



        #Add a label for each new
        if len(self._analogInputs):
            self.layoutGroupBox.addWidget(QtWidgets.QLabel("Analog Inputs"))

        self._myList = []
        for i, item in enumerate(self._analogInputs):
            if item['value'] == None:
                tmp_val = 'not yet read...'
            else:
                tmp_val = item['value']

            self._myList.append(QtWidgets.QLabel(item['name'] +"    -    " + "{:10.1f}".format(tmp_val ) + " " +item['units']))
            self.layoutGroupBox.addWidget(self._myList[i])



    tmpList = ([1,2,5], ) # tuple
    analogInputs = QtCore.pyqtProperty(type(tmpList),getAnalogInputs,setAnalogInputs)
