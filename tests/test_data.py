#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pytest
import ast
import xml.etree.ElementTree as ET
from PyQt5 import QtCore, QtWidgets, QtGui

from linuxnano.flags import TestingFlags
from linuxnano.strings import strings

from linuxnano.data import Node, ToolNode, SystemNode, DeviceNode, DeviceIconNode, HalNode, DigitalInputNode, DigitalOutputNode, AnalogInputNode, AnalogOutputNode
from linuxnano.digital_state_table_model import DigitalStateTableModel
from linuxnano.analog_state_table_model import AnalogStateTableModel
from linuxnano.calibration_table_model import CalibrationTableModel
from linuxnano.device_state_table_model import DeviceStateTableModel



@pytest.fixture()
def win():
    win = QtWidgets.QWidget()
    win.resize(600,600)
    win.setWindowTitle("State Table View")
    win.show()

    yield win




########## Node ##########
def test_node_attrs():
    node = Node()
    assert node.attrs() == {'description': '', 'name': 'unknown'}
    

def test_node_asXml():
    root = Node()
    child_1 = Node()
    child_2 = Node()

    root.addChild(child_1)
    root.addChild(child_2)
    xml1 = '''<root>\n    <root description="" name="unknown"/>\n    <root description="" name="unknown"/>\n</root>\n'''    
    xml2 = '''<root>\n    <root name="unknown" description=""/>\n    <root name="unknown" description=""/>\n</root>\n'''    

    #For some reason the xml properties order are random, there's a qSetGlobalQHashSeed but I can't import QHash
    assert root.asXml() in [xml1, xml2]
    

def test_node_loadAttribFromXML():
    node = Node()

    tree = ET.fromstring("<root><Tool_Node name='A name'></Tool_Node></root>")

    for tool_item in tree.findall(strings.TOOL_NODE):
        node.loadAttribFromXML(tool_item)

    assert node.name == "A name"

    

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

def test_node_children():
    root = Node()
    child_1 = Node()
    child_2 = Node()
    child_3 = Node()

    root.addChild(child_1)
    root.addChild(child_2)
    root.addChild(child_3)

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

    root.removeChild(1)
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
    root.setData(0, "my name")
    root.setData(1, "typeinfo is hard coded")
    root.setData(2, "my description")
    
    assert root.data(0) == "my name"
    assert root.data(1) == "root"
    assert root.data(2) == "my description"
    
def test_node_name_property():
    root = Node()
    root.name = "my name"
    assert root.name == "my name"

def test_node_description_property():
    root = Node()
    root.description = "my description"
    assert root.description == "my description"

def test_node_log():
    root    = Node()
    child_1 = Node()
    child_2 = Node()
    child_3 = Node()
    
    root.addChild(child_1)
    root.addChild(child_2)
    root.addChild(child_3)

    assert isinstance(root.log(), str)


########## ToolNode ##########
def test_ToolNode_typeInfo():
    tool  = ToolNode()
    assert tool.typeInfo() == strings.TOOL_NODE

def test_ToolNode_iconResource():
    tool  = ToolNode()
    assert tool.iconResource() == strings.TREE_ICON_TOOL_NODE


########## SystemNode ##########
def test_SystemNode_typeInfo():
    system  = SystemNode()
    assert system.typeInfo() == strings.SYSTEM_NODE

def test_SystemNode_iconResource():
    system  = SystemNode()
    assert system.iconResource() == strings.TREE_ICON_SYSTEM_NODE

def test_SystemNode_setData():
    node = SystemNode()
    node.setData(0, "my name")
    node.setData(1, "typeinfo is hard coded")
    node.setData(2, "my description")
    node.setData(10, strings.DEFAULT_SYSTEM_BACKGROUND) 
    
    assert node.data(0) == "my name"
    assert node.data(1) == strings.SYSTEM_NODE
    assert node.data(2) == "my description"
    assert node.data(10) == strings.DEFAULT_SYSTEM_BACKGROUND

