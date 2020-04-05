#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pytest
from PyQt5 import QtCore, QtWidgets, QtGui
import xml.etree.ElementTree as ET

from linuxnano.tool_model import ToolModel
from linuxnano.tool_editor import ToolEditor, NodeEditor, SystemEditor, DeviceEditor, DeviceIconEditor, DigitalInputEditor, DigitalOutputEditor, AnalogInputEditor, AnalogOutputEditor

from linuxnano.message_box import MessageBox
from linuxnano.flags import TestingFlags
from linuxnano.strings import strings


@pytest.fixture
def open_window(qtbot):
    def callback(window):
        widget = window()
        qtbot.addWidget(widget)
        widget.show()
        qtbot.wait_for_window_shown(widget)
        qtbot.wait(TestingFlags.TEST_WAIT_LONG)
        return widget

    return callback


@pytest.fixture()
def tool_model():
    tree = ET.parse('tests/tools/tool_model_1.xml')
    tool_model = ToolModel()
    tool_model.loadTool(tree)

    return tool_model


@pytest.fixture()
def indexes(tool_model):
    indexes = {strings.SYSTEM_NODE      : [],
               strings.DEVICE_NODE      : [],
               strings.DEVICE_ICON_NODE : [],
               strings.D_IN_NODE        : [],
               strings.A_IN_NODE        : [],
               strings.D_OUT_NODE       : [],
               strings.A_OUT_NODE       : []}


    tool_index = tool_model.index(0, 0, QtCore.QModelIndex())

    #Systems
    for row in range(tool_model.rowCount(tool_index)):
        indexes[strings.SYSTEM_NODE].append(tool_index.child(row, 0))

    #Devices
    for sys_index in indexes[strings.SYSTEM_NODE]:
        for row in range(tool_model.rowCount(sys_index)):
            indexes[strings.DEVICE_NODE].append(sys_index.child(row, 0))#This column matters!

    #children of a device
    for index in indexes[strings.DEVICE_NODE]:
        for row in range(tool_model.rowCount(index)):

            if index.child(row,0).internalPointer().typeInfo() == strings.D_IN_NODE:
                indexes[strings.D_IN_NODE].append(index.child(row, 0))

            if index.child(row,0).internalPointer().typeInfo() == strings.D_OUT_NODE:
                indexes[strings.D_OUT_NODE].append(index.child(row, 0))

            if index.child(row,0).internalPointer().typeInfo() == strings.A_IN_NODE:
                indexes[strings.A_IN_NODE].append(index.child(row, 0))

            if index.child(row,0).internalPointer().typeInfo() == strings.A_OUT_NODE:
                indexes[strings.A_OUT_NODE].append(index.child(row, 0))

    return indexes


def test_ToolEditor(qtbot, open_window, tool_model):
    editor = open_window(ToolEditor)
    editor.setWindowTitle("Tool Editor")
    editor.setModel(tool_model)

    if TestingFlags.ENABLE_MANUAL_TESTING:
        MessageBox("Tool Editor Testing")
        qtbot.stopForInteraction()


def test_NodeEditor(qtbot, open_window, tool_model, indexes):
    editor = open_window(NodeEditor)
    editor.setWindowTitle("Node Editor")
    editor.setModel(tool_model)

    for index in indexes[strings.DEVICE_NODE]:
        editor.setSelection(index)
        qtbot.wait(TestingFlags.TEST_WAIT_LONG)

        qtbot.mouseClick(editor.ui_name, QtCore.Qt.LeftButton)
        qtbot.mouseClick(editor.ui_description, QtCore.Qt.LeftButton)
        assert editor.isVisible()

    if TestingFlags.ENABLE_MANUAL_TESTING:
        MessageBox("Node Editor Manual Testing")
        qtbot.stopForInteraction()


def test_SystemEditor(qtbot, open_window, tool_model, indexes):
    editor = open_window(SystemEditor)
    editor.setWindowTitle("System Editor")
    editor.setModel(tool_model)

    for index in indexes[strings.SYSTEM_NODE]:
        editor.setSelection(index)
        qtbot.wait(TestingFlags.TEST_WAIT_LONG)

        qtbot.mouseClick(editor.ui_background_svg, QtCore.Qt.LeftButton)
        assert editor.isVisible()

    if TestingFlags.ENABLE_MANUAL_TESTING:
        MessageBox("System Editor Manual Testing")
        qtbot.stopForInteraction()


