#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pytest
import ast
import xml.etree.ElementTree as ET
from PyQt5 import QtCore, QtWidgets, QtGui

from linuxnano.flags import TestingFlags
from linuxnano.strings import strings

from linuxnano.data import Node, ToolNode, SystemNode, DeviceNode, DeviceIconNode, HalNode, DigitalInputNode, DigitalOutputNode, AnalogInputNode, AnalogOutputNode
from linuxnano.data import BoolVarNode, FloatVarNode
from linuxnano.digital_state_table_model import DigitalStateTableModel
from linuxnano.analog_state_table_model import AnalogStateTableModel
from linuxnano.calibration_table_model import CalibrationTableModel
from linuxnano.device_state_table_model import DeviceStateTableModel

import json

#@pytest.fixture(params=['tests/tools/tool_model_1.xml'])
#def tool_model(request):
#    tree = ET.parse(request.param)
#    tool_model = ToolModel()
#    tool_model.loadTool(tree)
#    return tool_model




########## Node ##########
def test_node_attrs():
    node = Node()
    assert node.attrs() == {'description': '', 'name': 'unknown'}


def test_node_asJSON_and_load():
    root = Node()
    child_1 = Node()
    child_2 = Node()

    root.addChild(child_1)
    root.addChild(child_2)


    standard = json.loads('''{
                        "children": [
                            {
                                "children": [],
                                "description": "",
                                "name": "unknown",
                                "type_info": "root"
                            },
                            {
                                "children": [],
                                "description": "",
                                "name": "unknown_new",
                                "type_info": "root"
                            }
                        ],
                        "description": "",
                        "name": "unknown",
                        "type_info": "root"
                    }''')

    new = json.loads('''{
                        "description": "my desc.",
                        "name": "A_name",
                        "type_info": "root"
                    }''')


    assert standard == json.loads(root.asJSON())

    #This will only load the properties for the node, the recursion in in the model
    root.loadAttrs(new)
    assert root.name == "A_name"
    assert root.description == "my desc."


def test_node_typeInfo():
    node = Node()
    assert node.typeInfo() == 'root'


def test_node_addChild():
    root = Node()
    child_1 = Node()

    root.addChild(child_1)
    assert child_1 == root.child(0)

def test_node_insertChild():
    root = Node()
    child_1 = Node()
    child_2 = Node()
    child_3 = Node()

    root.addChild(child_1)
    root.addChild(child_3)
    root.insertChild(1,child_2)

    assert child_1 == root.child(0)
    assert child_2 == root.child(1)
    assert child_3 == root.child(2)


def test_node_children():
    root = Node()
    child_1 = Node()
    child_2 = Node()
    child_3 = Node()

    root.addChild(child_1)
    root.addChild(child_2)
    root.addChild(child_3)

    children = root.children()

    assert len(children) == 3
    assert children[1] == child_2
    assert root.childCount() == 3


def test_node_removeChild():
    root = Node()
    child_1 = Node()
    child_2 = Node()
    child_3 = Node()

    root.addChild(child_1)
    root.addChild(child_2)
    root.addChild(child_3)

    root.removeChild(1)
    assert root.childCount() == 2

    root.removeChild(1)
    assert root.childCount() == 1

    root.removeChild(1) #There's only a child at position 0
    assert root.childCount() == 1

    root.removeChild(0)
    assert root.childCount() == 0


def test_node_parent():
    root    = Node()
    child_1 = Node()

    root.addChild(child_1)

    assert root.parent()    == None
    assert child_1.parent() == root


def test_node_row():
    root    = Node()
    child_1 = Node()
    child_2 = Node()
    child_3 = Node()

    root.addChild(child_1)
    root.addChild(child_2)
    root.addChild(child_3)

    assert root.row()    == None
    assert child_1.row() == 0
    assert child_2.row() == 1
    assert child_3.row() == 2


