#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pytest

from PyQt5 import QtCore, QtWidgets

from linuxnano.flags import TestingFlags
from linuxnano.strings import strings

from linuxnano.tool_model import ToolModel
import xml.etree.ElementTree as ET


@pytest.fixture()
def win():
    win = QtWidgets.QWidget()
    win.resize(600,600)
    win.setWindowTitle("State Table View")
    win.show()

    yield win

@pytest.fixture()
def good_xml_1 ():
    xml ='''
        <root>
            <Tool_Node description='for testing' name='[Awesome Tool'>
                <System_Node description='Main Chamber' name='Chamber A' backgroundSVG='/media/psf/linuxNano/resources/icons/evaporator_background.svg'>
                    <Device_Node
                        name='Foreline Valve'
                        description='a simple valve with limit switches'
                        deviceStateTableData="[['state', 'status', 'icon_layer', 'is_warning', 'warning_timeout', 'warning_message', 'is_alarm', 'alarm_timeout', 'alarm_message',
                                                                                                                            'triggers_action', 'action_timeout', 'action', 'log_entrance'],
    
                                               [0, 'Opening' , 'opening' ,  True, 10, 'taking too long',  True, 20,                                   'failed to open', False, 0, None, False],
                                               [1, 'Open'    , 'open'    , False,  0,                '', False,  0,                                                 '', False, 0, None,  True],
                                               [2, 'Opening' , 'opening' ,  True, 10, 'taking too long',  True, 20,                                   'failed to open', False, 0, None, False],
                                               [3, 'Fault'   , 'fault'   , False,  0,                '',  True,  0,          'cannot have both limit switches at once', False, 0, None, False],
                                               
                                               [4, 'Closing' , 'closing' ,  True, 10, 'taking too long',  True, 20,                          'failed to close', False, 0, None, False],
                                               [5, 'Closing' , 'closing' ,  True, 10, 'taking too long',  True, 20,                          'failed to close', False, 0, None,  True],
                                               [6, 'Closed'  , 'closed'  , False,  0,                '', False,  0,                                         '', False, 0, None, False],
                                               [7, 'Fault'   , 'fault'   , False,  0,                '',  True,  0,  'cannot have both limit switches at once', False, 0, None, False]]"

                    >

                        <Device_Icon_Node svg='linuxnano/resources/icons/valves/valve.svg' x='25' y='35' scale='1.0' rotation='0' numberNode='Pressure' />
                        <Digital_Output_Node description='Opens the valve' name='Output' stateTableData="[['state', 'gui_name','is_used'], [0, 'Open',True], [1, 'Close',True]]"/>
                        <Digital_Input_Node description='Closed limit switch' name='closed_limit' stateTableData="[['state', 'gui_name'], [0, 'is_not_open'], [1, 'is_open']]"/> 
                        <Digital_Input_Node description='Open limit switch' name='open_limit' stateTableData="[['state', 'gui_name'], [0, 'is_not_closed'], [1, 'is_closed']]"/> 
                    </Device_Node>

                    <Device_Node
                        name='Simple Valve'
                        description='a valve'
                        deviceStateTableData="[['state', 'status', 'icon_layer', 'is_warning', 'warning_timeout', 'warning_message', 'is_alarm', 'alarm_timeout', 'alarm_message',
                                                                                                                            'triggers_action', 'action_timeout', 'action', 'log_entrance'],
    
              
                                               [0, 'Open'  , 'open'  , False, 0, '', False, 0, '', False, 0, None, True],
                                               [1, 'Closed', 'closed', False, 0, '', False,0, '', False, 0, None, True]]"
                                               

                    >

                        <Device_Icon_Node svg='linuxnano/resources/icons/valves/valve.svg' x='25' y='35' scale='1.0' rotation='0' numberNode='Pressure' />
                        <Digital_Output_Node description='Opens the valve' name='Output' stateTableData="[['state', 'gui_name','is_used'], [0, 'Open',True], [1, 'Close',True]]"/>
                    </Device_Node>

                    <Device_Node
                        name='MFC'
                        description='just an analog output'
                        deviceStateTableData="[['state', 'status', 'icon_layer', 'is_warning', 'warning_timeout', 'warning_message', 'is_alarm', 'alarm_timeout', 'alarm_message',
                                                                                                                            'triggers_action', 'action_timeout', 'action', 'log_entrance'],
    
              
                                               [0, 'Off' , 'open'  , False, 0, '', False, 0, '', False, 0, None, True],
                                               [1, 'On'  , 'closed', False, 0, '', False, 0, '', False, 0, None, True]]"
                                               

                    >

                        <Device_Icon_Node svg='linuxnano/resources/icons/valves/valve.svg' x='25' y='35' scale='1.0' rotation='0' numberNode='output' />
                        <Analog_Output_Node 
                            name='output' 
                            description='setpoint  0-10vdc' 
                            units='sccm' 
                            displayDigts='1' 
                            displayScientific='False' 
                            scaleType='linear' 
                            manualDisplayType='slider' 
                            stateTableData="[['state','greater_than', 'gui_name'], [0, None, 'Off'], [1, 0.001, 'On']]"
                            calibrationTableData="[['hal_value','gui_value'], [0, 1000], [5, 97.2], [7.5, .01], [10, .000001]]"
                        />
                    </Device_Node>





                </System_Node>
            </Tool_Node>
        </root>'''



    return xml

