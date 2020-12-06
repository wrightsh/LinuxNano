#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pytest
import ast
import xml.etree.ElementTree as ET
from PyQt5 import QtCore, QtWidgets, QtGui

from linuxnano.flags import TestingFlags
from linuxnano.strings import strings, col, typ

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

    assert root.row()    == 0 #FIXME Not sure if we should test this to be 0 or None
    assert child_1.row() == 0
    assert child_2.row() == 1
    assert child_3.row() == 2


def test_node_setData():
    root = Node()
    root.setData(col.NAME, "my_nam e") #It should remove the space
    root.setData(col.TYPE_INFO, "typeinfo is hard coded")
    root.setData(col.DESCRIPTION, "my description")

    assert root.data(col.NAME) == "my_name"
    assert root.data(col.TYPE_INFO) == "root"
    assert root.data(col.DESCRIPTION) == "my description"




########## ToolNode ##########
def test_ToolNode_typeInfo():
    tool  = ToolNode()
    assert tool.typeInfo() == typ.TOOL_NODE


########## SystemNode ##########
def test_SystemNode_typeInfo():
    system  = SystemNode()
    assert system.typeInfo() == typ.SYSTEM_NODE


def test_SystemNode_setData():
    node = SystemNode()
    node.setData(col.NAME, "my_system_name")
    assert node.data(col.NAME) == "my_system_name"

    node.setData(col.TYPE_INFO, "typeinfo is hard coded")
    assert node.data(col.TYPE_INFO) == typ.SYSTEM_NODE

    node.setData(col.DESCRIPTION, "my description")
    assert node.data(col.DESCRIPTION) == "my description"

    node.setData(col.BACKGROUND_SVG, strings.DEFAULT_SYSTEM_BACKGROUND)
    assert node.data(col.BACKGROUND_SVG) == strings.DEFAULT_SYSTEM_BACKGROUND

def test_SystemNode_backgroundSVG():
    node = SystemNode()

    assert node.backgroundSVG == strings.DEFAULT_SYSTEM_BACKGROUND
    node.backgroundSVG = "invalid file path"
    assert node.backgroundSVG == strings.DEFAULT_SYSTEM_BACKGROUND



########## DeviceNode ##########
def test_DeviceNode_typeInfo():
    device  = DeviceNode()
    assert device.typeInfo() == typ.DEVICE_NODE

def test_DeviceNode_setData():
    device  = DeviceNode()

    new_status = 'The devices behavior tree will set the status.'
    current_status = device.data(col.STATUS)
    device.setData(col.STATUS, new_status)
    assert device.data(col.STATUS) == new_status

def old_test_DeviceNode_iconLayerList():
    device = DeviceNode()
    icon_node = DeviceIconNode()
    icon_node.setData(col.SVG, 'linuxnano/resources/icons/valves/valve.svg')

    device.addChild(icon_node)

    assert device.iconLayerList().names == ['closed', 'closing', 'open', 'opening', 'fault']



########## DeviceIconNode ##########
def test_DeviceIconNode_typeInfo():
    node = DeviceIconNode()
    assert node.typeInfo() == typ.DEVICE_ICON_NODE

def test_DeviceIconNode_setData():
    device  = DeviceNode()
    node = DeviceIconNode()
    device.addChild(node)

    node.setData(col.SVG, 'linuxnano/resources/icons/valves/valve.svg')
    node.setData(col.LAYER, 'closing')
    node.setData(col.X, 51)
    node.setData(col.Y, 57)
    node.setData(col.SCALE, 1.12)
    node.setData(col.ROTATION, 90)

    node.setData(col.HAS_TEXT, True)
    node.setData(col.TEXT, 'a word')
    node.setData(col.TEXT_X, 63)
    node.setData(col.TEXT_Y, 60)
    node.setData(col.FONT_SIZE, 18)

    assert node.data(col.SVG) == 'linuxnano/resources/icons/valves/valve.svg'
    assert node.data(col.LAYER) == 'closing'
    assert node.data(col.X) == 51
    assert node.data(col.Y) == 57
    assert node.data(col.SCALE) == 1.12
    assert node.data(col.ROTATION) == 90

    assert node.data(col.HAS_TEXT) == True
    assert node.data(col.TEXT) == 'a word'
    assert node.data(col.TEXT_X) == 63
    assert node.data(col.TEXT_Y) == 60
    assert node.data(col.FONT_SIZE) == 18