def test_SystemNode_backgroundSVG_property():
    node = SystemNode()
    
    assert node.backgroundSVG == strings.DEFAULT_SYSTEM_BACKGROUND
    node.backgroundSVG = "invalid file path"
    assert node.backgroundSVG == strings.DEFAULT_SYSTEM_BACKGROUND
   


########## DeviceNode ##########
def test_DeviceNode_typeInfo():
    device  = DeviceNode()
    assert device.typeInfo() == strings.DEVICE_NODE

def test_DeviceNode_iconResource():
    device  = DeviceNode()
    assert device.iconResource() == strings.TREE_ICON_DEVICE_NODE

def test_DeviceNode_addChild():
    device  = DeviceNode()
    d_out = DigitalOutputNode()

    device.addChild(d_out)
    assert d_out == device.child(0)

def test_node_insertChild():
    device  = DeviceNode()
    d_out_1 = DigitalOutputNode()
    d_out_2 = DigitalOutputNode()
    d_out_3 = DigitalOutputNode()
    
    device.addChild(d_out_1)
    device.addChild(d_out_3)
    

    device.insertChild(1,d_out_2)

    assert d_out_1 == device.child(0)
    assert d_out_2 == device.child(1)
    assert d_out_3 == device.child(2)

def test_node_removeChild():
    device  = DeviceNode()
    d_out_1 = DigitalOutputNode()
    d_out_2 = DigitalOutputNode()
    d_out_3 = DigitalOutputNode()
    

    device.addChild(d_out_1)
    device.addChild(d_out_2)
    device.addChild(d_out_3)


    device.removeChild(1)
    assert device.childCount() == 2
    
    device.removeChild(1)
    assert device.childCount() == 1

    device.removeChild(1)
    assert device.childCount() == 1
        
    device.removeChild(0)
    assert device.childCount() == 0


def test_DeviceNode_deviceStateTableModel():
    device  = DeviceNode()
    assert type(device.deviceStateTableModel()) == type(DeviceStateTableModel())



############ TODO ##################33
#def test_DeviceNode_state():
#    device  = DeviceNode()
#    device.state()


def test_DeviceNode_halNodeChanged():
    device  = DeviceNode()
    d_out = DigitalOutputNode()

    xml_string = "[['state','gui_name','is_used'],[0, 'Off',True],[1, 'On',True]]"
    d_out.stateTableData = xml_string
    
    device.addChild(d_out)
    
    #I guess manually call halNodeChanged?
    device.halNodeChanged()


#TODO Shouldn't be able to directly set status
def test_DeviceNode_setData():
    device  = DeviceNode()

    #TODO Shouldn't be able to directly set status
    current_status = device.data(10)
    device.setData(10, 'cant edit this way')
    assert current_status == device.data(10)

    #Can't change the table model
    current_model = device.data(15)
    new_model = DeviceStateTableModel()
    device.setData(15, new_model)
    assert device.data(15) == current_model



def test_DeviceNode_iconLayerList():
    device = DeviceNode()
    
    icon_node = DeviceIconNode()
    icon_node.setData(10, 'linuxnano/resources/icons/valves/valve.svg')

    device.addChild(icon_node)
   
    assert device.iconLayerList().names == ['closed', 'closing', 'open', 'opening', 'fault']




def test_DeviceNode_deviceStateTableData():
    xml_string = "[['state','gui_name','is_used'],[0, 'Off',True],[1, 'On',True]]"
    
    d_out = DigitalOutputNode()
    d_out.stateTableData = xml_string

    device  = DeviceNode()
    device.addChild(d_out)

    xml_string_device = "[['state', 'status', 'icon_layer', 'is_warning', 'warning_timeout', 'warning_message', 'is_alarm', 'alarm_timeout', 'alarm_message','triggers_action', 'action_timeout', 'action', 'log_entrance'],[0, 'Close', 'close', False,  0,'', False,  0,'', False, 0, None,  True],[1, 'Open' ,  'open',  True, 10, 'taking too long',  True, 20, 'failed to open', False, 0, None, False]]"


    device.deviceStateTableData = xml_string_device
    assert device.deviceStateTableData == ast.literal_eval(xml_string_device)









