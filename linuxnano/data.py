from PyQt5 import QtCore, QtGui, QtXml, QtWidgets
import sys
import ast

import re
import itertools
import math
import operator
import xml.etree.ElementTree as ET


import os.path
import queue


#from ManualViewsOld import SVGItem2

from linuxnano.strings import strings
from linuxnano.message_box import MessageBox
from linuxnano.device_state_table_model import DeviceStateTableModel

from linuxnano.digital_state_table_model import DigitalStateTableModel
from linuxnano.analog_state_table_model import AnalogStateTableModel
from linuxnano.calibration_table_model import CalibrationTableModel

import copy
import itertools
import numpy as np



def clamp(n, smallest, largest): return max(smallest, min(n, largest))


def str2bool(v):
  return v.lower() in ("yes", "true", "t", "1")


#Sending a list ['one','two','etc'] so we don't use *enumerated
def enum(enumerated):
    enums = dict(zip(enumerated, range(len(enumerated))))
    enums["names"] = enumerated
    return type('enum', (), enums)











########################################
#
#  ToolModel           :
#  Node                :
#    SystemNode        :
#      DeviceNode      :
#      DigitalOutputNode :
#      DigitalInputNode  :
#
#  StateTableModel             : Table model with an output/input's state vs hal pins being True/False
#  DeviceStateTableModel : Table model with each combinaiton of states a device can be in
########################################





class Node(object):
    def __init__(self, parent=None):
        super().__init__()

        self._name = "unknown"
        self._description = ''

        self._children = []
        self._parent = parent

        if parent is not None:
            parent.addChild(self)


    def attrs(self):
        myClasses = self.__class__.__mro__

        kv = {}

        for cls in myClasses:
            for k, v in sorted(iter(cls.__dict__.items())):
                if isinstance(v, property):
                    #print "Property:", k.rstrip("_"), "\n\tValue:", v.fget(self)
                    kv[k] = v.fget(self)

        return kv


    def asXml(self):
        doc = QtXml.QDomDocument()

        node = doc.createElement(self.typeInfo())
        doc.appendChild(node)

        for i in self._children:
            i._recurseXml(doc, node)

        return doc.toString(indent=4)


    def _recurseXml(self, doc, parent):
        node = doc.createElement(self.typeInfo())
        parent.appendChild(node)

        attrs = self.attrs().items()

        for key, value in attrs:
            if isinstance(value, list):
                value = str(value)

            node.setAttribute(key, value)

        for i in self._children:
            i._recurseXml(doc, node)


    def loadAttribFromXML(self,xml_tree):
        try:
            #Get all the attributes of the node
            attrs = iter(self.attrs().items())

            for key, value in attrs:
                if key in xml_tree.attrib:
                    value = xml_tree.attrib[key]
                    setattr(self, key, value)

        except Exception as e:
            MessageBox("Error setting attribute XML", e, key, value)


    def typeInfo(self):
        return 'root'


    def child(self, row):
        return self._children[row]
        #XXX something is asking for child[-1]

    def addChild(self, child):
        self._children.append(child)
        child._parent = self


    def insertChild(self, position, child):
        if position < 0 or position > len(self._children):
            return False

        self._children.insert(position, child)
        child._parent = self
        return True


    def children(self):
        return self._children

    def childCount(self):
        return len(self._children)

    def removeChild(self, position):
        if position < 0 or position >= len(self._children):
            return False

        child = self._children.pop(position)
        child._parent = None

        return True

    def parent(self):
        return self._parent

    def row(self):
        if self._parent is not None:
            return self._parent._children.index(self)

    def data(self, column):
        if   column is 0: return self.name
        elif column is 1: return self.typeInfo()
        elif column is 2: return self.description

    def setData(self, column, value):
        if   column is 0: self.name        = value
        elif column is 1: pass
        elif column is 2: self.description = value


    #Properties common to all nodes
    def name():
        def fget(self): return self._name
        def fset(self, value): self._name = str(value)
        return locals()
    name = property(**name())


    def description():
        def fget(self): return self._description
        def fset(self, value): self._description = str(value)
        return locals()
    description = property(**description())


    # Loging of node
    def __repr__(self):
        return self.log()


    def log(self, tab_level=-1):
        output     = ""
        tab_level += 1

        for i in range(tab_level):
            output += "\t"

        output += "|------" + self._name + "\n"

        for child in self._children:
            output += child.log(tab_level)

        tab_level -= 1
        output += "\n"

        return output


        # XXX This will probaly go away
        #def childLengths(self):
        #    children = self.children()
        #    lens = []
        #    for i, child in enumerate(children):
        #        if child.typeInfo() == strings.DIGITAL_INPUT_NODE or child.typeInfo() == strings.DIGITAL_OUTPUT_NODE:
        #            lens.append(child.numberOfBits())
        #        elif child.typeInfo() == strings.ANALOG_INPUT_NODE or child.typeInfo() == strings.ANALOG_OUTPUT_NODE:
        #            lens.append(2)
        #    return lens