def test_node_setData():
    root = Node()
    root.setData(0, "my_nam e") #It should remove the space
    root.setData(1, "typeinfo is hard coded")
    root.setData(2, "my description")

    assert root.data(0) == "my_name"
    assert root.data(1) == "root"
    assert root.data(2) == "my description"




########## ToolNode ##########
def test_ToolNode_typeInfo():
    tool  = ToolNode()
    assert tool.typeInfo() == strings.TOOL_NODE


########## SystemNode ##########
def test_SystemNode_typeInfo():
    system  = SystemNode()
    assert system.typeInfo() == strings.SYSTEM_NODE


def test_SystemNode_setData():
    node = SystemNode()
    node.setData(0, "my_system_name")
    node.setData(1, "typeinfo is hard coded")
    node.setData(2, "my description")
    node.setData(10, strings.DEFAULT_SYSTEM_BACKGROUND)

    assert node.data(0) == "my_system_name"
    assert node.data(1) == strings.SYSTEM_NODE
    assert node.data(2) == "my description"
    assert node.data(10) == strings.DEFAULT_SYSTEM_BACKGROUND

def test_SystemNode_backgroundSVG():
    node = SystemNode()

    assert node.backgroundSVG == strings.DEFAULT_SYSTEM_BACKGROUND
    node.backgroundSVG = "invalid file path"
    assert node.backgroundSVG == strings.DEFAULT_SYSTEM_BACKGROUND



########## DeviceNode ##########
def test_DeviceNode_typeInfo():
    device  = DeviceNode()
    assert device.typeInfo() == strings.DEVICE_NODE

def test_DeviceNode_setData():
    device  = DeviceNode()

    new_status = 'The devices behavior tree will set the status.'
    current_status = device.data(10)
    device.setData(10, new_status)
    assert device.data(10) == new_status

def test_DeviceNode_iconLayerList():
    device = DeviceNode()
    icon_node = DeviceIconNode()
    icon_node.setData(10, 'linuxnano/resources/icons/valves/valve.svg')

    device.addChild(icon_node)

    assert device.iconLayerList().names == ['closed', 'closing', 'open', 'opening', 'fault']



########## DeviceIconNode ##########
def test_DeviceIconNode_typeInfo():
    node = DeviceIconNode()
    assert node.typeInfo() == strings.DEVICE_ICON_NODE

def test_DeviceIconNode_setData():
    device  = DeviceNode()
    node = DeviceIconNode()
    device.addChild(node)

    node.setData(10, 'linuxnano/resources/icons/valves/valve.svg') #svg
    node.setData(11, 'closing') #svg layer
    node.setData(12, 51) #x
    node.setData(13, 57) #y
    node.setData(14, 1.12) #scale
    node.setData(15, 90) #rotation

    node.setData(16, True) #hasText
    node.setData(17, 'a word') #text
    node.setData(18, 63) #textX
    node.setData(19, 60) #textY
    node.setData(20, 18) #textFontSize

    assert node.data(10) == 'linuxnano/resources/icons/valves/valve.svg'
    assert node.data(11) == 'closing'
    assert node.data(12) == 51
    assert node.data(13) == 57
    assert node.data(14) == 1.12
    assert node.data(15) == 90

    assert node.data(16) == True
    assert node.data(17) == 'a word'
    assert node.data(18) == 63
    assert node.data(19) == 60
    assert node.data(20) == 18


def test_DeviceIconNode_layers():
    node = DeviceIconNode()
    node.setData(10, 'linuxnano/resources/icons/valves/valve.svg')

    assert node.layers().names == ['closed', 'closing', 'open', 'opening', 'fault']




########## HalNode ##########
#TODO: signalName or move that to the manual file

def test_HalNode_typeInfo():
    node = HalNode()
    with pytest.raises(Exception) as e_info:
        node.typeInfo()

def test_HalNode_setData():
    node = HalNode()

    node.setData(10, 1)
    assert node.data(10) == 1 #uses an index