def test_DeviceEditor(qtbot, open_window, tool_model, indexes):
    editor = open_window(DeviceEditor)
    editor.setWindowTitle("Device Editor")
    editor.setModel(tool_model)

    for index in indexes[strings.DEVICE_NODE]:
        editor.setSelection(index)
        qtbot.wait(TestingFlags.TEST_WAIT_LONG)
        assert editor.isVisible()

    if TestingFlags.ENABLE_MANUAL_TESTING:
        MessageBox("Device Editor Testing")
        qtbot.stopForInteraction()


def test_DeviceIconEditor(qtbot, open_window, tool_model, indexes):
    editor = open_window(DeviceIconEditor)
    editor.setWindowTitle("Device Icon Editor")
    editor.setModel(tool_model)

                  #col, test_value
    data_cols = [[14, 100.1],
                 [15, 200.1],
                 [16, 1.1],
                 [17, 500.1],
                 [19, 200.1],
                 [20, 200.1],
                 [21, 14]]

    for index in indexes[strings.DEVICE_NODE]:

        for col in data_cols:
            icon_index = index.child(0, col[0])

            editor.setSelection(icon_index)
            qtbot.wait(TestingFlags.TEST_WAIT_SHORT)
            tool_model.setData(icon_index,col[1])
            assert col[1] == tool_model.data(icon_index, QtCore.Qt.DisplayRole)
            assert editor.isVisible()

    if TestingFlags.ENABLE_MANUAL_TESTING:
        MessageBox("Device Icon Editor Testing")
        qtbot.stopForInteraction()


def test_DigitalInputEditor(qtbot, open_window, tool_model, indexes):
    editor = open_window(DigitalInputEditor)
    editor.setWindowTitle("Digital Input Editor")
    editor.setModel(tool_model)

    for index in indexes[strings.D_IN_NODE]:
        editor.setSelection(index)
        qtbot.wait(TestingFlags.TEST_WAIT_LONG)
        assert editor.isVisible()

    if TestingFlags.ENABLE_MANUAL_TESTING:
        MessageBox("Digital Input Editor Testing")
        qtbot.stopForInteraction()


def test_DigitalOututEditor(qtbot, open_window, tool_model, indexes):
    editor = open_window(DigitalOutputEditor)
    editor.setWindowTitle("Digital Output Editor")
    editor.setModel(tool_model)

    for index in indexes[strings.D_OUT_NODE]:
        editor.setSelection(index)
        qtbot.wait(TestingFlags.TEST_WAIT_LONG)
        assert editor.isVisible()

    if TestingFlags.ENABLE_MANUAL_TESTING:
        MessageBox("Digital Output Editor Testing")
        qtbot.stopForInteraction()


def test_AnalogInputEditor(qtbot, open_window, tool_model, indexes):
    editor = open_window(AnalogInputEditor)
    editor.setWindowTitle("Analog Input Editor")
    editor.setModel(tool_model)

    for index in indexes[strings.A_IN_NODE]:
        editor.setSelection(index)
        qtbot.wait(TestingFlags.TEST_WAIT_LONG)
        assert editor.isVisible()

    if TestingFlags.ENABLE_MANUAL_TESTING:
        MessageBox("Analog Input Editor Testing")
        qtbot.stopForInteraction()


def test_AnalogOututEditor(qtbot, open_window, tool_model, indexes):
    editor = open_window(AnalogOutputEditor)
    editor.setWindowTitle("Analog Output Editor")
    editor.setModel(tool_model)

    for index in indexes[strings.A_OUT_NODE]:
        editor.setSelection(index)
        qtbot.wait(TestingFlags.TEST_WAIT_LONG)
        assert editor.isVisible()

    if TestingFlags.ENABLE_MANUAL_TESTING:
        MessageBox("Analog Output Editor Testing")
        qtbot.stopForInteraction()
