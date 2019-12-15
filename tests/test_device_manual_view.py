#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import pytest
from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtTest import QTest
from linuxnano.flags import TestingFlags
from linuxnano.views.widgets.device_manual_view import DeviceManualView, DigitalInputManualView, DigitalOutputManualView, AnalogInputManualView, AnalogOutputManualView
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
def d_in_indexes(tool_model, device_indexes):
    tool_index = tool_model.index(0, 0, QtCore.QModelIndex())
    d_in_indexes = []
    for device_index in device_indexes:
        for row in range(tool_model.rowCount(device_index)):
            if device_index.child(row,0).internalPointer().typeInfo() == strings.D_IN_NODE:
                d_in_indexes.append(device_index.child(row, 0)) #11 for icon_layer
    return d_in_indexes

@pytest.fixture()
def d_out_indexes(tool_model, device_indexes):
    tool_index = tool_model.index(0, 0, QtCore.QModelIndex())
    d_out_indexes = []
    for device_index in device_indexes:
        for row in range(tool_model.rowCount(device_index)):
            if device_index.child(row,0).internalPointer().typeInfo() == strings.D_OUT_NODE:
                d_out_indexes.append(device_index.child(row, 0)) #11 for icon_layer
    return d_out_indexes

@pytest.fixture()
def a_in_indexes(tool_model, device_indexes):
    tool_index = tool_model.index(0, 0, QtCore.QModelIndex())
    a_in_indexes = []
    for device_index in device_indexes:
        for row in range(tool_model.rowCount(device_index)):
            if device_index.child(row,0).internalPointer().typeInfo() == strings.A_IN_NODE:
                a_in_indexes.append(device_index.child(row, 0)) #11 for icon_layer
    return a_in_indexes

@pytest.fixture()
def a_out_indexes(tool_model, device_indexes):
    tool_index = tool_model.index(0, 0, QtCore.QModelIndex())
    a_out_indexes = []
    for device_index in device_indexes:
        for row in range(tool_model.rowCount(device_index)):
            if device_index.child(row,0).internalPointer().typeInfo() == strings.A_OUT_NODE:
                a_out_indexes.append(device_index.child(row, 0)) #11 for icon_layer
    return a_out_indexes

@pytest.fixture()
def wid(tool_model):
    view = DeviceManualView()
    view.setModel(tool_model)
    view.resize(400,400)
    view.setWindowTitle(str(type(view)))
    view.show()
    return view

@pytest.fixture()
def wid2(tool_model):
    view = DeviceManualView()
    view.setModel(tool_model)
    view.setGeometry(0,0,400,400)
    view.setWindowTitle(str(type(view)))
    view.show()
    return view




def test_DigitalInputManualView_init(qtbot, tool_model, d_in_indexes):
    for index in d_in_indexes:
        wid = DigitalInputManualView()
        wid.setModel(tool_model)
        wid.setRootIndex(index.parent())
        wid.setCurrentModelIndex(index)
        wid.show()
        qtbot.wait(TestingFlags.TEST_WAIT_SHORT)
        assert wid.isVisible()

def test_DigitalOutputManualView_init(qtbot, tool_model, d_out_indexes):
    for index in d_out_indexes:
        wid = DigitalOutputManualView(index.internalPointer().states())
        wid.setModel(tool_model)
        wid.setRootIndex(index.parent())
        wid.setCurrentModelIndex(index)
        wid.show()
        qtbot.wait(TestingFlags.TEST_WAIT_SHORT)
        assert wid.isVisible()


def test_AnalogInputManualView_init(qtbot, tool_model, a_in_indexes):
    for index in a_in_indexes:
        wid = AnalogInputManualView()
        wid.setModel(tool_model)
        wid.setRootIndex(index.parent())
        wid.setCurrentModelIndex(index)
        wid.show()
        qtbot.wait(TestingFlags.TEST_WAIT_SHORT)
        assert wid.isVisible()


def test_AnalogOutputManualView_init(qtbot, tool_model, a_out_indexes):
    for index in a_out_indexes:
        wid = AnalogOutputManualView()
        wid.setModel(tool_model)
        wid.setRootIndex(index.parent())
        wid.setCurrentModelIndex(index)
        wid.show()
        qtbot.wait(TestingFlags.TEST_WAIT_SHORT)
        assert wid.isVisible()

    qtbot.stopForInteraction()


def itest_init(qtbot):
    view = DeviceManualView()
    assert isinstance(view, DeviceManualView)

def itest_setModel(qtbot, tool_model):
    view = DeviceManualView()
    view.setModel(tool_model)
    assert tool_model == view.model()

def test_tmp(qtbot, wid,wid2, tool_model, device_indexes):
    wid.setSelection(device_indexes[0])
    wid2.setSelection(device_indexes[0])

    with qtbot.waitExposed(wid, timeout=TestingFlags.WAIT_ACTIVE_TIMEOUT):pass
    with qtbot.waitExposed(wid2, timeout=TestingFlags.WAIT_ACTIVE_TIMEOUT):pass
    assert wid.isVisible()
    assert wid2.isVisible()

    if TestingFlags.ENABLE_MANUAL_TESTING is True:
        message = QtWidgets.QMessageBox()
        message.setText("Test view with two open.")
        message.exec_()

        qtbot.stopForInteraction()


def test_selectDevice(qtbot, wid, tool_model, device_indexes):

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


def test_selectDevice_object_count(qapp, qtbot, wid, tool_model, device_indexes):
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
