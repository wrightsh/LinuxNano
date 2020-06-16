#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pytest
from PyQt5 import QtCore, QtWidgets, QtGui
import xml.etree.ElementTree as ET

from linuxnano.tool_model import ToolModel
from linuxnano.tool_editor import ToolEditor, NodeEditor, SystemEditor, DeviceEditor, DeviceIconEditor, DigitalInputEditor, DigitalOutputEditor, AnalogInputEditor, AnalogOutputEditor
from linuxnano.tool_editor import BoolVarEditor, FloatVarEditor

from linuxnano.message_box import MessageBox
from linuxnano.flags import TestingFlags
from linuxnano.strings import strings

import json
from linuxnano.data import HalNode

@pytest.fixture
def open_window(qtbot):
    def callback(window):
        widget = window()
        widget.resize(400,400)
        qtbot.addWidget(widget)
        widget.setWindowTitle(widget.__class__.__name__)
        widget.show()
        qtbot.wait_for_window_shown(widget)
        qtbot.wait(TestingFlags.TEST_WAIT_LONG)
        return widget
        widget.show()
    return callback


@pytest.fixture()
def tool_model():
    model = ToolModel()

    HalNode.hal_pins.append(('d_in_1', 'bit', 'OUT'))
    HalNode.hal_pins.append(('d_in_2', 'bit', 'OUT'))
    HalNode.hal_pins.append(('d_in_3', 'bit', 'OUT'))

    HalNode.hal_pins.append(('d_out_1', 'bit', 'IN'))
    HalNode.hal_pins.append(('d_out_2', 'bit', 'IN'))
    HalNode.hal_pins.append(('d_out_3', 'bit', 'IN'))

    HalNode.hal_pins.append(('a_in_1', 'S32'  , 'OUT'))
    HalNode.hal_pins.append(('a_in_2', 'U32'  , 'OUT'))
    HalNode.hal_pins.append(('a_in_3', 'FLOAT', 'OUT'))

    HalNode.hal_pins.append(('a_out_1', 'S32'  , 'IN'))
    HalNode.hal_pins.append(('a_out_2', 'U32'  , 'IN'))
    HalNode.hal_pins.append(('a_out_3', 'FLOAT', 'IN'))

    file = 'tests/tools/basic_tool_1.json'
    with open(file) as f:
        json_data = json.load(f)

    model.loadJSON(json_data)


    return model




def itest_ToolEditor(qtbot, open_window, tool_model):
    editor = open_window(ToolEditor)
    editor.setWindowTitle("Tool Editor")
    editor.setModel(tool_model)

    if TestingFlags.ENABLE_MANUAL_TESTING:
        MessageBox("Tool Editor Testing")
        qtbot.stopForInteraction()


def test_NodeEditor(qtbot, open_window, tool_model):
    editor1 = open_window(NodeEditor)
    editor2 = open_window(NodeEditor)
    editor1.setModel(tool_model)
    editor2.setModel(tool_model)

    for index in tool_model.indexesOfType(strings.DEVICE_NODE):
        editor1.setSelection(index)
        editor2.setSelection(index)
        qtbot.mouseClick(editor1.ui_name, QtCore.Qt.LeftButton)
        qtbot.mouseClick(editor1.ui_description, QtCore.Qt.LeftButton)
        assert editor1.isVisible()
        assert editor2.isVisible()
        assert index.internalPointer().typeInfo() == editor1.ui_type.text()
        assert index.internalPointer().name == editor1.ui_name.text()
        assert index.internalPointer().description == editor1.ui_description.text()

    if TestingFlags.ENABLE_MANUAL_TESTING:
        MessageBox("Node Editor Manual Testing")
        qtbot.stopForInteraction()


