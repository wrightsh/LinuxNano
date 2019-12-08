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
def tool_model_1():
    tree = ET.parse('tests/tool_model.xml')
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
    device_icon_index_xval = device_index.child(0, 14)

    editor = DeviceIconEditor()
    editor.setModel(tool_model_1)

    editor.setSelection(device_icon_index_1)

    layout = QtWidgets.QVBoxLayout(win)
    layout.addWidget(editor)

    qtbot.addWidget(win)
    with qtbot.waitActive(win, timeout=TestingFlags.WAIT_ACTIVE_TIMEOUT):
        pass

    #print(tool_model_1.data(device_icon_index_xval,QtCore.Qt.DisplayRole))
    assert 11.11 == tool_model_1.setData(device_icon_index_xval,11.11)

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
