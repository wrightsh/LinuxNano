#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtGui, QtXml, QtWidgets
import sys

import re
import itertools
import math
import operator
import xml.etree.ElementTree as ET

import json
import os.path

from linuxnano.bt_model import BTModel

#from linuxnano.hardware import hardware
from linuxnano.strings import defaults, col, typ
from linuxnano.message_box import MessageBox
from linuxnano.calibration_table_model import CalibrationTableModel

import copy
import itertools
import numpy as np

import queue
from queue import Queue, Empty

def clamp(n, smallest, largest): return max(smallest, min(n, largest))

def str2bool(v):
  return v.lower() in ("yes", "true", "t", "1")

#Sending a list ['one','two','etc'] so we don't use *enumerated
def enum(enumerated):
    enums = dict(zip(enumerated, range(len(enumerated))))
    enums["names"] = enumerated
    return type('enum', (), enums)


class Node:
    def __init__(self, parent=None):
        super().__init__()

        self._parent = parent
        self._children = []
        self._name = "unknown"
        self._description = ''

        if parent is not None:
            parent.addChild(self)


    def attrs(self):
        kv = {}
        my_classes = self.__class__.__mro__

        for cls in my_classes:
            for key, val in sorted(iter(cls.__dict__.items())):
                if isinstance(val, property):
                    kv[key] = val.fget(self)
        return kv

    def loadAttrs(self, data):
        try:
            #Get all the attributes of the node
            attrs = iter(self.attrs().items())
            for key, value in attrs:
                if key in data:
                    setattr(self, key, data[key])

        except Exception as e:
            MessageBox("Error loading attribute", e, key, value)



    def convertToDict(self, o):
        #Need to manually add type_info and children since they aren't properties
        data = {"type_info": o.typeInfo(),
                "children" : o.children()}

        attrs = iter(o.attrs().items())
        for key, value in attrs:
            data[key] = value

        return data

    def asJSON(self):
        data = json.dumps(self, default=self.convertToDict,  sort_keys=True, indent=4)
        return data

    def typeInfo(self):
        return 'root'

    def parent(self):
        return self._parent

    def child(self, row):
        return self._children[row]

    def addChild(self, child):
        self._children.append(child)
        child._parent = self
        child.name = child.name #Force the name to be unique

    def insertChild(self, position, child):
        if position < 0 or position > len(self._children):
            return False

        self._children.insert(position, child)
        child._parent = self
        child.name = child.name #Force the name to be unique
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


    def row(self):
        if self._parent is not None:
            return self._parent._children.index(self)
        else:
            return 0


    def data(self, c):
        if   c is col.NAME: return self.name
        elif c is col.TYPE_INFO: return self.typeInfo()
        elif c is col.DESCRIPTION: return self.description

    def setData(self, c, value):
        if   c is col.NAME: self.name = value
        elif c is col.TYPE_INFO: pass
        elif c is col.DESCRIPTION: self.description = value

    def name():
        def fget(self):
            return self._name

        def fset(self,value):
            #Sibling names must be unique, only allowing alpha numeric, _ and -
            value = str(value)
            value = re.sub(r'[^a-zA-Z0-9_-]', '',value)

            if self.parent() == None:
                self._name = value

            else:
                sibling_names = []

                for child in self.parent().children():
                    if child != self:
                        sibling_names.append(child.name)

                while value in sibling_names:
                    value = value + "_new"

                self._name = value

        return locals()
    name = property(**name())

    def description():
        def fget(self): return self._description
        def fset(self, value): self._description = str(value)
        return locals()
    description = property(**description())


class ToolNode(Node):
    def __init__(self, parent=None):
        super().__init__(parent)

    def typeInfo(self):
        return typ.TOOL_NODE