class ToolNode(Node):
    def __init__(self, parent=None):
        super().__init__(parent)

    def typeInfo(self):
        return strings.TOOL_NODE

    def iconResource(self):
        return strings.TREE_ICON_TOOL_NODE


class SystemNode(Node):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._background_svg = strings.DEFAULT_SYSTEM_BACKGROUND

    def typeInfo(self):
        return strings.SYSTEM_NODE

    def iconResource(self):
        return strings.TREE_ICON_SYSTEM_NODE


    def data(self, column):
        r = super().data(column)

        if column is 10: r = self.backgroundSVG
        return r


    def setData(self, column, value):
        super().setData(column, value)

        if column is 10: self.backgroundSVG = value


    def backgroundSVG():
        def fget(self): return self._background_svg
        def fset(self, value):
            if os.path.isfile(value):
                self._background_svg = value
            else:
                self._background_svg =  strings.DEFAULT_SYSTEM_BACKGROUND
        return locals()
    backgroundSVG = property(**backgroundSVG())




# This has to be fixed after the IO nodes are fixed
class DeviceNode(Node):
    def __init__(self, parent=None):
        super().__init__(parent)

        self._device_state_table_model = DeviceStateTableModel()

        #self._current_state = 0
        # should this exist?
        #self._io_bits = 0
        #self._io_names  = []
        #self._io_states = []
        #self._manual_queue            = Queue.Queue()

    def typeInfo(self):
        return strings.DEVICE_NODE

    def iconResource(self):
        return strings.TREE_ICON_DEVICE_NODE


    def addChild(self, child):
        super().addChild(child)
        self.halNodeChanged()

    def insertChild(self, position, child):
        super().insertChild(position, child)
        self.halNodeChanged()

    def removeChild(self, position):
        super().removeChild(position)
        self.halNodeChanged()

    def deviceStateTableModel(self):
        return self._device_state_table_model

    #TODO Next!
    def state(self):
        raise NotImplementedError("Need to write this still...")

        '''This returns the current state of the device, first reads all child nodes then lookups state in DeviceStateTable '''

    '''
    TODO Then we need to make an interface to set the outputs for a device.
    This will be used for the Alarm action in the DeviceStateTable
    It will also be used in the recipe 'set' command
    We'll make a mirrored one for inputs and do both for manual page
    ...need a VIEW class that generates buttons when passed a big array. then we can use a pyqtProperty to link the view


    DynamicOutputView
        - linked via pyqtProperty
        - recieves an array of outputs
        - D_OUT: name: option, option, option - lookup old code!

        one version will have buttons linked to setting outputs, other drop downs to save

    '''


    def halNodeChanged(self):
        states = []

        for child in self._children:
            if child.typeInfo() in [strings.D_IN_NODE, strings.D_OUT_NODE, strings.A_IN_NODE, strings.A_OUT_NODE]:
                states.append([child.name] + child.states())

        model = self.deviceStateTableModel()
        model.setNodeStates(states)



    def data(self, column):
        r = super().data(column)

        if   column is 10: r =  self.status
        elif column is 15: r =  self._device_state_table_model
        #elif column is 16: r =  self.currentState()
        return r

    def setData(self, column, value):
        super().setData(column, value)

        if   column is 10: pass#self.status = value
        elif column is 15: pass
        #elif column is 16: self.setCurrentState(value)


    def iconLayerList(self):
        for child in self._children:
            if child.typeInfo() in [strings.DEVICE_ICON_NODE]:
                return child.layers()
        return


    #TODO
    def status(self):
        return 'TODO Data DeviceNode status'

    def deviceStateTableData():
        def fget(self):
            return self.deviceStateTableModel().dataArray()

        def fset(self, value):
            try:
                my_arr = ast.literal_eval(value)
                self.deviceStateTableModel().setDataArray(my_arr)
            except Exception as e:
                MessageBox("Malformed device state table data", e, value)



        return locals()
    deviceStateTableData = property(**deviceStateTableData())







    ##########################################################
    ##########################################################
    ##########################################################
    ##########################################################
    #def addIO(self, bits):
    #    bits = int(bits)
    #    self._io_bits += bits
    #    self._combination_table_model.addNode(bits)

    #def ioChildren(self):
    #    children = self.children()
    #    io_children = []

    #    for i, child in enumerate(children):
    #        if child.typeInfo() == strings.DIGITAL_INPUT_NODE:
    #            io_children.append(child)

    #    for i, child in enumerate(children):
    #        if child.typeInfo() == strings.DIGITAL_OUTPUT_NODE:
    #            io_children.append(child)

    #    for i, child in enumerate(children):
    #        if child.typeInfo() == strings.ANALOG_INPUT_NODE:
    #            io_children.append(child)

    #    for i, child in enumerate(children):
    #        if child.typeInfo() == strings.ANALOG_OUTPUT_NODE:
    #            io_children.append(child)

    #    return io_children
    ##########################################################
    ##########################################################
    #def updateIconLayer(self):
    #    self._icon_object.setLayer(self.iconLayer())
    #def updateIconHoverLayer(self):
    #    self._icon_object.setHoverLayer(self.iconHoverLayer())

    #def manualQueueGet(self):
    #    return self._manual_queue.get()

    #def manualQueuePut(self, row):
    #    #check the format of row
    #    row = [True,True,1.345,False]
    #    self._manual_queue.put(row)


    #def iconLayer(self):
    #    row = self._combination_table_model.dataForRow(self._current_state_id)
    #    return row[1]

    #def iconHoverLayer(self):
    #    row = self._combination_table_model.dataForRow(self._current_state_id)
    #    return row[2]

    ##########################################################
    ##########################################################




    #def digitalInputs(self):
    #    ''' Returns a list of dictionaries of the devices state inputs
    #        Used by the manual view
    #
    #        Return Format:
    #          [ {name:"Interlock",  value:"On"},
    #            {name:"Water"    ,  value:"On"}  ]

    #

    #    '''
    #    inputs = []
    #    childCount = self.childCount()

    #    i = 0
    #
    #    while i < childCount:
    #        myChild = self.child(i)
    #
    #        if (myChild.typeInfo() == strings.DIGITAL_INPUT_NODE):
    #            name   = str(myChild.name())
    #            value  = myChild.currentState()

    #            input = {'name': name, 'value': value}
    #            inputs.append(input)
    #
    #        i += 1
    #
    #    return inputs



    #def analogInputs(self):
    #    ''' Returns a list of dictionaries of the devices state inputs
    #        Used by the manual view
    #
    #        Return Format:
    #          [ {name:"Air Flow",  value: "124.1", units:" L/min"},
    #            {name:"Pressure", value: "55.2", units:" mTorr"}  ]

    #

    #    '''
    #    inputs = []
    #    childCount = self.childCount()

    #    i = 0
    #
    #    while i < childCount:
    #        myChild = self.child(i)
    #
    #        if (myChild.typeInfo() == strings.ANALOG_INPUT_NODE):
    #            name   = str(myChild.name())
    #            value  = myChild.currentValue()
    #            units  = myChild.units()

    #            input = {'name': name, 'value': value, 'units':units}
    #            inputs.append(input)
    #
    #        i += 1
    #
    #    return inputs



    #def digitalOutputs(self):
    #    ''' Returns a list of dictionaries of the devices state outputs
    #        Used by the manual view
    #
    #        Return Format:
    #            [  {name:"Lamp",  buttons:["On",   "Off"],   manualSetting: "On",    currentSetting: "None"},
    #               {name:"Valve", buttons:["Open", "Close",  manualSetting: "Close", currentSetting: "None"]},
    #               {name:"Light", buttons:["Low",  "High",   manualSetting: None,    currentSetting: "None"]} ]

    #    '''
    #    outputs = []
    #    childCount = self.childCount()

    #    i = 0
    #
    #    while i < childCount:
    #        myChild = self.child(i)
    #
    #        if (myChild.typeInfo() == strings.DIGITAL_OUTPUT_NODE):
    #            groupName   = str(myChild.name())
    #            buttonNames = myChild.possibleStatesList()

    #            buttonGroup = {'groupName': groupName, 'buttons': buttonNames, 'manualSetting' : None, 'currentSetting': None}


    #            outputs.append(buttonGroup)
    #
    #
    #        i += 1
    #
    #
    #    return outputs
    #



    #def setState(self):

    #    setting = self.manualStateOutputs()

    #    if setting is not None:
    #
    #        for i, tmp in enumerate(setting):
    #
    #            if tmp['manualSetting'] is not None:

    #                    nodes = self.children()
    #
    #                    for i, node in enumerate(nodes):

    #                        if node.name() == tmp['groupName'] and node.typeInfo() == strings.DIGITAL_OUTPUT_NODE:
    #                            print('Setting on ', str(node.name()))
    #                            node.setOutputFromState(tmp['manualSetting'])
    #


    #    self.setManualStateOutputs(None)



    #def updateState(self):
    #    ''' The system controller calls this in order to update the
    #        devices current state '''
    #
    #    row = 0
    #    count = self.childCount()
    #    lengths = self.childLengths()

    #    for i, node in enumerate(self.ioChildren()):
    #
    #        # Find the factor to multiply the nodes state by for the proper row
    #        if ( (i+1) < len(lengths)) :
    #            factor = reduce(operator.mul, lengths[i+1:])
    #
    #        else:
    #            factor = 1


    #        row += factor * node.currentIndex()
    #
    #

    #    # Only update the state if it changed
    #    if self._current_state_id is not row:
    #
    #        data = self.combinationTableModel().dataForRow(row)
    #
    #
    #
    #        #print self.name() + " - " + str(row) + " : " + str(data)
    #
    #
    #        #Log state change
    #        print "State Changed: " + str(row)
    #        self._current_state_id = row

    #        #Update gui icons

    #        try:
    #            self.updateIconLayer()
    #            self.updateIconHoverLayer()
    #        except:
    #            print "Failed to update part of the gui"
    #
    #
    #        self._status = data[0]