def test_DeviceIconNode_layers():
    node = DeviceIconNode()
    node.setData(col.SVG, 'linuxnano/resources/icons/valves/valve.svg')

    assert node.layers().names == ['closed', 'closing', 'open', 'opening', 'fault']


########## HalNode ##########
#TODO: signalName or move that to the manual file

def test_HalNode_typeInfo():
    node = HalNode()
    with pytest.raises(Exception) as e_info:
        node.typeInfo()


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
    assert node.typeInfo() == typ.D_IN_NODE

def test_DigitalInputNode_value():
    node = DigitalInputNode()

    node.offName = 'down'
    assert node.offName == 'down'

    node.onName = 'up'
    assert node.onName == 'up'

    node.setData(col.VALUE, False)
    assert node.data(col.VALUE) == False

    node.setData(col.VALUE, True)
    assert node.data(col.VALUE) == True


def test_DigitalInputNode_setData():
    HalNode.hal_pins.append(('d_in_1', 'bit', 'OUT'))
    HalNode.hal_pins.append(('d_in_2', 'bit', 'OUT'))
    HalNode.hal_pins.append(('d_out_1', 'bit', 'IN'))
    HalNode.hal_pins.append(('d_out_2', 'bit', 'IN'))

    node = DigitalInputNode()

    node.setData(col.HAL_PIN, 2)
    assert node.data(col.HAL_PIN) == 2 #uses an index
    assert node.data(col.HAL_PIN_TYPE) == 'bit'

    node.setData(col.HAL_PIN, 1)
    assert node.data(col.HAL_PIN) == 1 #uses an index
    assert node.data(col.HAL_PIN_TYPE) == 'bit'

    assert node.halPins().names[0] == ''
    assert node.halPins().names[1] == 'd_in_1'
    assert node.halPins().names[2] == 'd_in_2'

########## DigitalOutputNode ##########
def test_DigitalOutputNode_typeInfo():
    node = DigitalOutputNode()
    assert node.typeInfo() == typ.D_OUT_NODE

def test_DigitalOutputNode_valueName():
    node = DigitalOutputNode()

    node.offName = 'down'
    assert node.offName == 'down'

    node.onName = 'up'
    assert node.onName == 'up'

    node.setData(col.VALUE, False)
    assert node.data(col.VALUE) == False

    node.setData(col.VALUE, True)
    assert node.data(col.VALUE) == True


def test_DigitalOutputNode_setData():
    HalNode.hal_pins.append(('d_in_1', 'bit', 'OUT'))
    HalNode.hal_pins.append(('d_in_2', 'bit', 'OUT'))
    HalNode.hal_pins.append(('d_out_1', 'bit', 'IN'))
    HalNode.hal_pins.append(('d_out_2', 'bit', 'IN'))

    node = DigitalOutputNode()
    node.setData(col.HAL_PIN, 2)
    assert node.data(col.HAL_PIN) == 2 #uses an index
    assert node.data(col.HAL_PIN_TYPE) == 'bit'
    node.setData(col.HAL_PIN, 1)
    assert node.data(col.HAL_PIN) == 1 #uses an index
    assert node.data(col.HAL_PIN_TYPE) == 'bit'

    assert node.halPins().names[0] == ''
    assert node.halPins().names[1] == 'd_out_1'
    assert node.halPins().names[2] == 'd_out_2'


########## AnalogInputNode ##########
def test_AnalogInputNode_typeInfo():
    node = AnalogInputNode()
    assert node.typeInfo() == typ.A_IN_NODE

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

    node.setData(col.HAL_VALUE, .12)
    assert node.value() == 1.488
    assert node.data(col.VALUE) == 1.488



def test_AnalogInputNode_value():
    node = AnalogInputNode()
    cal = [['hal_value','gui_value'],[0.0,0.0],[ 10.0, 500.0]]
    node.calibrationTableData = cal

    node.setData(col.HAL_VALUE, 1.0)
    assert node.value() == 50
    assert node.data(col.VALUE) == 50

    node.setData(col.HAL_VALUE, 1.5)
    assert node.value() == 75
    assert node.data(col.VALUE) == 75