class SystemNode(Node):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._background_svg = defaults.SYSTEM_BACKGROUND
        self._movable_icons = False

    def typeInfo(self):
        return typ.SYSTEM_NODE

    def data(self, c):
        r = super().data(c)

        if   c is col.BACKGROUND_SVG: r = self.backgroundSVG
        elif c is col.MOVABLE_ICONS : r = self.movableIcons()
        return r

    def setData(self, c, value):
        super().setData(c, value)
        if   c is col.BACKGROUND_SVG: self.backgroundSVG = value
        elif c is col.MOVABLE_ICONS : self._movable_icons = value

    def movableIcons(self):
        return self._movable_icons

    def backgroundSVG():
        def fget(self): return self._background_svg
        def fset(self, value):
            if isinstance(value, str) and os.path.isfile(value):
                self._background_svg = value
            else:
                self._background_svg =  defaults.SYSTEM_BACKGROUND
        return locals()
    backgroundSVG = property(**backgroundSVG())



# This has to be fixed after the IO nodes are fixed
class DeviceNode(Node):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._status = ''
        self._is_dirty = False
        self._bt_model = BTModel()

        file = 'tests/behaviors/test_1.json'
        with open(file) as f:
            json_data = json.load(f)

        self._bt_model.loadJSON(json_data)


        '''
        Device Children:
            - hal Nodes
            - buffered com nodes like serial

            - variables --> table owned by the device or children?
                - digital and analog
                - has min and max
                - manual view of variables lets you set them

        a device has a:
            - a behavior tree
                - a devices bt has to know the children of the device

                - on load it needs to check if everything it has in it actually exists
                - the hardware  file will be going through evaluating the branches/leaves



        '''
    def typeInfo(self):
        return typ.DEVICE_NODE

    def data(self, c):
        r = super().data(c)
        if c is col.STATUS: r =  self._status
        return r

    def setData(self, c, value):
        super().setData(c, value)
        if c is col.STATUS: self._status = str(value)

    def dirty(self):
        return self._is_dirty

    def setDirty(self, value):
        self._is_dirty = True if value else False

    #def halNodeChanged(self):
    #    states = []
    #    for child in self._children:
    #        if child.typeInfo() in [typ.D_IN_NODE, typ.D_OUT_NODE, typ.A_IN_NODE, typ.A_OUT_NODE]:
    #            states.append((child.name, child.states))
    #    model = self.deviceStateTableModel()
    #    model.setNodeStates(states)


