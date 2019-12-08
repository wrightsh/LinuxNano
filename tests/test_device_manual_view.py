#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pytest
from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtTest import QTest
from linuxnano.flags import TestingFlags
from linuxnano.views.widgets.device_manual_view import DeviceManualView
import xml.etree.ElementTree as ET
from linuxnano.tool_model import ToolModel
from linuxnano.strings import strings


#@pytest.fixture(params=['tests/tools/tool_model_1.xml','tests/tools/tool_model_2.xml'])
@pytest.fixture(params=['tests/tools/tool_model_1.xml'])
def tool_model(request):
    tree = ET.parse(request.param)
    tool_model = ToolModel()
    tool_model.loadTool(tree)
    return tool_model

@pytest.fixture()
def system_indexes(tool_model):
    tool_index = tool_model.index(0, 0, QtCore.QModelIndex())
    system_indexes = []
    for row in range(tool_model.rowCount(tool_index)):
        system_indexes.append(tool_index.child(row, 0))
    return system_indexes

@pytest.fixture()
def device_indexes(tool_model, system_indexes):
    tool_index = tool_model.index(0, 0, QtCore.QModelIndex())
    device_indexes = []
    for sys_index in system_indexes:
        for row in range(tool_model.rowCount(sys_index)):
            device_indexes.append(sys_index.child(row, 0)) #11 for icon_layer
    return device_indexes

@pytest.fixture()
def wid(tool_model):
    view = DeviceManualView()
    view.setModel(tool_model)
    view.resize(400,400)
    view.setWindowTitle(str(type(view)))
    view.show()
    return view


def itest_init(qtbot):
    view = DeviceManualView()
    assert isinstance(view, DeviceManualView)

def itest_setModel(qtbot, tool_model):
    view = DeviceManualView()
    view.setModel(tool_model)
    assert tool_model == view.model()

def test_selectDevice(qtbot, wid, tool_model, device_indexes):
    wid.setSelection(device_indexes[0])
    with qtbot.waitExposed(wid, timeout=TestingFlags.WAIT_ACTIVE_TIMEOUT):pass
    assert wid.isVisible()

    qtbot.stopForInteraction()
    return

    for index in device_indexes:
        wid.setSelection(index)
        qtbot.wait(TestingFlags.TEST_WAIT_SHORT)

    if TestingFlags.ENABLE_MANUAL_TESTING is True:
        message = QtWidgets.QMessageBox()
        message.setText("Should have selected the devices.")
        message.exec_()
        qtbot.stopForInteraction()