class DeviceIconNode(Node):
    def __init__(self, parent=None):
        super().__init__(parent)

        self._name     = 'Icon'
        self._x        = 50.0
        self._y        = 50.0
        self._rotation = 0.0
        self._scale    = 1.0

        self._svg = 'resources/icons/general/unknown.svg'

        self._layer = ''
        self._number_node  = 'None'

        self._number_x             = 0
        self._number_y             = 0
        self._number_font_size     = 12

        self._number_min_font_size = 6
        self._number_max_font_size = 72


        #Data should not own view widgets...        self._icon_object = SVGWidget()

        #self._numeric_icon_object = None
        #not sure what type of data this should store XXX
        #temp_string_list = ('None','1','2')
        #self._number_node_list_model = QtCore.QStringListModel(temp_string_list)

        # We also need to know what index to use for the number if there is one.
        # Does this reference the id that the node owns or the QModelIndex
        #self._icon_number_node_index = None  #QModelIndex of the node that we get the # from, calculated at runtime
        #self._icon_number_node_id = 0  # ID of the node that we pull the number from



    def typeInfo(self):
        return strings.DEVICE_ICON_NODE


    def iconResource(self):
        return strings.TREE_ICON_DEVICE_ICON_NODE


    def data(self, column):
        r = super().data(column)

        if   column is 10: r = self.svg
        elif column is 11: r = self._layer #Will want to transmit the name for mapping this for manual icon view
        elif column is 14: r = self.x
        elif column is 15: r = self.y
        elif column is 16: r = self.scale
        elif column is 17: r = self.rotation
        elif column is 18: r = self.numberNodes().names.index(self._number_node)  #connected to a QComboBox which passes an index
        elif column is 19: r = self.numberX
        elif column is 20: r = self.numberY
        elif column is 21: r = self.numberFontSize


        return r


    def setData(self, column, value):
        super().setData(column, value)

        if   column is 10: self.svg                 = value
        elif column is 11:
            if value in self.layers().names:
                self._layer = str(value)
        elif column is 14: self.x                   = value
        elif column is 15: self.y                   = value
        elif column is 16: self.scale               = value
        elif column is 17: self.rotation            = value
        elif column is 18: self.numberNode          = self.numberNodes().names[value] #Connected to a QComboBox so we use an index
        elif column is 19: self.numberX             = value
        elif column is 20: self.numberY             = value
        elif column is 21: self.numberFontSize      = value


    def numberNodes(self):
        '''Returns enum of nodes available for graphic display'''
        node_names = ['None']

        for child in self.parent().children():
            if child.typeInfo() in [strings.A_IN_NODE, strings.A_OUT_NODE]:
                node_names.append(child.name)

        return enum(node_names)

    def layers(self):
        try:
            xml = ET.parse(self.svg)
            svg = xml.getroot()

            layers = []

            for child in svg:
                layers.append(child.attrib['id'])

            return enum(layers)
        except:
            return enum([])


    '''Cant use this format without it being a property / saved '''
    #def layer():
    #    def fget(self):
    #        print("layer fget:", self._layer)
    #        return self._layer

    #    def fset(self, value):
    #        print("layer fset:", value)

    #        if value in self.layers().names:
    #            self._layer = str(value)
    #        else:
    #            self._layer = ''
    #    return locals()
    #layer = property(**layer())



    def svg():
        def fget(self):
            return self._svg

        def fset(self, value):
            if os.path.isfile(value):
                self._svg = value
                #self._icon_object.setIconFile(self._icon_svg)
                #self.updateIconPosition()

        return locals()
    svg = property(**svg())


    def x():
        def fget(self): return self._x
        def fset(self,value):
            self._x = float(value)
            #self.updateIconPosition()
        return locals()
    x = property(**x())

    def y():
        def fget(self): return self._y
        def fset(self,value):
            self._y = float(value)
            #self.updateIconPosition()
        return locals()
    y = property(**y())

    def scale():
        def fget(self): return self._scale
        def fset(self,value):
            self._scale = float(value)
            #self.updateIconPosition()
        return locals()
    scale = property(**scale())

    def rotation():
        def fget(self): return self._rotation
        def fset(self,value):
            self._rotation = float(value)
            #self.updateIconPosition()
        return locals()
    rotation = property(**rotation())

    def numberX():
        def fget(self): return self._number_x
        def fset(self,value):
            self._number_x = float(value)
            #self.updateIconPosition()
        return locals()
    numberX = property(**numberX())

    def numberY():
        def fget(self): return self._number_y
        def fset(self,value):
            self._number_y = float(value)
            #self.updateIconPosition()
        return locals()
    numberY = property(**numberY())


    def numberFontSize():
        def fget(self): return self._number_font_size
        def fset(self,value):
            self._number_font_size = clamp( int(value) , self._number_min_font_size, self._number_max_font_size)
            #self.updateIconPosition()
        return locals()
    numberFontSize = property(**numberFontSize())



    def numberNode():
        '''Stores the name of the analog node for graphic display'''
        def fget(self):
            return self._number_node
        def fset(self, value): #self._number_node = value
            if value in self.numberNodes().names: #strings.ANALOG_MANUAL_DISPLAY_TYPES.names:
                self._number_node = value
            else:
                self._number_node = 'None'
        return locals()
    numberNode = property(**numberNode())





            #self._icon_object.setLayer(self._icon_layer)
        #return locals()
    #This is from the device state not a saved item iconLayer = property(**iconLayer())