#TODO: Add background and font color and left/right align
class DeviceIconNode(Node):
    def __init__(self, parent=None):
        super().__init__(parent)

        self._name     = 'Icon'
        self._x        = 50.0
        self._y        = 50.0
        self._rotation = 0.0
        self._scale    = 1.0

        self._layer = ''
        self._layers = []

        self._has_text = False
        self._text = ''
        self._text_x = 0
        self._text_y = 0

        self._font_size = 12
        self._min_font_size = 6
        self._max_font_size = 72

        self.svg = defaults.DEVICE_ICON        #'linuxnano/resources/icons/general/unknown.svg'

    def typeInfo(self):
        return typ.DEVICE_ICON_NODE

    def data(self, c):
        r = super().data(c)

        if   c is col.SVG      : r = self.svg
        elif c is col.LAYER    : r = self.layer()
        elif c is col.X        : r = self.x
        elif c is col.Y        : r = self.y
        elif c is col.SCALE    : r = self.scale
        elif c is col.ROTATION : r = self.rotation

        elif c is col.HAS_TEXT : r = self.hasText
        elif c is col.TEXT     : r = self._text
        elif c is col.TEXT_X   : r = self.textX
        elif c is col.TEXT_Y   : r = self.textY
        elif c is col.FONT_SIZE: r = self.fontSize

        elif c is col.POS      : r = QtCore.QPointF(self.x, self.y)

        return r

    def setData(self, c, value):
        super().setData(c, value)

        if   c is col.SVG       : self.svg      = value
        elif c is col.LAYER     : self._layer   = value
        elif c is col.X         : self.x        = value
        elif c is col.Y         : self.y        = value
        elif c is col.SCALE     : self.scale    = value
        elif c is col.ROTATION  : self.rotation = value

        elif c is col.HAS_TEXT  : self.hasText  = value
        elif c is col.TEXT      : self._text    = str(value)
        elif c is col.TEXT_X    : self.textX    = value
        elif c is col.TEXT_Y    : self.textY    = value
        elif c is col.FONT_SIZE : self.fontSize = value

        elif c is col.POS:
            self.x = value.x()
            self.y = value.y()


    def text(self):
        return self._text

    def layer(self):
        if self._layer in self.layers().names:
            return self._layer
        else:
            return self.layers().names[0]

    ''' TODO: change how this enum works?'''
    def layers(self):
        '''Returns enum of layers for a dropdown list in the deviceStateTableModel'''
        return enum(self._layers)


    #All of these properties get saved
    def svg():
        def fget(self):
            return self._svg

        def fset(self, value):
            try:
                self._svg = value
                self._layers = []
                xml = ET.parse(self._svg)
                svg = xml.getroot()

                for child in svg:
                    self._layers.append(child.attrib['id'])

            except:
                self._svg = 'linuxnano/resources/icons/general/unknown.svg'
                xml = ET.parse(self._svg)
                svg = xml.getroot()

                for child in svg:
                    self._layers.append(child.attrib['id'])

        return locals()
    svg = property(**svg())

    def x():
        def fget(self): return self._x
        def fset(self,value): self._x = float(value)
        return locals()
    x = property(**x())

    def y():
        def fget(self): return self._y
        def fset(self,value): self._y = float(value)
        return locals()
    y = property(**y())

    def scale():
        def fget(self): return self._scale
        def fset(self,value): self._scale = float(value)
        return locals()
    scale = property(**scale())

    def rotation():
        def fget(self): return self._rotation
        def fset(self,value): self._rotation = float(value)
        return locals()
    rotation = property(**rotation())

    def hasText():
        def fget(self): return self._has_text
        def fset(self,value): self._has_text = bool(value)
        return locals()
    hasText = property(**hasText())

    def textX():
        def fget(self): return self._text_x
        def fset(self,value): self._text_x = float(value)
        return locals()
    textX = property(**textX())

    def textY():
        def fget(self): return self._text_y
        def fset(self,value): self._text_y = float(value)
        return locals()
    textY = property(**textY())


    def fontSize():
        def fget(self): return self._font_size
        def fset(self,value):
            self._font_size = clamp( int(value) , self._min_font_size, self._max_font_size)
        return locals()
    fontSize = property(**fontSize())


    ''''Saving the number node code for now because it was werid to make with the enum:'''
    #def numberNode():
    #    '''Stores the name of the analog node for graphic display'''
    #    def fget(self):
    #        return self._number_node
    #    def fset(self, value): #self._number_node = value
    #        if value in self.numberNodes().names: #strings.ANALOG_MANUAL_DISPLAY_TYPES.names:
    #            self._number_node = value
    #        else:
    #            self._number_node = 'None'
    #    return locals()
    #numberNode = property(**numberNode())
    #elif column is 18:
    #    try:
    #        r = self.numberNodes().names.index(self._number_node)  #connected to a QComboBox which passes an index
    #    except:
    #        self.numberNode = self.numberNodes().names[0] #If it fails then we set it to None which is 0
    #        r = self.numberNodes().names.index(self._number_node)

    #elif column is 18: self.numberNode          = self.numberNodes().names[value] #Connected to a QComboBox so we use an index

    #def numberNodes(self):
    #    '''Returns enum of nodes available for graphic display'''
    #    node_names = ['None']

    #    for child in self.parent().children():
    #        if child.typeInfo() in [strings.A_IN_NODE, strings.A_OUT_NODE]:
    #            node_names.append(child.name)

    #    return enum(node_names)



