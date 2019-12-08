#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pytest
from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtTest import QTest

from linuxnano.flags import TestingFlags
from linuxnano.tool_manual_view import ToolManualView
import xml.etree.ElementTree as ET
from linuxnano.tool_model import ToolModel


#@pytest.fixture(params=['tests/tools/tool_model_1.xml','tests/tools/tool_model_2.xml'])
@pytest.fixture(params=['tests/tools/tool_model_1.xml'])
def tool_model(request):
    tree = ET.parse(request.param)
    tool_model = ToolModel()
    tool_model.loadTool(tree)
    return tool_model

@pytest.fixture()
def wid(tool_model):
    view = ToolManualView(tool_model)
    view.resize(800,600)
    view.setWindowTitle(str(type(view)))
    view.show()
    return view


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
            device_indexes.append(sys_index.child(row, 0))#This column matters!
    return device_indexes



def test_init(qtbot, tool_model):
    view = ToolManualView(tool_model)
    assert isinstance(view, ToolManualView)

def test_tmp(qtbot, wid, tool_model):
    view = ToolManualView(tool_model)
    qtbot.addWidget(wid)
    with qtbot.waitExposed(wid, timeout=TestingFlags.WAIT_ACTIVE_TIMEOUT):pass
    qtbot.stopForInteraction()


def test_setTreeSelection_system(qtbot, wid, tool_model, system_indexes):
    qtbot.addWidget(wid)
    wid.setTreeSelection(system_indexes[0])
    with qtbot.waitExposed(wid, timeout=TestingFlags.WAIT_ACTIVE_TIMEOUT):pass
    assert wid.isVisible()
    qtbot.wait(TestingFlags.TEST_WAIT_LONG)

    for index in system_indexes:
        wid.setTreeSelection(index)
        qtbot.wait(TestingFlags.TEST_WAIT_SHORT)

    if TestingFlags.ENABLE_MANUAL_TESTING is True:
        message = QtWidgets.QMessageBox()
        message.setText("Should have selected each system from the tree.")
        message.exec_()
        qtbot.stopForInteraction()


def test_setGraphicSelection_system(qtbot, wid, tool_model, system_indexes):
    qtbot.addWidget(wid)
    wid.setGraphicSelection(system_indexes[0])
    with qtbot.waitExposed(wid, timeout=TestingFlags.WAIT_ACTIVE_TIMEOUT):pass
    assert wid.isVisible()
    qtbot.wait(TestingFlags.TEST_WAIT_SHORT)

    for index in system_indexes:
        wid.setGraphicSelection(index)
        qtbot.wait(TestingFlags.TEST_WAIT_SHORT)

    if TestingFlags.ENABLE_MANUAL_TESTING is True:
        message = QtWidgets.QMessageBox()
        message.setText("Should have selected each system from the graphic.")
        message.exec_()
        qtbot.stopForInteraction()


def test_setTreeSelection_device(qtbot, wid, tool_model, device_indexes):
    qtbot.addWidget(wid)
    wid.setTreeSelection(device_indexes[0])
    with qtbot.waitExposed(wid, timeout=TestingFlags.WAIT_ACTIVE_TIMEOUT):pass
    assert wid.isVisible()
    qtbot.wait(TestingFlags.TEST_WAIT_LONG)

    for index in device_indexes:
        qtbot.wait(TestingFlags.TEST_WAIT_SHORT)
        wid.setTreeSelection(index)

    if TestingFlags.ENABLE_MANUAL_TESTING is True:
        message = QtWidgets.QMessageBox()
        message.setText("Should have selected each device from the tree.")
        message.exec_()
        qtbot.stopForInteraction()


def test_setGraphicSelection_device(qtbot, wid, tool_model, device_indexes):
    qtbot.addWidget(wid)
    wid.setGraphicSelection(device_indexes[0])
    with qtbot.waitExposed(wid, timeout=TestingFlags.WAIT_ACTIVE_TIMEOUT):pass
    assert wid.isVisible()
    qtbot.wait(TestingFlags.TEST_WAIT_LONG)

    for index in device_indexes:
        qtbot.wait(TestingFlags.TEST_WAIT_SHORT)
        wid.setGraphicSelection(index)

    if TestingFlags.ENABLE_MANUAL_TESTING is True:
        message = QtWidgets.QMessageBox()
        message.setText("Should have selected each device from the graphic.")
        message.exec_()
        qtbot.stopForInteraction()
