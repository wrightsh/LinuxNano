#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import pytest
from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtTest import QTest
from linuxnano.flags import TestingFlags

from linuxnano.views.widgets.device_manual_view import DeviceManualView, ManualBoolView, ManualBoolSet, ManualFloatView, ManualFloatSet

from linuxnano.tool_model import ToolModel
from linuxnano.strings import strings
from linuxnano.message_box import MessageBox
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


def test_init(qtbot):
    view = DeviceManualView()
    assert isinstance(view, DeviceManualView)

def test_setModel(qtbot, tool_model):
    view = DeviceManualView()
    view.setModel(tool_model)
    assert tool_model == view.model()


def test_deviceParams(qtbot, open_window, tool_model):
    wid = open_window(DeviceManualView)
    wid.setModel(tool_model)

    indexes = tool_model.indexesOfType(strings.DEVICE_NODE)
    dev = indexes[0]
    wid.setSelection(dev)

    #Name
    tool_model.setData(dev.siblingAtColumn(0), 'A_New_Name')
    assert wid.ui_name.text() == 'A_New_Name'

    #Description
    tool_model.setData(dev.siblingAtColumn(2), 'This is what the device is')
    assert wid.ui_description.text() == 'This is what the device is'

    #Status
    tool_model.setData(dev.siblingAtColumn(10), 'a status')
    assert wid.ui_status.text() == 'a status'


def test_twoOpen(qtbot, open_window, tool_model):
    wid1 = open_window(DeviceManualView)
    wid2 = open_window(DeviceManualView)

    wid1.setModel(tool_model)
    wid2.setModel(tool_model)

    indexes = tool_model.indexesOfType(strings.DEVICE_NODE)
    index = indexes[0]

    wid1.setSelection(index)
    wid2.setSelection(index)

    assert wid1.isVisible()
    assert wid2.isVisible()

    indexes = tool_model.indexesOfType(strings.D_IN_NODE)
    d_in = indexes[0]
    indexes = tool_model.indexesOfType(strings.A_IN_NODE)
    a_in = indexes[0]

    qtbot.wait(TestingFlags.TEST_WAIT_LONG)
    tool_model.setData(d_in.siblingAtColumn(20), True)
    tool_model.setData(a_in.siblingAtColumn(20), .11)
    qtbot.wait(TestingFlags.TEST_WAIT_LONG)
    tool_model.setData(d_in.siblingAtColumn(20), False)
    tool_model.setData(a_in.siblingAtColumn(20), .22)
    qtbot.wait(TestingFlags.TEST_WAIT_LONG)
    tool_model.setData(d_in.siblingAtColumn(20), True)
    tool_model.setData(a_in.siblingAtColumn(20), .33)

    if TestingFlags.ENABLE_MANUAL_TESTING is True:
        MessageBox("Test with two windows open")
        qtbot.stopForInteraction()


def test_ManualBoolView_init(qtbot, tool_model):
    for index in tool_model.indexesOfType(strings.D_IN_NODE):
        wid = ManualBoolView()
        wid.setModel(tool_model)
        wid.setRootIndex(index.parent())
        wid.setCurrentModelIndex(index)
        wid.show()
        qtbot.wait(TestingFlags.TEST_WAIT_SHORT)

        assert wid.isVisible()
        assert wid.ui_val.text() == index.internalPointer().displayValue()


def test_ManualFloatView_init(qtbot, tool_model):
    for index in tool_model.indexesOfType(strings.A_IN_NODE):
        wid = ManualFloatView()
        wid.setModel(tool_model)
        wid.setRootIndex(index.parent())
        wid.setCurrentModelIndex(index)
        wid.show()
        qtbot.wait(TestingFlags.TEST_WAIT_SHORT)

        assert wid.isVisible()
        assert wid.val == index.internalPointer().displayValue()
        tool_model.setData(index.siblingAtColumn(20), .22)
        assert wid.val == index.internalPointer().displayValue()








def itest_selectDevice(qtbot, wid, tool_model, device_indexes):
    wid.setSelection(device_indexes[0])
    with qtbot.waitExposed(wid, timeout=TestingFlags.WAIT_ACTIVE_TIMEOUT):pass
    assert wid.isVisible()

    for index in device_indexes:
        wid.setSelection(index)
        qtbot.wait(TestingFlags.TEST_WAIT_SHORT)

    wid.setSelection(device_indexes[0])
    if TestingFlags.ENABLE_MANUAL_TESTING is True:
        message = QtWidgets.QMessageBox()
        message.setText("Should have selected the devices.")
        message.exec_()

        qtbot.stopForInteraction()


def itest_selectDevice_object_count(qapp, qtbot, wid, tool_model, device_indexes):
    wid.setSelection(device_indexes[0])
    with qtbot.waitExposed(wid, timeout=TestingFlags.WAIT_ACTIVE_TIMEOUT):pass
    assert wid.isVisible()
    qtbot.wait(TestingFlags.TEST_WAIT_SHORT)

    starting_number = len(qapp.allWidgets())
    for i in range(50):
        for index in device_indexes:
            wid.setSelection(index)
    wid.setSelection(device_indexes[0])

    post_number = len(qapp.allWidgets())
    qtbot.wait(TestingFlags.TEST_WAIT_LONG)
    qtbot.wait(TestingFlags.TEST_WAIT_LONG)
    post_number_wait = len(qapp.allWidgets())

    #print('\n'.join(repr(w) for w in qapp.allWidgets()))
    assert starting_number == post_number_wait