class HalNode(Node):
    '''Common to all IO nodes
        All IO Nodes have:
            - name           : The nodes name is used for the hal pin name, for >1 bit name_0, name_1, etc.  This is unique within a device
    '''
    hal_pins = []  # Format (pin_name, direction, type)

    def __init__(self, parent=None):
        super().__init__(parent)

        self._name = 'HAL_Node'
        self._hal_pin = ''
        self._hal_pin_type = None

        #not sure on these
        self._sampler_index = None
        self._streamer_index = None
        self._manual_queue = Queue()


    def typeInfo(self):
        raise NotImplementedError("Nodes that inherit HalNode must implement typeInfo")

    def data(self, c):
        r = super().data(c)
        if c is col.HAL_PIN:
            try:
                r = self.halPins().names.index(self._hal_pin) #Connected to a QComboBox which passes an index
            except:
                self.halPin = ''
                r = ''
        elif c is col.HAL_PIN_TYPE: r = self._hal_pin_type

        return r

    def setData(self, c, value):
        super().setData(c, value)

        if c is col.HAL_PIN:
            try:
                self.halPin = self.halPins().names[value] #Connected to a QComboBox so we use an index
            except:
                self.halPin = ''
        elif c is col.HAL_PIN_TYPE: pass

    def signalName(self):
        return self.parent().parent().name + '.' + self.parent().name + '.' + self.name + '.'

    def samplerIndex(self):
        return self._sampler_index

    def setSamplerIndex(self, value):
        if not isinstance(value, int):
            raise TypeError("setSamplerIndex must receive an integer")
        self._sampler_index = value

    def streamerIndex(self):
        return self._streamer_index

    def setStreamerIndex(self, value):
        if not isinstance(value, int):
            raise TypeError("setStreamerIndex must receive an integer")
        self._streamer_index = value

    def manualQueueGet(self):
        return self._manual_queue.get_nowait()

    def manualQueuePut(self, value):
        self._manual_queue.put_nowait(value)

    def halPin():
        def fget(self): return self._hal_pin
        def fset(self, value):
            try:
                pin = [item for item in HalNode.hal_pins if item[0] == value]
                self._hal_pin = pin[0][0]
                self._hal_pin_type = pin[0][1]
            except:
                self._hal_pin = ""
                self._hal_pin_type = None
        return locals()
    halPin = property(**halPin())

    #def signals(self):
    #    signals = []
    #    base_name = self.parent().parent().name + '.' + self.parent().name + '.' + self.name + '.'
    #    for i, item in enumerate(self.halPins):
    #        signals.append(base_name + str(i))
    #    return signals


class DigitalInputNode(HalNode):
    def __init__(self, parent=None):
        super().__init__(parent)

        self._name = 'Digital_Input_Node'
        self._val = False
        self._off_name = ''
        self._on_name = ''

    def typeInfo(self):
        return typ.D_IN_NODE

    def data(self, c):
        r = super().data(c)
        if   c is col.VALUE    : r = self._val
        elif c is col.OFF_NAME : r = self.offName
        elif c is col.ON_NAME  : r = self.onName

        return r

    def setData(self, c, value):
        super().setData(c, value)
        if c is col.VALUE:
            self._val = True if value == True else False
            if self.parent():
                self.parent().setDirty(True)

        elif c is col.OFF_NAME : self.offName = value
        elif c is col.ON_NAME  : self.onName  = value

    def value(self):
        return self._val

    def halPins(self):
        all_pins = HalNode.hal_pins #list of (name, type, dir)
        sub_pins = [item for item in all_pins if item[1] == 'bit']
        pins = [item[0] for item in sub_pins if item[2] == 'OUT']
        pins.insert(0, '')
        return enum(pins)

    def offName():
        def fget(self): return self._off_name
        def fset(self,value): self._off_name = str(value)
        return locals()
    offName = property(**offName())

    def onName():
        def fget(self): return self._on_name
        def fset(self,value): self._on_name = str(value)
        return locals()
    onName = property(**onName())


class DigitalOutputNode(DigitalInputNode):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._name = 'Digital_Output_Node'

    def typeInfo(self):
        return typ.D_OUT_NODE

    def halPins(self):
        all_pins = HalNode.hal_pins #list of (name, type, dir)
        sub_pins = [item for item in all_pins if item[1] == 'bit']
        pins = [item[0] for item in sub_pins if item[2] == 'IN']
        pins.insert(0, '')
        return enum(pins)



