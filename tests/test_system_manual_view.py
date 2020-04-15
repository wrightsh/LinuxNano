#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pytest
from PyQt5 import QtCore, QtWidgets, QtGui

from linuxnano.views.widgets.system_manual_view import SystemManualView
import xml.etree.ElementTree as ET
from linuxnano.tool_model import ToolModel

from linuxnano.strings import strings
from linuxnano.flags import TestingFlags
from linuxnano.message_box import MessageBox


@pytest.fixture
def open_window(qtbot):
    def callback(window):
        widget = window()
        qtbot.addWidget(widget)
        widget.resize(700,700)
        widget.show()
        widget.setWindowTitle(widget.__class__.__name__)
        qtbot.wait_for_window_shown(widget)
        qtbot.wait(TestingFlags.TEST_WAIT_LONG)
        return widget
    return callback


@pytest.fixture(params=['tests/tools/tool_model_1.xml','tests/tools/tool_model_2.xml'])
def tool_model(request):
    tree = ET.parse(request.param)
    tool_model = ToolModel()
    tool_model.loadTool(tree)
    return tool_model


def itest_init(qtbot):
    view = SystemManualView()
    assert isinstance(view, SystemManualView)


def itest_setModel(qtbot, tool_model):
    view = SystemManualView()
    view.setModel(tool_model)
    assert tool_model == view.model()


def itest_selectSystem(qtbot, open_window, tool_model):
    system_indexes = tool_model.indexesOfType(strings.SYSTEM_NODE)

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


def itest_selectDevice(qtbot, open_window, tool_model):
    device_indexes = tool_model.indexesOfType(strings.DEVICE_NODE)

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


def test_setLayer(qtbot, open_window, tool_model):
    device_indexes = tool_model.indexesOfType(strings.DEVICE_NODE)

    wid = open_window(SystemManualView)
    wid.setModel(tool_model)
    wid.setSelection(device_indexes[0])
    assert wid.isVisible()

    for i, dev_index in enumerate(device_indexes):
        layers = dev_index.internalPointer().iconLayerList()

        for layer in layers.names:
            wid.setSelection(dev_index)

            tool_model.setData(dev_index.siblingAtColumn(11), layer)
            assert tool_model.data(dev_index.siblingAtColumn(11), QtCore.Qt.DisplayRole) == layer

            qtbot.wait(TestingFlags.TEST_WAIT_SHORT)


    if TestingFlags.ENABLE_MANUAL_TESTING:
        MessageBox("For each device it should have cycled through the icon layers.")
        qtbot.stopForInteraction()