def test_SystemEditor(qtbot, open_window, tool_model):
    editor1 = open_window(SystemEditor)
    editor2 = open_window(SystemEditor)
    editor1.setModel(tool_model)
    editor2.setModel(tool_model)

    for index in tool_model.indexesOfType(strings.SYSTEM_NODE):
        editor1.setSelection(index)
        editor2.setSelection(index)
        qtbot.mouseClick(editor1.ui_background_svg, QtCore.Qt.LeftButton)
        assert editor1.isVisible()
        assert editor2.isVisible()
        assert index.internalPointer().backgroundSVG == editor1.ui_background_svg.text()

    if TestingFlags.ENABLE_MANUAL_TESTING:
        MessageBox("System Editor Manual Testing")
        qtbot.stopForInteraction()


def test_DeviceEditor(qtbot, open_window, tool_model):
    editor1 = open_window(DeviceEditor)
    editor2 = open_window(DeviceEditor)
    editor1.setModel(tool_model)
    editor2.setModel(tool_model)

    for index in tool_model.indexesOfType(strings.DEVICE_NODE):
        editor1.setSelection(index)
        editor2.setSelection(index)
        assert editor1.isVisible()
        assert editor2.isVisible()

    if TestingFlags.ENABLE_MANUAL_TESTING:
        MessageBox("Device Editor Testing")
        qtbot.stopForInteraction()


def test_DeviceIconEditor(qtbot, open_window, tool_model):
    editor1 = open_window(DeviceIconEditor)
    editor2 = open_window(DeviceIconEditor)
    editor1.setModel(tool_model)
    editor2.setModel(tool_model)

    for index in tool_model.indexesOfType(strings.DEVICE_ICON_NODE):
        editor1.setSelection(index)
        editor2.setSelection(index)
        assert editor1.isVisible()
        assert editor2.isVisible()

        assert index.internalPointer().x == editor1.ui_x.value()
        assert index.internalPointer().y == editor1.ui_y.value()
        assert index.internalPointer().scale == editor1.ui_scale.value()
        assert index.internalPointer().rotation == editor1.ui_rotation.value()
        assert index.internalPointer().hasText == editor1.ui_has_text.isChecked()
        assert index.internalPointer().textX == editor1.ui_text_x.value()
        assert index.internalPointer().textY == editor1.ui_text_y.value()
        assert index.internalPointer().fontSize == editor1.ui_font_size.value()

    if TestingFlags.ENABLE_MANUAL_TESTING:
        MessageBox("Device Icon Editor Testing")
        qtbot.stopForInteraction()


def test_DigitalInputEditor(qtbot, open_window, tool_model):
    editor1 = open_window(DigitalInputEditor)
    editor2 = open_window(DigitalInputEditor)
    editor1.setModel(tool_model)
    editor2.setModel(tool_model)

    for index in tool_model.indexesOfType(strings.D_IN_NODE):
        editor1.setSelection(index)
        editor2.setSelection(index)
        assert editor1.isVisible()
        assert editor2.isVisible()
        assert index.internalPointer().halPin == editor1.ui_hal_pin.currentText()
        assert index.internalPointer().displayValueOff == editor1.ui_display_value_off.text()
        assert index.internalPointer().displayValueOn == editor1.ui_display_value_on.text()
        assert index.internalPointer().displayValue() == editor1.ui_display_value.text()
        tool_model.setData(index.siblingAtColumn(20), True)
        tool_model.setData(index.siblingAtColumn(21), True)
        assert index.internalPointer().displayValue() == editor1.ui_display_value.text()

    if TestingFlags.ENABLE_MANUAL_TESTING:
        MessageBox("Digital Input Editor Testing")
        qtbot.stopForInteraction()


def test_DigitalOutputEditor(qtbot, open_window, tool_model):
    editor1 = open_window(DigitalOutputEditor)
    editor2 = open_window(DigitalOutputEditor)
    editor1.setModel(tool_model)
    editor2.setModel(tool_model)

    for index in tool_model.indexesOfType(strings.D_OUT_NODE):
        editor1.setSelection(index)
        editor2.setSelection(index)
        assert editor1.isVisible()
        assert editor2.isVisible()
        assert index.internalPointer().halPin == editor1.ui_hal_pin.currentText()
        assert index.internalPointer().displayValueOff == editor1.ui_display_value_off.text()
        assert index.internalPointer().displayValueOn == editor1.ui_display_value_on.text()
        assert index.internalPointer().displayValue() == editor1.ui_display_value.text()
        tool_model.setData(index.siblingAtColumn(20), True)
        tool_model.setData(index.siblingAtColumn(21), True)
        assert index.internalPointer().displayValue() == editor1.ui_display_value.text()

    if TestingFlags.ENABLE_MANUAL_TESTING:
        MessageBox("Digital Output Editor Testing")
        qtbot.stopForInteraction()


