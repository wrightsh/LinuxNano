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
from linuxnano.message_box import MessageBox


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


@pytest.fixture(params=['tests/tools/tool_model_1.xml'])
def tool_model(request):
    tree = ET.parse(request.param)
    tool_model = ToolModel()
    tool_model.loadTool(tree)
    return tool_model


#11 for icon layer?
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

            if index.child(row, 0).internalPointer().typeInfo() == strings.D_OUT_NODE:
                indexes[strings.D_OUT_NODE].append(index.child(row, 20))

            if index.child(row,0).internalPointer().typeInfo() == strings.A_IN_NODE:
                indexes[strings.A_IN_NODE].append(index.child(row, 0))

            if index.child(row,0).internalPointer().typeInfo() == strings.A_OUT_NODE:
                indexes[strings.A_OUT_NODE].append(index.child(row, 0))

    return indexes




def itest_DigitalInputManualView_init(qtbot, tool_model, indexes):
    for index in indexes[strings.D_IN_NODE]:
        wid = DigitalInputManualView()
        wid.setModel(tool_model)
        wid.setRootIndex(index.parent())
        wid.setCurrentModelIndex(index)
        wid.show()
        qtbot.wait(TestingFlags.TEST_WAIT_SHORT)
        assert wid.isVisible()

    if TestingFlags.ENABLE_MANUAL_TESTING:
        MessageBox("Digital Input Manual View")
        qtbot.stopForInteraction()


def test_DigitalOutputManualView_init(qtbot, tool_model, indexes):
    for index in indexes[strings.D_OUT_NODE]:
        wid = DigitalOutputManualView(index.internalPointer().halPins, index.internalPointer().states, index.internalPointer().isUsed)
        wid.setModel(tool_model)
        wid.setRootIndex(index.parent())
        wid.setCurrentModelIndex(index)
        wid.show()
        qtbot.wait(TestingFlags.TEST_WAIT_SHORT)
        assert wid.isVisible()

    if TestingFlags.ENABLE_MANUAL_TESTING:
        MessageBox("Digital Output Manual View")
        qtbot.stopForInteraction()


def itest_AnalogInputManualView_init(qtbot, tool_model, a_in_indexes):
    for index in a_in_indexes:
        wid = AnalogInputManualView()
        wid.setModel(tool_model)
        wid.setRootIndex(index.parent())
        wid.setCurrentModelIndex(index)
        wid.show()
        qtbot.wait(TestingFlags.TEST_WAIT_SHORT)
        assert wid.isVisible()


def itest_AnalogOutputManualView_init(qtbot, tool_model, a_out_indexes):
    for index in a_out_indexes:
        wid = AnalogOutputManualView()
        wid.setModel(tool_model)
        wid.setRootIndex(index.parent())
        wid.setCurrentModelIndex(index)
        wid.show()
        qtbot.wait(TestingFlags.TEST_WAIT_SHORT)
        assert wid.isVisible()

    qtbot.stopForInteraction()


def test_init(qtbot):
    view = DeviceManualView()
    assert isinstance(view, DeviceManualView)

def test_setModel(qtbot, tool_model):
    view = DeviceManualView()
    view.setModel(tool_model)
    assert tool_model == view.model()

def test_twoOpen(qtbot, open_window, tool_model, indexes):
    wid1 = open_window(DeviceManualView)
    wid2 = open_window(DeviceManualView)

    wid1.setModel(tool_model)
    wid2.setModel(tool_model)

    index = indexes[strings.DEVICE_NODE][0]

    wid1.setSelection(index)
    wid2.setSelection(index)

    assert wid1.isVisible()
    assert wid2.isVisible()

    if TestingFlags.ENABLE_MANUAL_TESTING is True:
        message = QtWidgets.QMessageBox()
        message.setText("Test view with two open.")
        message.exec_()


        d_out = indexes[strings.D_OUT_NODE][0]

        qtbot.wait(TestingFlags.TEST_WAIT_LONG)
        tool_model.setData(d_out, 0)
        print("grr")
        qtbot.wait(TestingFlags.TEST_WAIT_LONG)
        tool_model.setData(d_out, 1)
        print("grr")
        qtbot.wait(TestingFlags.TEST_WAIT_LONG)
        tool_model.setData(d_out, 0)
        print("grr")
        qtbot.wait(TestingFlags.TEST_WAIT_LONG)
        tool_model.setData(d_out, 1)
        print("grr")
        #qtbot.wait(TestingFlags.TEST_WAIT_LONG)
        #tool_model.setData(d_out, 3)
        #qtbot.wait(TestingFlags.TEST_WAIT_LONG)
        #tool_model.setData(d_out, 4)
        #qtbot.wait(TestingFlags.TEST_WAIT_LONG)
        #tool_model.setData(d_out, 5)
        #qtbot.wait(TestingFlags.TEST_WAIT_LONG)
        #tool_model.setData(d_out, 6)
        #qtbot.wait(TestingFlags.TEST_WAIT_LONG)
        #tool_model.setData(d_out, 63)
        #qtbot.wait(TestingFlags.TEST_WAIT_LONG)
        #tool_model.setData(d_out, 64)
        #qtbot.wait(TestingFlags.TEST_WAIT_LONG)
        #tool_model.setData(d_out, 255)

        qtbot.stopForInteraction()


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
