#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pytest
from PyQt5 import QtSvg, QtCore
from linuxnano.flags import TestingFlags
from linuxnano.message_box import MessageBox
from linuxnano.views.widgets.device_icon_widget import DeviceIconWidget

def test_init(qtbot):
    svg = 'linuxnano/resources/icons/general/unknown.svg'
    renderer = QtSvg.QSvgRenderer()
    renderer.load(svg)

    wid = DeviceIconWidget(renderer)
    assert isinstance(wid, DeviceIconWidget)


def test_setCallback(qtbot):
    called_function_on_click = False
    def my_fun(my_val):
        nonlocal called_function_on_click
        called_function_on_click = my_val

    wid = DeviceIconWidget()
    wid.setCallback(my_fun)

def test_setPosCallback(qtbot):
    called_function_on_click = False
    def my_fun(my_val):
        nonlocal called_function_on_click
        called_function_on_click = my_val

    wid = DeviceIconWidget()
    wid.setPosCallback(my_fun)

def test_setIndex(qtbot):
    wid = DeviceIconWidget()
    wid.setIndex(QtCore.QModelIndex())

def test_setMovable(qtbot):
    wid = DeviceIconWidget()
    wid.setMovable(True)
    wid.setMovable(False)
