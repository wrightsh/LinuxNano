#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pytest
import json

from PyQt5 import QtCore, QtWidgets, QtGui

from linuxnano.views.widgets.system_manual_view import SystemManualView
import xml.etree.ElementTree as ET
from linuxnano.tool_model import ToolModel

from linuxnano.strings import typ, col
from linuxnano.flags import TestingFlags
from linuxnano.message_box import MessageBox

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

@pytest.fixture(params=['tests/tools/basic_tool_1.json'])
def tool_model(request):
    model = ToolModel()
    file = request.param
    with open(file) as f:
        json_data = json.load(f)

    model.loadJSON(json_data)
    return model


def test_init(qtbot):
    view = SystemManualView()
    assert isinstance(view, SystemManualView)

def test_setModel(qtbot, tool_model):
    view = SystemManualView()
    view.setModel(tool_model)
    assert tool_model == view.model()

def test_selectSystem(qtbot, open_window, tool_model):
    system_indexes = tool_model.indexesOfType(typ.SYSTEM_NODE)

    wid = open_window(SystemManualView)
    wid.setModel(tool_model)
    wid.setSelection(system_indexes[0])

    assert wid.isVisible()

    for index in system_indexes:
        wid.setSelection(index)
        assert wid.isVisible()
        qtbot.wait(TestingFlags.TEST_WAIT_LONG)


    if TestingFlags.ENABLE_MANUAL_TESTING:
        MessageBox("For each tool it should cycle through each system.")
        qtbot.stopForInteraction()


def test_selectDevice(qtbot, open_window, tool_model):
    device_indexes = tool_model.indexesOfType(typ.DEVICE_NODE)

    wid = open_window(SystemManualView)
    wid.setModel(tool_model)
    wid.setSelection(device_indexes[0])
    assert wid.isVisible()

    for index in device_indexes:
        wid.setSelection(index)
        qtbot.wait(TestingFlags.TEST_WAIT_LONG)

    if TestingFlags.ENABLE_MANUAL_TESTING:
        MessageBox("Should have selected the devices for this tool.")
        qtbot.stopForInteraction()

def test_fixMe(qtbot):
    assert False == 'We only have 1 tool thats being tested right now'

def test_setLayer(qtbot, open_window, tool_model):
    device_indexes = tool_model.indexesOfType(typ.DEVICE_NODE)
    icon_indexes = tool_model.indexesOfType(typ.DEVICE_ICON_NODE)

    wid = open_window(SystemManualView)
    wid.setModel(tool_model)
    assert wid.isVisible()

    for i, icon_index in enumerate(icon_indexes):
        node = icon_index.internalPointer()

        wid.setSelection(icon_index.parent())
        for layer in node.layers().names:
            tool_model.setData(icon_index.siblingAtColumn(col.LAYER), layer)
            assert tool_model.data(icon_index.siblingAtColumn(col.LAYER), QtCore.Qt.DisplayRole) == layer
            qtbot.wait(TestingFlags.TEST_WAIT_SHORT)

    if TestingFlags.ENABLE_MANUAL_TESTING:
        MessageBox("For each device it should have cycled through the icon layers.")
        qtbot.stopForInteraction()