def test_HalNode_samplerStreamerIndex():
    node = HalNode()
    node.setSamplerIndex(17)
    assert node.samplerIndex() == 17

    with pytest.raises(Exception) as e_info:
        node.setSamplerIndex('wrong')

    node.setStreamerIndex(7)
    assert node.streamerIndex() == 7

    with pytest.raises(Exception) as e_info:
        node.setSamplerIndex('wrong')

def test_HalNode_manualQueue():
    node = HalNode()
    node.manualQueuePut('thing_1')
    node.manualQueuePut('thing_2')
    node.manualQueuePut('thing_3')

    assert node.manualQueueGet() == 'thing_1'
    assert node.manualQueueGet() == 'thing_2'
    assert node.manualQueueGet() == 'thing_3'



########## DigitalInputNode ##########
def test_DigitalInputNode_name():
    device  = DeviceNode()
    node_1 = DigitalInputNode()
    node_2 = DigitalInputNode()
    node_3 = DigitalInputNode()

    device.addChild(node_1)
    device.addChild(node_2)
    device.addChild(node_3)

    node_1.name = "signal_1"
    node_2.name = "signal-$$@/::\\!2"
    node_3.name = "signal 3"

    assert node_1.name == "signal_1"
    assert node_2.name == "signal-2"
    assert node_3.name == "signal3"

    node_2.name = "signal_1"
    node_3.name = "signal_1"

    assert node_2.name == "signal_1_new"
    assert node_3.name == "signal_1_new_new"

def test_DigitalInputNode_typeInfo():
    node = DigitalInputNode()
    assert node.typeInfo() == strings.D_IN_NODE

def test_DigitalInputNode_displayValue():
    node = DigitalInputNode()

    node.displayValueOff = 'down'
    assert node.displayValueOff == 'down'

    node.displayValueOn = 'up'
    assert node.displayValueOn == 'up'

    node.setData(20, False)
    assert node.data(20) == False
    assert node.data(21) == 'down'

    node.setData(20, True)
    assert node.data(20) == True
    assert node.data(21) == 'up'


########## DigitalOutputNode ##########
def test_DigitalOutputNode_typeInfo():
    node = DigitalOutputNode()
    assert node.typeInfo() == strings.D_OUT_NODE

def test_DigitalOutputNode_valueName():
    node = DigitalOutputNode()

    node.displayValueOff = 'down'
    assert node.displayValueOff == 'down'

    node.displayValueOn = 'up'
    assert node.displayValueOn == 'up'

    node.setData(20, False)
    assert node.data(20) == False
    assert node.data(21) == 'down'

    node.setData(20, True)
    assert node.data(20) == True
    assert node.data(21) == 'up'





########## AnalogInputNode ##########
def test_AnalogInputNode_typeInfo():
    node = AnalogInputNode()
    assert node.typeInfo() == strings.A_IN_NODE

def test_AnalogInputNode_calibrationTableModel():
    node = AnalogInputNode()
    assert type(node.calibrationTableModel()) == type(CalibrationTableModel())

def test_AnalogInputNode_units():
    node = AnalogInputNode()

    node.units = 'mTorr'
    assert node.units == 'mTorr'

    node.units = 'Torr'
    assert node.units == 'Torr'

def test_AnalogInputNode_displayDigits():
    node = AnalogInputNode()

    assert node.displayDigits == strings.A_DISPLAY_DIGITS_DEFAULT

    node.displayDigits = -1
    assert node.displayDigits == 0

    node.displayDigits = 9991
    assert node.displayDigits == strings.A_DISPLAY_DIGITS_MAX

def test_AnalogInputNode_displayScientific():
    node = AnalogInputNode()
    assert node.displayScientific == False

    node.displayScientific = True
    assert node.displayScientific == True

    node.displayScientific = 'ham'
    assert node.displayScientific == False