def test_AnalogInputNode_displayToHal():
    node = AnalogInputNode()
    cal = [['hal_value','gui_value'],[0.0,0.0],[ 10.0, 500.0]]
    node.calibrationTableData = cal

    node.setData(col.HAL_VALUE, 1.75)
    assert node.data(col.HAL_VALUE) == 1.75
    assert node.displayToHal(node.value()) == 1.75


def test_AnalogInputNode_setData():
    node = AnalogInputNode()
    cal = [['hal_value','gui_value'],[0.0,0.0],[ 10.0, 500.0]]
    node.calibrationTableData = cal

    node.setData(col.HAL_VALUE, 1.5)
    node.setData(col.VALUE, "can't set this")
    node.setData(col.UNITS, 'mTorr')
    node.setData(col.DISPLAY_DIGITS, 5)
    node.setData(col.DISPLAY_SCIENTIFIC, True)
    node.setData(col.CALIBRATION_TABLE_MODEL, "can't set this")

    assert node.data(col.HAL_VALUE) == 1.5
    assert node.data(col.VALUE) == 75
    assert node.data(col.UNITS) == 'mTorr'
    assert node.data(col.DISPLAY_DIGITS) == 5
    assert node.data(col.DISPLAY_SCIENTIFIC) == True
    assert type(node.data(col.CALIBRATION_TABLE_MODEL)) == type(CalibrationTableModel())


########## AnalogOutputNode ##########
def test_AnalogOutputNode_typeInfo():
    node = AnalogOutputNode()
    assert node.typeInfo() == typ.A_OUT_NODE


########## BoolVarNode ##########
def test_BoolVarNode_typeInfo():
    node = BoolVarNode()
    assert node.typeInfo() == typ.BOOL_VAR_NODE

def test_BoolVarNode_setData():
    node = BoolVarNode()

    node.setData(col.VALUE, True)
    node.setData(col.ENABLE_MANUAL, True)
    assert node.data(col.VALUE) == True
    assert node.data(col.ENABLE_MANUAL) == True

    node.setData(col.VALUE, False)
    node.setData(col.ENABLE_MANUAL, False)
    assert node.data(col.VALUE) == False
    assert node.data(col.ENABLE_MANUAL) == False

    node.setData(col.OFF_NAME, 'OPEN')
    node.setData(col.ON_NAME, 'CLOSE')
    assert node.data(col.OFF_NAME) == 'OPEN'
    assert node.data(col.ON_NAME) == 'CLOSE'

    #view only
    node.setData(col.VIEW_ONLY, False)
    assert node.data(col.VIEW_ONLY) == False
    node.setData(col.VIEW_ONLY, True)
    assert node.data(col.VIEW_ONLY) == True

########## FloatVarNode ##########
def test_FloatVarNode_typeInfo():
    node = FloatVarNode()
    assert node.typeInfo() == typ.FLOAT_VAR_NODE

def test_FloatVarNode_setData():
    node = FloatVarNode()

    node.setData(col.UNITS, 'mTorr')
    node.setData(col.DISPLAY_DIGITS, 5)
    node.setData(col.DISPLAY_SCIENTIFIC, True)

    assert node.data(col.UNITS) == 'mTorr'
    assert node.data(col.DISPLAY_DIGITS) == 5
    assert node.data(col.DISPLAY_SCIENTIFIC) == True

    #Value must be between min/max
    node.min = -10.0
    node.max = 10.0

    assert node.min == -10.0
    assert node.max == 10.0

    node.setData(col.VALUE, 1.234)
    assert node.data(col.VALUE) == 1.234

    node.setData(col.VALUE, -991.234)
    assert node.data(col.VALUE) == -10.0

    node.setData(col.VALUE, 12.0)
    assert node.data(col.VALUE) == 10.0

    #min
    node.setData(col.MIN, -100.1)
    assert node.data(col.MIN) == -100.1

    #max
    node.setData(col.MAX, 100.1)
    assert node.data(col.MAX) == 100.1

    node.setData(col.VALUE, 102)
    assert node.data(col.VALUE) == 100.1

    #man_enable
    node.setData(col.ENABLE_MANUAL, True)
    assert node.data(col.ENABLE_MANUAL) == True

    node.setData(col.ENABLE_MANUAL, False)
    assert node.data(col.ENABLE_MANUAL) == False

    #view only
    node.setData(col.VIEW_ONLY, False)
    assert node.data(col.VIEW_ONLY) == False
    node.setData(col.VIEW_ONLY, True)
    assert node.data(col.VIEW_ONLY) == True