@pytest.fixture()
def tool_model_1(good_xml_1):
    tree = ET.ElementTree(ET.fromstring(good_xml_1))
    tool_model = ToolModel()
    tool_model.loadTool(tree)

    return tool_model

def test_ToolModel_init(good_xml_1):
    tree = ET.ElementTree(ET.fromstring(good_xml_1))
    tool_model = ToolModel()
    assert tool_model.loadTool(tree) is not False
    
    
def test_ToolModel_asXml(good_xml_1):
    tree = ET.ElementTree(ET.fromstring(good_xml_1))
    tool_model = ToolModel()
    tool_model.loadTool(tree)
    
    assert(isinstance(tool_model.asXml(),str))


def test_ToolModel_rowCount(tool_model_1):
    tool_index = tool_model_1.index(0, 0, QtCore.QModelIndex())
    system_index = tool_index.child(0, 0)
    device_index = system_index.child(0, 0)
    
    assert tool_model_1.rowCount(tool_index) == 1
    assert tool_model_1.rowCount(system_index) == 3
    assert tool_model_1.rowCount(device_index) == 4

def test_ToolModel_columnCount(tool_model_1):
    tool_index = tool_model_1.index(0, 0, QtCore.QModelIndex())
    assert tool_model_1.columnCount(tool_index) == 2
  
def test_ToolModel_possibleChildren(tool_model_1):
    tool_index = tool_model_1.index(0, 0, QtCore.QModelIndex())
    system_index = tool_index.child(0, 0)
    device_index = system_index.child(0, 0)

    assert tool_model_1.possibleChildren(tool_index) == [strings.SYSTEM_NODE]
    assert tool_model_1.possibleChildren(system_index) == [strings.DEVICE_NODE]
    assert tool_model_1.possibleChildren(device_index) == [strings.DEVICE_ICON_NODE, strings.D_IN_NODE, strings.D_OUT_NODE, strings.A_IN_NODE, strings.A_OUT_NODE]
    

def test_ToolModel_allowedInsertRows(tool_model_1):
    tool_index = tool_model_1.index(0, 0, QtCore.QModelIndex())
    system_index = tool_index.child(0, 0)
    device_index = system_index.child(0, 0)

    assert tool_model_1.allowedInsertRows(tool_index, strings.SYSTEM_NODE) == [0,1]
    assert tool_model_1.allowedInsertRows(system_index, strings.DEVICE_NODE) == [0,1,2,3]
    assert tool_model_1.allowedInsertRows(device_index, strings.D_IN_NODE) == [1,2,3,4]

def test_ToolModel_insertChild(tool_model_1):
    tool_index = tool_model_1.index(0, 0, QtCore.QModelIndex())
    system_index = tool_index.child(0, 0)
    device_index = system_index.child(0, 0)

    num_devices = tool_model_1.rowCount(system_index) 
    new_device_index = tool_model_1.insertChild(system_index, strings.DEVICE_NODE)
  
    assert new_device_index is not False
    assert num_devices + 1 == tool_model_1.rowCount(system_index) 


    bad_index = tool_model_1.insertChild(system_index, "Dig_Inptu_Node")
    assert bad_index == False

    bad_index = tool_model_1.insertChild(system_index, strings.DEVICE_NODE, 843)
    assert bad_index == False
    
    bad_index = tool_model_1.insertChild(system_index, strings.SYSTEM_NODE)
    assert bad_index == False