def test_AnalogInputNode_calibrationTableData():
    node = AnalogInputNode()

    good_cal = [['hal_value','gui_value'],[0.0,0.0],[ 1.0, 12.4],[2, 24.8]]
    bad_cal  = [['hal_value','gui_value'],[0.0,0.0],[-1.0, 12.4],[2, 24.8]]

    node.calibrationTableData = good_cal
    assert node.calibrationTableData == good_cal

    node.calibrationTableData = bad_cal
    assert node.calibrationTableData == good_cal

    node.setData(20, .12)
    assert node.displayValue() == 1.488
    assert node.data(21) == 1.488



def test_AnalogInputNode_displayValue():
    node = AnalogInputNode()
    cal = [['hal_value','gui_value'],[0.0,0.0],[ 10.0, 500.0]]
    node.calibrationTableData = cal

    node.setData(20, 1.0)
    assert node.displayValue() == 50
    assert node.data(21) == 50

    node.setData(20, 1.5)
    assert node.displayValue() == 75
    assert node.data(21) == 75

def test_AnalogInputNode_displayToHal():
    node = AnalogInputNode()
    cal = [['hal_value','gui_value'],[0.0,0.0],[ 10.0, 500.0]]
    node.calibrationTableData = cal

    node.setData(20, 1.75)

    assert node.data(20) == 1.75
    assert node.displayToHal(node.displayValue()) == 1.75


def test_AnalogInputNode_setData():
    node = AnalogInputNode()
    cal = [['hal_value','gui_value'],[0.0,0.0],[ 10.0, 500.0]]
    node.calibrationTableData = cal

    node.setData(20, 1.5)
    node.setData(21, "can't set this")
    node.setData(22, 'mTorr')
    node.setData(23, 5)
    node.setData(24, True)
    node.setData(25, "can't set this")

    assert node.data(20) == 1.5
    assert node.data(21) == 75
    assert node.data(22) == 'mTorr'
    assert node.data(23) == 5
    assert node.data(24) == True
    assert type(node.data(25)) == type(CalibrationTableModel())


########## AnalogOutputNode ##########
def test_AnalogOutputNode_typeInfo():
    node = AnalogOutputNode()
    assert node.typeInfo() == strings.A_OUT_NODE


########## BoolVarNode ##########
def test_BoolVarNode_typeInfo():
    node = BoolVarNode()
    assert node.typeInfo() == strings.BOOL_VAR_NODE

def test_BoolVarNode_setData():
    node = BoolVarNode()

    node.setData(10, True)
    node.setData(13, True)
    node.setData(14, True)
    assert node.data(10) == True
    assert node.data(13) == True
    assert node.data(14) == True

    node.setData(10, False)
    node.setData(13, False)
    node.setData(14, False)
    assert node.data(10) == False
    assert node.data(13) == False
    assert node.data(14) == False

    node.setData(10, 'False')
    node.setData(13, 'False')
    node.setData(14, 'False')
    assert node.data(10) == False
    assert node.data(13) == False
    assert node.data(14) == False

    node.setData(11, 'OPEN')
    node.setData(12, 'CLOSE')
    assert node.data(11) == 'OPEN'
    assert node.data(12) == 'CLOSE'






########## FloatVarNode ##########
def test_FloatVarNode_typeInfo():
    node = FloatVarNode()
    assert node.typeInfo() == strings.FLOAT_VAR_NODE

def test_FloatVarNode_setData():
    node = FloatVarNode()
    node.min = -10.0
    node.max = 10.0

    assert node.min == -10.0
    assert node.max == 10.0

    node.setData(10, 1.234)
    assert node.data(10) == 1.234

    node.setData(10, -991.234)
    assert node.data(10) == -10.0

    node.setData(10, 12.0)
    assert node.data(10) == 10.0

    #min
    node.setData(11, -100.1)
    assert node.data(11) == -100.1

    #max
    node.setData(12, 100.1)
    assert node.data(12) == 100.1

    node.setData(10, 102)
    assert node.data(10) == 100.1

    #man_enable
    node.setData(13, True)
    assert node.data(13) == True

    node.setData(13, False)
    assert node.data(13) == False