#TODO figure out the number type part
class AnalogInputNode(HalNode):
    '''
        Represents an analog input (i.e. 0-10 VDC) for a device
            - calibration_table_model : Calibration of analog signal to HAL numbers
            - calibration_table_data : This property is used to load and save cal data
            - display_digits : number of digits to display on default
            - display_scientific : If true use scientific notation
    '''
    def __init__(self, parent=None):
        super().__init__(parent)
        self._name = 'Analog_Input_Node'

        self._hal_val = 0
        self._val = 0
        self._units = ''

        self._display_digits = defaults.A_DISPLAY_DIGITS
        self._display_scientific = False

        self._calibration_table_model = CalibrationTableModel()
        self._calibration_table_model.dataChanged.connect(self.updateScaleFactor)
        self._calibration_table_model.modelReset.connect(self.updateScaleFactor)

        self._xp = [0,0]
        self._yp = [0,0]


    def typeInfo(self):
        return typ.A_IN_NODE

    def calibrationTableModel(self):
        return self._calibration_table_model

    def data(self, c):
        r = super().data(c)

        if   c is col.HAL_VALUE               : r = self._hal_val
        elif c is col.VALUE                   : r = self.value()
        elif c is col.UNITS                   : r = self.units
        elif c is col.DISPLAY_DIGITS          : r = self.displayDigits
        elif c is col.DISPLAY_SCIENTIFIC      : r = self.displayScientific
        elif c is col.CALIBRATION_TABLE_MODEL : r = self._calibration_table_model

        return r

    def setData(self, c, value):
        super().setData(c, value)

        if   c is col.HAL_VALUE          : self._hal_val = value
        elif c is col.VALUE              : pass
        elif c is col.UNITS              : self.units = value
        elif c is col.DISPLAY_DIGITS     : self.displayDigits = value
        elif c is col.DISPLAY_SCIENTIFIC : self.displayScientific = value
        elif c is 25: pass

    def value(self):
        return float(np.interp(self._hal_val, self._xp, self._yp))

    def displayToHal(self, val):
        return np.interp(val, self._yp, self._xp)

    def updateScaleFactor(self):
        try:
            self._xp = self._calibration_table_model.halValues()
            self._yp = self._calibration_table_model.guiValues()
        except:
            self._xp = [0,0]
            self._yp = [0,0]

    def halPins(self):
        all_pins = HalNode.hal_pins #list of (name, type, dir)
        sub_pins = [item for item in all_pins if item[1] in ['S32','U32','FLOAT']]
        pins = [item[0] for item in sub_pins if item[2] == 'OUT']
        pins.insert(0, '')
        return enum(pins)

    def units():
        def fget(self): return self._units
        def fset(self, value): self._units = str(value)
        return locals()
    units = property(**units())

    def displayDigits():
        def fget(self): return self._display_digits
        def fset(self, value):
            self._display_digits = clamp(int(value), 0, defaults.A_DISPLAY_DIGITS_MAX)
            self.updateScaleFactor()
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

    def calibrationTableData():
        def fget(self):
            return self.calibrationTableModel().dataArray()

        def fset(self, value):
            try:
                self.calibrationTableModel().setDataArray(value)
                self.updateScaleFactor()
            except Exception as e:
                MessageBox("Malformed calibration table data", e, value)

        return locals()
    calibrationTableData = property(**calibrationTableData())


class AnalogOutputNode(AnalogInputNode):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._name = 'Analog_Output_Node'

    def typeInfo(self):
        return typ.A_OUT_NODE

    def halPins(self):
        all_pins = HalNode.hal_pins #list of (name, type, dir)
        sub_pins = [item for item in all_pins if item[1] in ['S32','U32','FLOAT']]
        pins = [item[0] for item in sub_pins if item[2] == 'IN']
        pins.insert(0, '')
        return enum(pins)