def test_AnalogInputEditor(qtbot, open_window, tool_model):
    editor1 = open_window(AnalogInputEditor)
    editor2 = open_window(AnalogInputEditor)
    editor1.setModel(tool_model)
    editor2.setModel(tool_model)

    for index in tool_model.indexesOfType(strings.A_IN_NODE):
        editor1.setSelection(index)
        editor2.setSelection(index)
        assert editor1.isVisible()
        assert editor2.isVisible()
        assert index.internalPointer().halPin == editor1.ui_hal_pin.currentText()
        assert index.internalPointer().displayValue() == editor1.ui_display_value.value()
        assert index.internalPointer().units == editor1.ui_units.text()
        assert index.internalPointer().displayDigits == editor1.ui_display_digits.value()
        assert index.internalPointer().displayScientific == editor1.ui_display_scientific.isChecked()

    if TestingFlags.ENABLE_MANUAL_TESTING:
        MessageBox("Analog Input Editor Testing")
        qtbot.stopForInteraction()


def test_AnalogOutputEditor(qtbot, open_window, tool_model):
    editor1 = open_window(AnalogOutputEditor)
    editor2 = open_window(AnalogOutputEditor)
    editor1.setModel(tool_model)
    editor2.setModel(tool_model)

    for index in tool_model.indexesOfType(strings.A_OUT_NODE):
        editor1.setSelection(index)
        editor2.setSelection(index)
        assert editor1.isVisible()
        assert editor2.isVisible()
        assert index.internalPointer().halPin == editor1.ui_hal_pin.currentText()
        assert index.internalPointer().displayValue() == editor1.ui_display_value.value()
        assert index.internalPointer().units == editor1.ui_units.text()
        assert index.internalPointer().displayDigits == editor1.ui_display_digits.value()
        assert index.internalPointer().displayScientific == editor1.ui_display_scientific.isChecked()

    if TestingFlags.ENABLE_MANUAL_TESTING:
        MessageBox("Analog Output Editor Testing")
        qtbot.stopForInteraction()


def test_BoolVarEditor(qtbot, open_window, tool_model):
    editor1 = open_window(BoolVarEditor)
    editor2 = open_window(BoolVarEditor)
    editor1.setModel(tool_model)
    editor2.setModel(tool_model)

    for index in tool_model.indexesOfType(strings.BOOL_VAR_NODE):
        editor1.setSelection(index)
        editor2.setSelection(index)
        assert editor1.isVisible()
        assert editor2.isVisible()

        assert index.internalPointer().offName == editor1.ui_off_name.text()
        assert index.internalPointer().onName == editor1.ui_on_name.text()

    if TestingFlags.ENABLE_MANUAL_TESTING:
        MessageBox("Bool Var Editor Testing")
        qtbot.stopForInteraction()

def test_FloatVarEditor(qtbot, open_window, tool_model):
    editor1 = open_window(FloatVarEditor)
    editor2 = open_window(FloatVarEditor)
    editor1.setModel(tool_model)
    editor2.setModel(tool_model)

    for index in tool_model.indexesOfType(strings.FLOAT_VAR_NODE):
        editor1.setSelection(index)
        editor2.setSelection(index)
        assert editor1.isVisible()
        assert editor2.isVisible()

        assert index.internalPointer().min == editor1.ui_min.value()
        assert index.internalPointer().max == editor1.ui_max.value()

    if TestingFlags.ENABLE_MANUAL_TESTING:
        MessageBox("Float Var Editor Testing")
        qtbot.stopForInteraction()