#####################
    #def numberDisplayNodeListModel(self):
    #    return ({'list_model':self._number_node_list_model, 'current_id':self._icon_number_node_id},)

    #def setNumberDisplayNodeListModel(self, val):
    #    val = val[0]
    #
    #    model      = val['list_model']
    #    current_id = val['current_id']

    #    self._icon_number_node_id = current_id
#####################



    #def iconObject(self):
    #    return self._icon_object
    # Optional number next to the icon
    #def updateIconPosition(self):
    #    try:
    #        self._icon_object.updatePosition(self._icon_x,self._icon_y,self._icon_rotation, self._icon_scale)
    #    except:
    #        pass






class HalNode(Node):
    '''Common to all IO nodes
        All IO Nodes have:
            - name           : The nodes name is used for the hal pin name, for >1 bit name_0, name_1, etc.  This is unique within a device
            - number_of_bits : The number of bits this input has

            - state_table_model : This table does the conversion between state (True/False) and the 'value' string
            - state_table_data : This property is used to load and save state table model
    '''
    def __init__(self, parent=None):#, state_table_allow_is_used=False):
        super().__init__(parent)

        self._name = "IO_Node"

        #if state_table_allow_is_used == True:  self._state_table_model = StateTableModel(allow_is_used = True)
        #else:                                  self._state_table_model = StateTableModel(allow_is_used = False)
        #
        #self.stateTableModel().dataChanged.connect(self.stateTableChanged)
        #self.stateTableModel().modelReset.connect(self.stateTableChanged)


    def typeInfo(self):
        raise NotImplementedError("Nodes that inherit HalNode must implement typeInfo")

    def stateTableModel(self):
        raise NotImplementedError("Nodes that inherit HalNode must implement stateTableModel")
        #return self._state_table_model

    def stateTableChanged(self):
        try:
            self.parent().halNodeChanged()
        except Exception as e:
            pass
            #print("\nDevice node lacks halNodeChanged()")

    def numberOfStates(self):
        raise NotImplementedError("Nodes that inherit HalNode must implement numberOfStates")
        #return self.stateTableModel().numberOfBits()

    def states(self):
        return self.stateTableModel().states()

    def data(self, column):
        r = super().data(column)

        if   column is 11: r = self.numberOfStateBits
        elif column is 20: r = self.stateTableModel()

        return r

    def setData(self, column, value):
        super().setData(column, value)

        if   column is 11: pass #Num bits is only set by the state_table_view
        elif column is 20: pass #The state_table_model is owend by the node and never set again


    def name():
        def fget(self):
            return self._name

        def fset(self,value):
            '''We have to keep the names unique among all children owed by a Device '''

            #Only allowing alpha numeric, _ and - for now
            value = str(value)
            value = re.sub(r'[^a-zA-Z0-9_-]', '',value)

            sibling_names = []

            try:
                for child in self.parent().children():
                    if child != self:
                        sibling_names.append(child.name)

                while value in sibling_names:
                    value = value + "_new"

                self._name = value
                self.parent().halNodeChanged()


            except Exception as e:
                print("HalNode Error {}".format(e))


        return locals()
    name = property(**name())

    def stateTableData():
        def fget(self):
            return self.stateTableModel().dataArray()

        def fset(self, value):
            try:
                my_arr = ast.literal_eval(value)
                self.stateTableModel().setDataArray(my_arr)
                self.stateTableChanged()
            except Exception as e:
                MessageBox("Malformed state table data", e, value)


        return locals()
    stateTableData = property(**stateTableData())


