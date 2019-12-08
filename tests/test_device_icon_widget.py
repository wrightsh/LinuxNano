#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pytest
from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtTest import QTest

from linuxnano.flags import TestingFlags
from linuxnano.views.widgets.device_icon_widget import DeviceIconWidget

@pytest.fixture()
def win():
    win = QtWidgets.QWidget()
    win.resize(200,200)
    win.setWindowTitle("Device Icon Widget")
    win.show()
    yield win

def test_init(qtbot):
    svg = 'linuxnano/resources/icons/general/unknown.svg'
    wid = DeviceIconWidget(svg)
    assert isinstance(wid, DeviceIconWidget)


def test_property(qtbot, win):
    called_function_on_click = False
    def my_fun(my_val):
        nonlocal called_function_on_click
        called_function_on_click = my_val

    svg = 'linuxnano/resources/icons/general/unknown.svg'
    wid = DeviceIconWidget(svg, my_fun, True)

    layout = QtWidgets.QVBoxLayout(win)
    layout.addWidget(wid)

    qtbot.addWidget(win)
    with qtbot.waitActive(win, timeout=TestingFlags.WAIT_ACTIVE_TIMEOUT):
        pass

    wid.layer = '1'
    qtbot.wait(TestingFlags.TEST_WAIT_SHORT)
    wid.layer = '2'
    qtbot.wait(TestingFlags.TEST_WAIT_SHORT)
    wid.layer = '1'
    qtbot.wait(TestingFlags.TEST_WAIT_SHORT)
    wid.setSelected()
    qtbot.wait(TestingFlags.TEST_WAIT_SHORT)
    wid.clearSelected()
    qtbot.wait(TestingFlags.TEST_WAIT_SHORT)
    QTest.mouseClick(wid, QtCore.Qt.LeftButton)
    qtbot.wait(TestingFlags.TEST_WAIT_SHORT)
    assert called_function_on_click == True
    wid.clearSelected()

    if TestingFlags.ENABLE_MANUAL_TESTING is False: return

    message = QtWidgets.QMessageBox()
    message.setText("Test that its outlined on hover and select")
    message.exec_()

    qtbot.stopForInteraction()