class BoolVarNode(Node):
    def __init__(self, parent=None):
        super().__init__(parent)

        self._name = 'Bool_Var_Node'
        self._val = False

        self._off_name = ''
        self._on_name = ''
        self._enable_manual = True
        self._view_only = True

    def typeInfo(self):
        return typ.BOOL_VAR_NODE

    def data(self, c):
        r = super().data(c)

        if   c is col.VALUE         : r = self._val
        elif c is col.OFF_NAME      : r = self.offName
        elif c is col.ON_NAME       : r = self.onName
        elif c is col.ENABLE_MANUAL : r = self.enableManual
        elif c is col.VIEW_ONLY     : r = self.viewOnly

        return r

    def setData(self, c, value):
        super().setData(c, value)
        print("Col: ",c, " - ",value)
        if c is col.VALUE:
            self._val = True if value == True else False
            if self.parent():
                self.parent().setDirty(True)

        elif c is col.OFF_NAME      : self.offName      = value
        elif c is col.ON_NAME       : self.onName       = value
        elif c is col.ENABLE_MANUAL : self.enableManual = value
        elif c is col.VIEW_ONLY     : self.viewOnly     = value

    def value(self):
        return self._val

    def offName():
        def fget(self): return self._off_name
        def fset(self, value): self._off_name = str(value)
        return locals()
    offName = property(**offName())

    def onName():
        def fget(self): return self._on_name
        def fset(self, value): self._on_name = str(value)
        return locals()
    onName = property(**onName())

    def enableManual():
        def fget(self): return self._enable_manual
        def fset(self, value):
            if value == True or value == 'True':
                self._enable_manual = True
            else:
                self._enable_manual = False

        return locals()
    enableManual = property(**enableManual())

    def viewOnly():
        def fget(self): return self._view_only
        def fset(self, value):
            if value == True or value == 'True':
                self._view_only = True
            else:
                self._view_only = False

        return locals()
    viewOnly = property(**viewOnly())


class FloatVarNode(Node):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._name = 'Float_Var_Node'
        self._val = 0
        self._min = 0
        self._max = 0
        self._units = ''
        self._display_digits = defaults.A_DISPLAY_DIGITS
        self._display_scientific = False
        self._enable_manual = True
        self._view_only = True

    def typeInfo(self):
        return typ.FLOAT_VAR_NODE

    def data(self, c):
        r = super().data(c)
        if   c is col.VALUE              : r = self._val
        elif c is col.MIN                : r = self.min
        elif c is col.MAX                : r = self.max
        elif c is col.UNITS              : r = self.units
        elif c is col.DISPLAY_DIGITS     : r = self.displayDigits
        elif c is col.DISPLAY_SCIENTIFIC : r = self.displayScientific
        elif c is col.ENABLE_MANUAL      : r = self.enableManual
        elif c is col.VIEW_ONLY          : r = self.viewOnly
        return r


    def setData(self, c, value):
        super().setData(c, value)
        if c is col.VALUE:
            self._val = clamp(float(value), self.min, self.max)
            if self.parent():
                self.parent().setDirty(True)
        elif c is col.MIN                : self.min = value
        elif c is col.MAX                : self.max = value
        elif c is col.UNITS              : self.units = value
        elif c is col.DISPLAY_DIGITS     : self.displayDigits = value
        elif c is col.DISPLAY_SCIENTIFIC : self.displayScientific = value
        elif c is col.ENABLE_MANUAL      : self.enableManual = value
        elif c is col.VIEW_ONLY          : self.viewOnly = value

    def value(self):
        return self._val

    def min():
        def fget(self): return self._min
        def fset(self, value): self._min = float(value)
        return locals()
    min = property(**min())

    def max():
        def fget(self): return self._max
        def fset(self, value): self._max = float(value)
        return locals()
    max = property(**max())

    def units():
        def fget(self): return self._units
        def fset(self, value): self._units = str(value)
        return locals()
    units = property(**units())

    def displayDigits():
        def fget(self): return self._display_digits
        def fset(self, value):
            self._display_digits = clamp(int(value), 0, defaults.A_DISPLAY_DIGITS_MAX)
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

    def enableManual():
        def fget(self): return self._enable_manual
        def fset(self, value):
            if value == True or value == 'True':
                self._enable_manual = True
            else:
                self._enable_manual = False

        return locals()
    enableManual = property(**enableManual())

    def viewOnly():
        def fget(self): return self._view_only
        def fset(self, value):
            if value == True or value == 'True':
                self._view_only = True
            else:
                self._view_only = False

        return locals()
    viewOnly = property(**viewOnly())