########## DeviceIconNode ##########
def test_DeviceIconNode_typeInfo():
    node = DeviceIconNode()
    assert node.typeInfo() == strings.DEVICE_ICON_NODE
   
def test_DeviceIconNode_iconResource():
    node = DeviceIconNode()
    assert node.iconResource() == strings.TREE_ICON_DEVICE_ICON_NODE
   
  
def test_DeviceIconNode_setData():
    node = DeviceIconNode()

    device  = DeviceNode()
    d_out_1 = DigitalOutputNode()
    d_out_2 = DigitalOutputNode()
    d_out_3 = DigitalOutputNode()
   
    a_in_1 = AnalogInputNode()
    a_in_2 = AnalogInputNode()

    device.addChild(d_out_1)
    device.addChild(d_out_2)
    device.addChild(d_out_3)
    device.addChild(a_in_1)
    device.addChild(a_in_2)
    device.addChild(node)
    
    a_in_1.setData(0, 'AnalogName')
    a_in_2.setData(0, 'AnalogName2')

    
    node.setData(10, 'linuxnano/resources/icons/valves/valve.svg')
    node.setData(11, 'closing')
    node.setData(14, 51)
    node.setData(15, 57)
    node.setData(16, 1.12)
    node.setData(17, 90)
    node.setData(18, 1) #Connected to a QComboBox so it uses enum and an index 
    node.setData(19, 63)
    node.setData(20, 60)
    node.setData(21, 18)
    
    assert node.data(10) == 'linuxnano/resources/icons/valves/valve.svg'
    assert node.data(11) == 'closing'
    assert node.data(14) == 51
    assert node.data(15) == 57
    assert node.data(16) == 1.12 
    assert node.data(17) == 90 
    assert node.data(18) == 1 #Connected to a QComboBox so it uses enum and an index 
    assert node.data(19) == 63
    assert node.data(20) == 60
    assert node.data(21) == 18

def test_DeviceIconNode_numberNodes():
    node = DeviceIconNode()

    device  = DeviceNode()
    d_out_1 = DigitalOutputNode()
    a_in_1  = AnalogInputNode()
    a_in_2  = AnalogInputNode()

    device.addChild(d_out_1)
    device.addChild(a_in_1)
    device.addChild(a_in_2)
    device.addChild(node)
    
    a_in_1.setData(0, 'Pressure')
    a_in_2.setData(0, 'Flow')

    assert node.numberNodes().names == ['None', 'Pressure', 'Flow']
 
def test_DeviceIconNode_layers():
    node = DeviceIconNode()
    node.setData(10, 'linuxnano/resources/icons/valves/valve.svg')
    
    assert node.layers().names == ['closed', 'closing', 'open', 'opening', 'fault']
   



########## HalNode ##########
def test_HalNode_typeInfo():
    node = HalNode()
    with pytest.raises(Exception) as e_info:
        node.typeInfo()


########## DigitalInputNode ##########
#Cant add generic HalNode to a device so must test name function like this
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

def test_DigitalInputNode_iconResource():
    node = DigitalInputNode()
    assert node.iconResource() == strings.TREE_ICON_D_IN_NODE

def test_DigitalInputNode_stateTableModel():
    node = DigitalInputNode()
    assert type(node.stateTableModel()) == type(DigitalStateTableModel())

def test_DigitalInputNode_numberOfStates():
    node = DigitalInputNode()
    
    xml_string = "[['state','gui_name'],[0, 'Button 1'],[1, 'Button 2'], [2, 'Button 3'], [3, 'Button 4']]"
    node.stateTableData = xml_string

    assert node.numberOfStates() == 4
    assert node.stateTableData == ast.literal_eval(xml_string)
    
    xml_string = "[['state','gui_name'],[0, 'Off'],[1, 'On']]"
    node.stateTableData = xml_string
    assert node.numberOfStates() == 2
    assert node.stateTableData == ast.literal_eval(xml_string)

def test_DigitalInputNode_states():
    node = DigitalInputNode()
    
    xml_string = "[['state','gui_name'],[0, 'Button 1'],[1, 'Button 2'],[2, 'Button 3'],[3, 'Button 4']]"
    node.stateTableData = xml_string
    
    states = ['Button 1','Button 2','Button 3','Button 4']
    assert node.states() == states

def test_DigitalInputNode_stateTableData():
    good_xml = "[['state','gui_name'],[0, 'Off'],[1, 'On']]"
    malformed_xml = "[['state','gui_name'],[0, 'Off'],[1, 'On']]]"
  
    node = DigitalInputNode()
    node.stateTableData = good_xml
    assert node.stateTableData == ast.literal_eval(good_xml)
    node.stateTableData = malformed_xml
    assert node.stateTableData == ast.literal_eval(good_xml)


########## DigitalOutputNode ##########
def test_DigitalOutputNode_typeInfo():
    node = DigitalOutputNode()
    assert node.typeInfo() == strings.DIGITAL_OUTPUT_NODE

def test_DigitalOutputNode_iconResource():
    node = DigitalOutputNode()
    assert node.iconResource() == strings.TREE_ICON_D_OUT_NODE

def test_DigitalOutputNode_stateTableModel():
    node = DigitalOutputNode()
    assert type(node.stateTableModel()) == type(DigitalStateTableModel())

def test_DigitalOutputNode_numberOfStates():
    node = DigitalOutputNode()
    
    xml_string = "[['state','gui_name','is_used'],[0, 'Button 1',True],[1, 'Button 2',True],[2, 'Button 3',True],[3, 'NA',False]]"
    node.stateTableData = xml_string

    assert node.numberOfStates() == 4
    assert node.stateTableData == ast.literal_eval(xml_string)
    
    xml_string = "[['state','gui_name','is_used'],[0, 'Off',True],[1, 'On',True]]"
    node.stateTableData = xml_string
    assert node.numberOfStates() == 2
    assert node.stateTableData == ast.literal_eval(xml_string)

def test_DigitalOutputNode_states():
    node = DigitalOutputNode()
    
    xml_string = "[['state','gui_name','is_used'],[0, 'Button 1',True],[1, 'Button 2',True],[2, 'Button 3',True],[3, 'NA',False]]"
    node.stateTableData = xml_string
    
    states = ['Button 1','Button 2','Button 3','NA']
    assert node.states() == states

def test_DigitalOutputNode_manualDisplayType():
    node = DigitalOutputNode()
    
    node.manualDisplayType = strings.MANUAL_DISPLAY_BUTTONS
    assert node.manualDisplayType == strings.MANUAL_DISPLAY_BUTTONS
    
    node.manualDisplayType = strings.MANUAL_DISPLAY_COMBO_BOX
    assert node.manualDisplayType == strings.MANUAL_DISPLAY_COMBO_BOX

    node.manualDisplayType = 'bad_option'
    assert node.manualDisplayType != 'bad_option'

def test_DigitalOutputNode_stateTableData():
    good_xml = "[['state','gui_name', 'is_used'],[0, 'Off',False],[1, 'On',False]]"
    malformed_xml = "[['state','gui_name', 'is_used'],[0, 'Off',False],[1, 'On',False']]"
   
    node = DigitalOutputNode()
    node.stateTableData = good_xml
    assert node.stateTableData == ast.literal_eval(good_xml)
    node.stateTableData = malformed_xml
    assert node.stateTableData == ast.literal_eval(good_xml)



########## AnalogInputNode ##########
def test_AnalogInputNode_typeInfo():
    node = AnalogInputNode()
    assert node.typeInfo() == strings.A_IN_NODE

def test_AnalogInputNode_iconResource():
    node = AnalogInputNode()
    assert node.iconResource() == strings.TREE_ICON_A_IN_NODE

