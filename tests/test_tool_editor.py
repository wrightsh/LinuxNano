#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pytest

from PyQt5 import QtCore, QtWidgets, QtGui
import xml.etree.ElementTree as ET

from linuxnano.tool_model import ToolModel
from linuxnano.tool_editor import ToolEditor, NodeEditor, SystemEditor, DeviceEditor, DeviceIconEditor, DigitalInputEditor, DigitalOutputEditor, AnalogInputEditor, AnalogOutputEditor

from linuxnano.message_box import MessageBox
from linuxnano.flags import TestingFlags


@pytest.fixture()
def win():
    win = QtWidgets.QWidget()
    win.resize(600,600)
    win.show()

    yield win

@pytest.fixture()
def good_xml_1 ():
    xml ='''
        <root>
            <Tool_Node description='for testing' name='Awesome Tool'>
                <System_Node description='Main Chamber' name='Chamber A' backgroundSVG='linuxnano/resources/icons/evaporator_background.svg'>
                    <Device_Node
                        name='Atmo Gauge'
                        description='A pressure switch'
                    >
                        <Device_Icon_Node svg='linuxnano/resources/icons/valves/valve.svg' x='25' y='35' scale='1.0' rotation='0' numberNode='Pressure_backup' />
                        <Digital_Input_Node description='Terminal block X' name='Power' stateTableData="[['state', 'gui_name'], [0, 'Off'], [1, 'On']]"/> 
                        <Digital_Input_Node description='Terminal block X' name='Door' stateTableData="[['state', 'gui_name'], [0, 'Open'], [1, 'Close']]"/>
                        <Analog_Input_Node 
                            name='Pressure' 
                            description='some signal' 
                            units='mTorr' 
                            displayDigits='1'
                            displayScientific='True' 
                            scaleType='linear' 
                            stateTableData="[['state','greater_than', 'gui_name'], [0, None, 'Open'], [1, 9.2, 'Close']]"
                            calibrationTableData="[['hal_value','gui_value'], [-10, 0], [1, 97.2], [100, 1000], [244, 1200]]"
                        />
                        <Analog_Input_Node 
                            name='Pressure_backup' 
                            description='some signal' 
                            units='Barr' 
                            displayDigts='0' 
                            displayScientific='False' 
                            scaleType='cubic_spline' 
                            stateTableData="[['state','greater_than', 'gui_name'], [0, None, 'Open'], [1, 5.2, 'Close']]"
                            calibrationTableData="[['hal_value','gui_value'], [0, 1000], [5, 97.2], [20, .01], [100, .000001]]"
                        />
                    </Device_Node>
                    <Device_Node description='the desc is here' name='Foreline Valve'>
                        <Device_Icon_Node svg='linuxnano/resources/icons/valves/valve.svg' x='25' y='35' scale='1.0' rotation='0' numberNode='Valve_angle' />
                        <Digital_Output_Node
                            name='Actuator' 
                            description='Terminal block X'
                            manualDisplayType='buttons' 
                            stateTableData="[['state', 'gui_name', 'is_used'], [0, 'Close', True], [1, 'Open', True]]"
                        /> 
                        <Digital_Output_Node 
                            name='Lock' 
                            description='Terminal block Y' 
                            manualDisplayType='combo_box' 
                            stateTableData="[['state', 'gui_name', 'is_used'], [0, 'Lock', True], [1, 'Unlock', True]]"
                        />
                        <Analog_Output_Node 
                            name='Valve_angle' 
                            description='some signal' 
                            units='%' 
                            displayDigts='1' 
                            displayScientific='False' 
                            scaleType='linear' 
                            manualDisplayType='slider' 
                            stateTableData="[['state','greater_than', 'gui_name'], [0, None, 'Open'], [1, 5.2, 'Close']]"
                            calibrationTableData="[['hal_value','gui_value'], [0, 1000], [5, 97.2], [7.5, .01], [10, .000001]]"
                        />
                        <Analog_Output_Node 
                            name='Door_angle' 
                            description='signal' 
                            units='percent' 
                            displayDigts='2' 
                            displayScientific='True' 
                            scaleType='cubic_spline' 
                            manualDisplayType='number_box' 
                            stateTableData="[['state','greater_than', 'gui_name'], [0, None, 'Open'], [1, 5.2, 'Close'], [2, 9.2, 'Jammed']]"
                            calibrationTableData="[['hal_value','gui_value'], [2, 1.01], [10, .000001]]"
                        />
                    </Device_Node>
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



def test_ToolEditor(qtbot, win, tool_model_1):
    if TestingFlags.ENABLE_MANUAL_TESTING is False: return
    win.setWindowTitle("Tool Editor Window")

    tool_editor = ToolEditor(tool_model_1)
    
    layout = QtWidgets.QVBoxLayout(win)
    layout.addWidget(tool_editor)

    qtbot.addWidget(win)
    with qtbot.waitActive(win, timeout=TestingFlags.WAIT_ACTIVE_TIMEOUT):
        pass
    MessageBox("Manual testing of the tool editor window")
    qtbot.stopForInteraction()



def test_NodeEditor(qtbot, win, tool_model_1):
    if TestingFlags.ENABLE_MANUAL_TESTING is False: return
    win.setWindowTitle("Node Editor")

    tool_index = tool_model_1.index(0, 0, QtCore.QModelIndex())
    system_index = tool_index.child(0, 0)
    device_index_1 = system_index.child(0, 0)
    device_index_2 = system_index.child(1, 0)
    device_index_3 = system_index.child(2, 0)

    editor = NodeEditor()
    editor.setModel(tool_model_1)

    editor.setSelection(system_index)
    
    layout = QtWidgets.QVBoxLayout(win)
    layout.addWidget(editor)

    qtbot.addWidget(win)
    with qtbot.waitActive(win, timeout=TestingFlags.WAIT_ACTIVE_TIMEOUT):
        pass
   
    qtbot.wait(TestingFlags.TEST_WAIT_LONG)
    editor.setSelection(device_index_1)

    qtbot.wait(TestingFlags.TEST_WAIT_LONG)
    editor.setSelection(device_index_2)
    
    MessageBox("Manual testing of the node editor window")
    qtbot.stopForInteraction()

def test_SystemEditor(qtbot, win, tool_model_1):
    if TestingFlags.ENABLE_MANUAL_TESTING is False: return
    win.setWindowTitle("System Editor")

    tool_index = tool_model_1.index(0, 0, QtCore.QModelIndex())
    system_index = tool_index.child(0, 0)

    editor = SystemEditor()
    editor.setModel(tool_model_1)

    editor.setSelection(system_index)
    
    layout = QtWidgets.QVBoxLayout(win)
    layout.addWidget(editor)

    qtbot.addWidget(win)
    with qtbot.waitActive(win, timeout=TestingFlags.WAIT_ACTIVE_TIMEOUT):
        pass

    
    MessageBox("Manual testing of the system editor window")
    qtbot.stopForInteraction()


def test_DeviceEditor(qtbot, win, tool_model_1):
    if TestingFlags.ENABLE_MANUAL_TESTING is False: return
    win.setWindowTitle("Device Editor")

    tool_index = tool_model_1.index(0, 0, QtCore.QModelIndex())
    system_index = tool_index.child(0, 0)
    device_index_1 = system_index.child(0, 0)
    device_index_2 = system_index.child(1, 0)
    device_index_3 = system_index.child(2, 0)


    editor = DeviceEditor()
    editor.setModel(tool_model_1)
    editor.setSelection(device_index_1)
    
    layout = QtWidgets.QVBoxLayout(win)
    layout.addWidget(editor)

    qtbot.addWidget(win)
    with qtbot.waitActive(win, timeout=TestingFlags.WAIT_ACTIVE_TIMEOUT):
        pass

    qtbot.wait(TestingFlags.TEST_WAIT_LONG)
    editor.setSelection(device_index_1)
    qtbot.wait(TestingFlags.TEST_WAIT_LONG)
    editor.setSelection(device_index_3)
    
    
    MessageBox("It should have just changed between 3 devices")
    MessageBox("Manual testing of the device editor window")
    qtbot.stopForInteraction()


def test_DeviceEditor(qtbot, win, tool_model_1):
    if TestingFlags.ENABLE_MANUAL_TESTING is False: return
    win.setWindowTitle("Device Editor")

    tool_index = tool_model_1.index(0, 0, QtCore.QModelIndex())
    system_index = tool_index.child(0, 0)
    device_index = system_index.child(0, 0)

    editor = DeviceEditor()
    editor.setModel(tool_model_1)

    editor.setSelection(device_index)
    
    layout = QtWidgets.QVBoxLayout(win)
    layout.addWidget(editor)

    qtbot.addWidget(win)
    with qtbot.waitActive(win, timeout=TestingFlags.WAIT_ACTIVE_TIMEOUT):
        pass

    
    MessageBox("Manual testing of the device editor window")
    qtbot.stopForInteraction()



def test_DeviceIconEditor(qtbot, win, tool_model_1):
    if TestingFlags.ENABLE_MANUAL_TESTING is False: return
    win.setWindowTitle("Device Icon Editor")

    tool_index = tool_model_1.index(0, 0, QtCore.QModelIndex())
    system_index = tool_index.child(0, 0)
    device_index = system_index.child(0, 0)
    device_icon_index_1 = device_index.child(0, 0)

    editor = DeviceIconEditor()
    editor.setModel(tool_model_1)

    editor.setSelection(device_icon_index_1)
    
    layout = QtWidgets.QVBoxLayout(win)
    layout.addWidget(editor)

    qtbot.addWidget(win)
    with qtbot.waitActive(win, timeout=TestingFlags.WAIT_ACTIVE_TIMEOUT):
        pass

    
    MessageBox("Manual testing of the device icon editor window")
    qtbot.stopForInteraction()

def test_DigitalInputEditor(qtbot, win, tool_model_1):
    if TestingFlags.ENABLE_MANUAL_TESTING is False: return
    win.setWindowTitle("Digital Input Editor")

    tool_index = tool_model_1.index(0, 0, QtCore.QModelIndex())
    system_index = tool_index.child(0, 0)
    device_index = system_index.child(0, 0)
    d_in_1_index = device_index.child(1,0)
    d_in_2_index = device_index.child(2,0)


    editor = DigitalInputEditor()
    editor.setModel(tool_model_1)
    editor.setSelection(d_in_1_index)
    
    layout = QtWidgets.QVBoxLayout(win)
    layout.addWidget(editor)

    qtbot.addWidget(win)
    with qtbot.waitActive(win, timeout=TestingFlags.WAIT_ACTIVE_TIMEOUT):
        pass

    qtbot.wait(TestingFlags.TEST_WAIT_LONG)
    editor.setSelection(d_in_2_index)
    qtbot.wait(TestingFlags.TEST_WAIT_LONG)
    editor.setSelection(d_in_1_index)
    
    
    MessageBox("It should have just changed between 2 digital input nodes")
    MessageBox("Manual testing of the digital input editor window")
    qtbot.stopForInteraction()

def test_DigitalOutputEditor(qtbot, win, tool_model_1):
    if TestingFlags.ENABLE_MANUAL_TESTING is False: return
    win.setWindowTitle("Digital Output Editor")

    tool_index = tool_model_1.index(0, 0, QtCore.QModelIndex())
    system_index = tool_index.child(0, 0)
    device_index = system_index.child(1, 0)
    d_out_1_index = device_index.child(1,0)
    d_out_2_index = device_index.child(2,0)

    editor = DigitalOutputEditor()
    editor.setModel(tool_model_1)
    editor.setSelection(d_out_1_index)
    
    layout = QtWidgets.QVBoxLayout(win)
    layout.addWidget(editor)

    qtbot.addWidget(win)
    with qtbot.waitActive(win, timeout=TestingFlags.WAIT_ACTIVE_TIMEOUT):
        pass
    
    qtbot.wait(TestingFlags.TEST_WAIT_LONG)
    editor.setSelection(d_out_2_index)
    qtbot.wait(TestingFlags.TEST_WAIT_LONG)
    editor.setSelection(d_out_1_index)
    
    MessageBox("Manual testing of the digital output editor window")
    qtbot.stopForInteraction()

def test_AnalogInputEditor(qtbot, win, tool_model_1):
    if TestingFlags.ENABLE_MANUAL_TESTING is False: return
    win.setWindowTitle("Analog Input Editor")

    tool_index = tool_model_1.index(0, 0, QtCore.QModelIndex())
    system_index = tool_index.child(0, 0)
    device_index = system_index.child(0, 0)
    a_in_1_index = device_index.child(3,0)
    a_in_2_index = device_index.child(4,0)

    editor = AnalogInputEditor()
    editor.setModel(tool_model_1)
    editor.setSelection(a_in_1_index)
    
    layout = QtWidgets.QVBoxLayout(win)
    layout.addWidget(editor)

    qtbot.addWidget(win)
    with qtbot.waitActive(win, timeout=TestingFlags.WAIT_ACTIVE_TIMEOUT):
        pass
    
    qtbot.wait(TestingFlags.TEST_WAIT_LONG)
    editor.setSelection(a_in_2_index)
    qtbot.wait(TestingFlags.TEST_WAIT_LONG)
    editor.setSelection(a_in_1_index)
    
    MessageBox("Manual testing of the analog input editor window")
    qtbot.stopForInteraction()

def test_AnalogOutputEditor(qtbot, win, tool_model_1):
    if TestingFlags.ENABLE_MANUAL_TESTING is False: return
    win.setWindowTitle("Analog Output Editor")

    tool_index = tool_model_1.index(0, 0, QtCore.QModelIndex())
    system_index = tool_index.child(0, 0)
    device_index = system_index.child(1, 0)
    a_out_1_index = device_index.child(3,0)

    a_out_2_index = device_index.child(4,0)

    editor = AnalogOutputEditor()
    editor.setModel(tool_model_1)
    editor.setSelection(a_out_1_index)
    
    layout = QtWidgets.QVBoxLayout(win)
    layout.addWidget(editor)

    qtbot.addWidget(win)
    with qtbot.waitActive(win, timeout=TestingFlags.WAIT_ACTIVE_TIMEOUT):
        pass
   
    qtbot.wait(TestingFlags.TEST_WAIT_LONG)
    editor.setSelection(a_out_2_index)
    qtbot.wait(TestingFlags.TEST_WAIT_LONG)
    editor.setSelection(a_out_1_index)
    
    MessageBox("Manual testing of the analog output editor window")
    qtbot.stopForInteraction()