def test_ToolModel_removeRows(tool_model_1):
    tool_index = tool_model_1.index(0, 0, QtCore.QModelIndex())
    system_index = tool_index.child(0, 0)
    device_index = system_index.child(0, 0)

    num_devices = tool_model_1.rowCount(system_index) 
   
    tool_model_1.removeRows(0, 1, system_index)

    assert num_devices - 1 == tool_model_1.rowCount(system_index) 
 

    assert False == tool_model_1.removeRows(-1, 1, system_index)
    assert False == tool_model_1.removeRows('dog', 1, system_index)
    assert False == tool_model_1.removeRows(0, -10, system_index)
    assert False == tool_model_1.removeRows(0, 'cat', system_index)


def test_ToolModel_data(tool_model_1):
    tool_index = tool_model_1.index(0, 0, QtCore.QModelIndex())
    system_index = tool_index.child(0, 0)
    
    
    device_index = system_index.child(0, 0)
    name_string = 'Foreline Valve'
    assert name_string == tool_model_1.data(device_index, QtCore.Qt.DisplayRole)
    assert name_string == tool_model_1.data(device_index, QtCore.Qt.EditRole)
  
    device_index = system_index.child(1, 1)
    assert strings.DEVICE_NODE == tool_model_1.data(device_index, QtCore.Qt.DisplayRole)
    assert strings.DEVICE_NODE == tool_model_1.data(device_index, QtCore.Qt.EditRole)
   
    device_index = system_index.child(1, 2)
    desc_string = 'a valve'
    assert desc_string == tool_model_1.data(device_index, QtCore.Qt.DisplayRole)
    assert desc_string == tool_model_1.data(device_index, QtCore.Qt.EditRole)
    
def test_ToolModel_setData(tool_model_1):
    tool_index = tool_model_1.index(0, 0, QtCore.QModelIndex())
    system_index = tool_index.child(0, 0)
    
    
    device_index = system_index.child(0, 0)
    name_string = 'NEW Name Here'
    assert True == tool_model_1.setData(device_index, name_string)
    assert name_string == tool_model_1.data(device_index, QtCore.Qt.DisplayRole)
 

    device_index = system_index.child(1, 1)
    tool_model_1.setData(device_index, "Cant set") 
    assert strings.DEVICE_NODE == tool_model_1.data(device_index, QtCore.Qt.DisplayRole)
  
    device_index = system_index.child(1, 2)
    description_string = 'This is the new description for the device'
    assert True == tool_model_1.setData(device_index, description_string)
    assert description_string == tool_model_1.data(device_index, QtCore.Qt.DisplayRole)


def test_ToolModel_headerData(tool_model_1):
    assert "Name" == tool_model_1.headerData(0, QtCore.Qt.Horizontal, QtCore.Qt.DisplayRole)
    assert "Type" == tool_model_1.headerData(1, QtCore.Qt.Horizontal, QtCore.Qt.DisplayRole)

#TODO Not sure if these flags make sense currently
def test_ToolModel_flag(tool_model_1):
    tool_index = tool_model_1.index(0, 0, QtCore.QModelIndex())
    system_index = tool_index.child(0, 0)
    device_index = system_index.child(0, 0)
    
    assert tool_model_1.flags(system_index) == QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable
    assert tool_model_1.flags(device_index) == QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable

def test_ToolModel_parent(tool_model_1):
    tool_index = tool_model_1.index(0, 0, QtCore.QModelIndex())
    system_index = tool_index.child(0, 0)
    device_index = system_index.child(0, 0)
   
    assert system_index == tool_model_1.parent(device_index)
    assert tool_index == tool_model_1.parent(system_index)

#TODO Add once there's system Icons ??
#def test_ToolModel_systemIcons(tool_model_1):
#    tool_index = tool_model_1.index(0, 0, QtCore.QModelIndex())
#    system_index = tool_index.child(0, 0)
#    device_index = system_index.child(0, 0)
#  
#
#    icons = tool_model_1.systemIcons(system_index)
#
#
#    #TODO! Add once we stat using the icons again
#    assert len(icons) == 2



    
    # QtCore.Qt.DecorationRole:








