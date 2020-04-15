#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pytest
from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtTest import QTest

from linuxnano.flags import TestingFlags
from linuxnano.message_box import MessageBox

from linuxnano.views.widgets.device_icon_widget import DeviceIconWidget


@pytest.fixture
def open_window(qtbot):
    def callback(window):
        widget = window()
        qtbot.addWidget(widget)
        widget.show()
        widget.setWindowTitle(widget.__class__.__name__)
        qtbot.wait_for_window_shown(widget)
        qtbot.wait(TestingFlags.TEST_WAIT_LONG)
        return widget
    return callback


def test_init(qtbot):
    svg = 'linuxnano/resources/icons/general/unknown.svg'
    wid = DeviceIconWidget(svg)
    assert isinstance(wid, DeviceIconWidget)


def test_setters(qtbot, open_window):
    called_function_on_click = False
    def my_fun(my_val):
        nonlocal called_function_on_click
        called_function_on_click = my_val

    svg = 'linuxnano/resources/icons/general/unknown.svg'

    wid = open_window(DeviceIconWidget)
    assert wid.isVisible()

    wid.setIcon(svg)
    wid.setCallback(my_fun)
    wid.setIndex(True) #Just seeing that True gets sent to the callback


    wid.layer = '1'
    qtbot.wait(TestingFlags.TEST_WAIT_LONG)
    wid.layer = '2'
    qtbot.wait(TestingFlags.TEST_WAIT_LONG)
    wid.layer = '1'
    qtbot.wait(TestingFlags.TEST_WAIT_LONG)

    wid.setSelected()
    qtbot.wait(TestingFlags.TEST_WAIT_LONG)
    wid.clearSelected()
    qtbot.wait(TestingFlags.TEST_WAIT_LONG)

    QTest.mouseClick(wid, QtCore.Qt.LeftButton)
    qtbot.wait(TestingFlags.TEST_WAIT_LONG)
    assert called_function_on_click == True
    wid.clearSelected()
    assert wid.isVisible()

    if TestingFlags.ENABLE_MANUAL_TESTING:
        MessageBox("Test that its outlined on hover and select")
        qtbot.stopForInteraction()


def test_bad_svg(qtbot, open_window):
    wid = open_window(DeviceIconWidget)
    assert wid.isVisible()

    with pytest.raises(ValueError):
        wid.setIcon('bad svg path')

    assert wid.isVisible()
