#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pytest

from PyQt5 import QtCore, QtWidgets, QtGui

from linuxnano.flags import TestingFlags
from linuxnano.views.widgets.state_table_views import DigitalStateTableView
from linuxnano.digital_state_table_model import DigitalStateTableModel
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

@pytest.fixture
def good_data():
    hal_pins = ['pin_a','pin_b']
    states = ['BTN 1', 'BTN 2', 'BTN 3', 'NA']
    is_used = [True, True, True, False]

    return [hal_pins, states, is_used]

def test_setModel(qtbot):
    table_view  = DigitalStateTableView()
    table_model = DigitalStateTableModel()
    qtbot.addWidget(table_view)

    table_view.setModel(table_model)

def test_getModel(qtbot):
    table_view  = DigitalStateTableView()
    table_model = DigitalStateTableModel()
    qtbot.addWidget(table_view)

    table_view.setModel(table_model)
    assert table_model == table_view.getModel()


def test_addRemoveBits(qtbot, open_window, good_data):
    table_model = DigitalStateTableModel(allow_is_used = True)
    table_model.setHalPins(good_data[0])
    table_model.setStates(good_data[1])
    table_model.setIsUsed(good_data[2])


    table_view = open_window(DigitalStateTableView)
    table_view.setWindowTitle("Digital State Table View")
    table_view.setModel(table_model)
    table_view.resize(table_view.sizeHint()*2)
    assert table_view.isVisible()

    starting_rows = table_model.rowCount()

    #Add One
    table_view.addBit()
    qtbot.wait(TestingFlags.TEST_WAIT_SHORT)
    assert starting_rows<<1 == table_model.rowCount()

    #Remove One
    table_view.removeBit()
    qtbot.wait(TestingFlags.TEST_WAIT_SHORT)
    assert starting_rows == table_model.rowCount()

    #Remove Another
    table_view.removeBit()
    qtbot.wait(TestingFlags.TEST_WAIT_SHORT)
    assert starting_rows>>1 == table_model.rowCount()

    #Remove One Too Many!
    with pytest.raises(ValueError):
        table_view.removeBit()
        qtbot.wait(TestingFlags.TEST_WAIT_SHORT)

    #Add One
    table_view.addBit()
    qtbot.wait(TestingFlags.TEST_WAIT_SHORT)
    assert starting_rows == table_model.rowCount()

    table_model.setAllowedHalPins(['None','pin_1', 'pin_2', 'pin_33', 'pin_4'])

    table_view.setHalPin(0,'pin_1')
    table_view.setHalPin(1,'pin_2')

    menu = table_view.generateContextMenu()
    assert isinstance(menu, QtWidgets.QMenu)

    if TestingFlags.ENABLE_MANUAL_TESTING:
        MessageBox("Digital State Table Manual Testing","Test that the GUI Name and is Used can be edited\n Row 0 is used must be True\n Right click add and remove bits")
        qtbot.stopForInteraction()


def test_noIsUsed(qtbot, open_window, good_data):
    table_model = DigitalStateTableModel(allow_is_used = False)
    table_model.setHalPins(good_data[0])
    table_model.setStates(good_data[1])

    table_model.setAllowedHalPins(['None','pin_1', 'pin_2', 'pin_33', 'pin_4'])

    table_view = open_window(DigitalStateTableView)
    table_view.setWindowTitle("Digital State Table View")
    table_view.setModel(table_model)
    table_view.resize(table_view.sizeHint()*2)
    assert table_view.isVisible()

    if TestingFlags.ENABLE_MANUAL_TESTING:
        MessageBox("Digital State Table Manual Testing","No is used column")
        qtbot.stopForInteraction()