class DigitalInputNode(HalNode):
    '''Represents a digital input (on/off), or group of inputs (low/medium/high) for a device.

        Digital inputs have:
            - name           : The nodes name is used for the hal pin name, for >1 bit name_0, name_1, etc
            - state_table_model : This table does the conversion between state (True/False) and the 'value' string
            - state_table_data : This property is used to load and save state table model
    '''

    def __init__(self, parent=None):
        super().__init__(parent)#, state_table_allow_is_used = False)

        self._state_table_model = DigitalStateTableModel(allow_is_used = False)
        self._state_table_model.dataChanged.connect(self.stateTableChanged)
        self._state_table_model.modelReset.connect(self.stateTableChanged)

    def typeInfo(self):
        return strings.D_IN_NODE

    def iconResource(self):
        return strings.TREE_ICON_D_IN_NODE

    def stateTableModel(self):
        return self._state_table_model

    def numberOfStates(self):
        return self._state_table_model.rowCount()

    def data(self, column):
        r = super().data(column)
        return r

    def setData(self, column, value):
        super().setData(column, value)


class DigitalOutputNode(HalNode):
    '''Represents a digital input (on/off), or group of inputs (low/medium/high) for a device.

        Digital outputs have:
            - name           : The nodes name is used for the hal pin name, for >1 bit name_0, name_1, etc
            - state_table_model : This table does the conversion between state (True/False) and the 'value' string
            - state_table_data : Used to load and save the data from teh state table model as a property
            - manual_display_type : How should it be displayed on the manual window (buttons or dropdown)
    '''

    def __init__(self, parent=None):
        super().__init__(parent)

        self._manual_display_type = strings.MANUAL_DISPLAY_TYPES.names[0]

        self._state_table_model = DigitalStateTableModel(allow_is_used = True)
        self._state_table_model.dataChanged.connect(self.stateTableChanged)
        self._state_table_model.modelReset.connect(self.stateTableChanged)


    def typeInfo(self):
        return strings.D_OUT_NODE

    def iconResource(self):
        return strings.TREE_ICON_D_OUT_NODE

    def stateTableModel(self):
        return self._state_table_model

    def numberOfStates(self):
        return self._state_table_model.rowCount()

    def data(self, column):
        r = super().data(column)
        if column is 21: r = strings.MANUAL_DISPLAY_TYPES.names.index(self.manualDisplayType)
        return r

    def setData(self, column, value):
        super().setData(column, value)
        if column is 21: self.manualDisplayType = strings.MANUAL_DISPLAY_TYPES.names[value]


    def manualDisplayType():
        def fget(self): return self._manual_display_type
        def fset(self, value):
            if value in strings.MANUAL_DISPLAY_TYPES.names:
                self._manual_display_type = value
        return locals()
    manualDisplayType = property(**manualDisplayType())


class AnalogInputNode(HalNode):
    '''Represents an analog input (i.e. 0-10 VDC) for a device

        Analog inputs have:
            - name           : The nodes name is used for the hal pin name, for >1 bit name_0, name_1, etc

            - state_table_model : This table does the conversion between state (0V>X>5.5V) and the 'value' string
            - state_table_data : This property is used to load and save state table model

            - calibration_table_model : Calibration of analog signal to HAL numbers
            - calibration_table_data : This property is used to load and save cal data

            - units
            - display_digits
            - display_scientific : If true use scientific notation
            - scale_type : Linear or cubic spline for signal calibration
    '''
    def __init__(self, parent=None):
        super().__init__(parent)
        self._state_table_model = AnalogStateTableModel()

        self._calibration_table_model = CalibrationTableModel()
        self._calibration_table_model.dataChanged.connect(self.calibrationTableChanged)
        self._calibration_table_model.modelReset.connect(self.calibrationTableChanged)


        self._units              = ''
        self._display_digits     = strings.A_IN_DISPLAY_DIGITS_DEFAULT
        self._display_scientific = False
        self._scale_type         = strings.ANALOG_SCALE_TYPES.names[0]  #Linear or cubic_spline


    def typeInfo(self):
        return strings.A_IN_NODE

    def iconResource(self):
        return strings.TREE_ICON_A_IN_NODE

    def stateTableModel(self):
        return self._state_table_model

    def numberOfStates(self):
        return self._state_table_model.rowCount()

    def calibrationTableModel(self):
        return self._calibration_table_model

    def data(self, column):
        r = super().data(column)

        if   column is 21: r = self._calibration_table_model
        elif column is 22: r = self.units
        elif column is 23: r = self.displayDigits
        elif column is 24: r = self.displayScientific
        elif column is 25: r = strings.ANALOG_SCALE_TYPES.names.index(self.scaleType) #FIXME

        return r


    def setData(self, column, value):
        super().setData(column, value)

        if   column is 21: pass
        elif column is 22: self.units             = value
        elif column is 23: self.displayDigits     = value
        elif column is 24: self.displayScientific = value
        elif column is 25: self.scaleType         = strings.ANALOG_SCALE_TYPES.names[value] #FIXME


    def units():
        def fget(self): return self._units
        def fset(self, value): self._units = str(value)
        return locals()
    units = property(**units())

    def displayDigits():
        def fget(self): return self._display_digits
        def fset(self, value): self._display_digits = clamp(int(value),0,strings.A_IN_DISPLAY_DIGITS_MAX)
        return locals()
    displayDigits = property(**displayDigits())

    def displayScientific():
        def fget(self): return self._display_scientific
        def fset(self, value):
            if value == True or value == 'True':
                self._display_scientific = True
            else:
                self._display_scientific = False

        return locals()
    displayScientific = property(**displayScientific())

    def scaleType():
        def fget(self): return self._scale_type
        def fset(self, value):
            if value in strings.ANALOG_SCALE_TYPES.names:
                self._scale_type = value
        return locals()
    scaleType = property(**scaleType())

    def calibrationTableChanged(self):
        try:
            self.parent().halNodeChanged()
        except Exception as e:
            MessageBox("Failed when changing calibration table", e)

    def calibrationTableData():
        def fget(self):
            return self.calibrationTableModel().dataArray()

        def fset(self, value):
            try:
                my_arr = ast.literal_eval(value)
                self.calibrationTableModel().setDataArray(my_arr)
                self.calibrationTableChanged()
            except Exception as e:
                MessageBox("Malformed calibration table data", e, value)


        return locals()
    calibrationTableData = property(**calibrationTableData())


class AnalogOutputNode(AnalogInputNode):
    '''Represents an analog output (i.e. 0-10 VDC) for a device

        Analog outputs have:
            - name           : The nodes name is used for the hal pin name, for >1 bit name_0, name_1, etc

            - state_table_model : This table does the conversion between state (0V>X>5.5V) and the 'value' string
            - state_table_data : This property is used to load and save state table model

            - calibration_table_model : Calibration of analog signal to HAL numbers
            - calibration_table_data : This property is used to load and save cal data

            - units
            - display_digits
            - display_scientific : If true use scientific notation
            - scale_type : Linear or cubic spline for signal calibration
    '''
    def __init__(self, parent=None):
        super().__init__(parent)
        self._manual_display_type = strings.ANALOG_MANUAL_DISPLAY_TYPES.names[0]

    def typeInfo(self):
        return strings.A_OUT_NODE

    def iconResource(self):
        return strings.TREE_ICON_A_OUT_NODE

    def data(self, column):
        r = super().data(column)
        if column is 26: r = strings.ANALOG_MANUAL_DISPLAY_TYPES.names.index(self._manual_display_type)

        return r

    def setData(self, column, value):
        super().setData(column, value)
        if column is 26: self.manualDisplayType = strings.ANALOG_MANUAL_DISPLAY_TYPES.names[value]


    def displayDigits():
        def fget(self): return self._display_digits
        def fset(self, value): self._display_digits = clamp(int(value),0,strings.A_OUT_DISPLAY_DIGITS_MAX)
        return locals()
    displayDigits = property(**displayDigits())

    def manualDisplayType():
        def fget(self): return self._manual_display_type
        def fset(self, value):
            if value in strings.ANALOG_MANUAL_DISPLAY_TYPES.names:
                self._manual_display_type = value
        return locals()
    manualDisplayType = property(**manualDisplayType())