def test_AnalogInputNode_stateTableModel():
    node = AnalogInputNode()
    assert type(node.stateTableModel()) == type(AnalogStateTableModel())

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

    assert node.displayDigits == strings.A_IN_DISPLAY_DIGITS_DEFAULT
   
    node.displayDigits = -1
    assert node.displayDigits == 0
    
    node.displayDigits = 9991
    assert node.displayDigits == strings.A_IN_DISPLAY_DIGITS_MAX

def test_AnalogInputNode_displayScientific():
    node = AnalogInputNode()
    assert node.displayScientific == False
   
    node.displayScientific = True
    assert node.displayScientific == True
    
    node.displayScientific = 'ham'
    assert node.displayScientific == False

def test_AnalogInputNode_stateTableData():
    node = AnalogInputNode()
    
    good_xml      = "[['state','greater_than', 'gui_name'],[0, None, 'HiVac'],[1, 2.00, 'Vac'],[2, 3.00, 'Atmo']]"
    malformed_xml = "[['state','greater_than', 'gui_name'],['some', None, 'HiVac'],[1, 2.00, 'Vac'],[2, 3.00, 'Atmo']]"
   
    node.stateTableData = good_xml
    assert node.stateTableData == ast.literal_eval(good_xml)
    node.stateTableData = malformed_xml
    assert node.stateTableData == ast.literal_eval(good_xml)

def test_AnalogInputNode_calibrationTableData():
    node = AnalogInputNode()
    good_xml      = "[['hal_value','gui_value'],[0.0,0.0],[ 1.0, 12.4],[2, 24.8]]"
    malformed_xml = "[['hal_value','gui_value'],[0.0,0.0],[-1.0, 12.4],[2, 24.8]]"
    
    node.calibrationTableData = good_xml
    assert node.calibrationTableData == ast.literal_eval(good_xml)
    node.calibrationTableData = malformed_xml
    assert node.calibrationTableData == ast.literal_eval(good_xml)

def test_AnalogInputNode_states():
    node = AnalogInputNode()
    xml_string = "[['state','greater_than', 'gui_name'],[0, None, 'HiVac'],[1, 2.00, 'Vac'],[2, 3.00, 'Atmo']]"
    node.stateTableData = xml_string
    
    states = ['HiVac','Vac','Atmo']
    assert node.states() == states

def test_AnalogInputNode_numberOfStates():
        node = AnalogInputNode()
        
        xml_string = "[['state','greater_than', 'gui_name'],[0, None, 'HiVac'],[1, 2.00, 'Vac'],[2, 3.00, 'Atmo']]"
    
        node.stateTableData = xml_string
    
        assert node.numberOfStates() == 3
        assert node.stateTableData == ast.literal_eval(xml_string)
        
        xml_string = "[['state','greater_than', 'gui_name'],[0, None, 'HiVac'],[1, 2.00, 'Vac']]"
        node.stateTableData = xml_string
        assert node.numberOfStates() == 2
        assert node.stateTableData == ast.literal_eval(xml_string)

#FIXME - need to revisit this whole enum thing...
def test_AnalogInputNode_scaleType():
    node = AnalogInputNode()

    for scale_type in strings.ANALOG_SCALE_TYPES.names:
        #print(scale_type)
        #print(strings.ANALOG_SCALE_TYPES.names.index(scale_type))
        node.scaleType = scale_type
        assert node.scaleType == scale_type

    node.scaleType = 'ham'
    assert node.scaleType == scale_type


########## AnalogOutputNode ##########
def test_AnalogOutputNode_typeInfo():
    node = AnalogOutputNode()
    assert node.typeInfo() == strings.A_OUT_NODE

def test_AnalogOutputNode_iconResource():
    node = AnalogOutputNode()
    assert node.iconResource() == strings.TREE_ICON_A_OUT_NODE

def test_AnalogOutputNode_stateTableModel():
    node = AnalogOutputNode()
    assert type(node.stateTableModel()) == type(AnalogStateTableModel())

def test_AnalogOutputNode_calibrationTableModel():
    node = AnalogOutputNode()
    assert type(node.calibrationTableModel()) == type(CalibrationTableModel())

def test_AnalogOutputNode_units():
    node = AnalogOutputNode()
    node.units = 'sccm'
    assert node.units == 'sccm'

    node.units = 'Torr'
    assert node.units == 'Torr'

def test_AnalogOutputNode_displayDigits():
    node = AnalogOutputNode()
    assert node.displayDigits == strings.A_OUT_DISPLAY_DIGITS_DEFAULT
   
    node.displayDigits = -1
    assert node.displayDigits == 0
    
    node.displayDigits = 9991
    assert node.displayDigits == strings.A_OUT_DISPLAY_DIGITS_MAX

def test_AnalogOutputNode_displayScientific():
    node = AnalogOutputNode()
    assert node.displayScientific == False
   
    node.displayScientific = True
    assert node.displayScientific == True
    
    node.displayScientific = 'ham'
    assert node.displayScientific == False

def test_AnalogOutputNode_stateTableData():
    node = AnalogOutputNode()
    
    good_xml      = "[['state','greater_than', 'gui_name'],[0, None, 'HiVac'],[1, 2.00, 'Vac'],[2, 3.00, 'Atmo']]"
    malformed_xml = "[['state','greater_than', 'gui_name'],['some', None, 'HiVac'],[1, 2.00, 'Vac'],[2, 3.00, 'Atmo']]"
   
    node.stateTableData = good_xml
    assert node.stateTableData == ast.literal_eval(good_xml)
    node.stateTableData = malformed_xml
    assert node.stateTableData == ast.literal_eval(good_xml)

def test_AnalogOutputNode_calibrationTableData():
    node = AnalogOutputNode()
    good_xml      = "[['hal_value','gui_value'],[0.0,0.0],[ 1.0, 12.4],[2, 24.8]]"
    malformed_xml = "[['hal_value','gui_value'],[0.0,0.0],[-1.0, 12.4],[2, 24.8]]"
    
    node.calibrationTableData = good_xml
    assert node.calibrationTableData == ast.literal_eval(good_xml)
    node.calibrationTableData = malformed_xml
    assert node.calibrationTableData == ast.literal_eval(good_xml)

def test_AnalogOutputNode_states():
    node = AnalogOutputNode()
    xml_string = "[['state','greater_than', 'gui_name'],[0, None, 'HiVac'],[1, 2.00, 'Vac'],[2, 3.00, 'Atmo']]"
    node.stateTableData = xml_string
    
    states = ['HiVac','Vac','Atmo']
    assert node.states() == states

#FIXME - need to revisit this whole enum thing...
def test_AnalogOutputNode_scaleType():
    node = AnalogOutputNode()
    for scale_type in strings.ANALOG_SCALE_TYPES.names:
        node.scaleType = scale_type
        assert node.scaleType == scale_type

    node.scaleType = 'ham'
    assert node.scaleType == scale_type

#FIXME - need to revisit this whole enum thing...
def test_AnalogOutputNode_manualDisplayType():
    node = AnalogOutputNode()
    for display_type in strings.ANALOG_MANUAL_DISPLAY_TYPES.names:
        node.manualDisplayType = display_type
        assert node.manualDisplayType == display_type

    node.manualDisplayType = 'ham'
    assert node.manualDisplayType == display_type

def test_AnalogOutputNode_numberOfStates():
    node = AnalogOutputNode()
    
    xml_string = "[['state','greater_than', 'gui_name'],[0, None, 'HiVac'],[1, 2.00, 'Vac'],[2, 3.00, 'Atmo']]"
    node.stateTableData = xml_string

    assert node.numberOfStates() == 3
    assert node.stateTableData == ast.literal_eval(xml_string)
    
    xml_string = "[['state','greater_than', 'gui_name'],[0, None, 'HiVac'],[1, 2.00, 'Vac']]"
    node.stateTableData = xml_string
    assert node.numberOfStates() == 2
    assert node.stateTableData == ast.literal_eval(xml_string)






