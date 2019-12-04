#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pytest

from PyQt5 import QtCore, QtWidgets, QtGui

from linuxnano.flags import TestingFlags
from linuxnano.views.widgets.state_table_views import DigitalStateTableView 
from linuxnano.digital_state_table_model import DigitalStateTableModel


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


@pytest.fixture()
def win():
    win = QtWidgets.QWidget()
    win.resize(600,600)
    win.setWindowTitle("Digital State Table View")
    win.show()

    yield win


def test_addRemoveBits(qtbot, win):
    
    good_data = [ ['state','gui_name','is_used'],
                  [0, "BTN 1", True],
                  [1, "BTN 2", True],
                  [2, "BTN 3", True],
                  [3, "BTN 4", True]]
    
    table_model = DigitalStateTableModel(allow_is_used = True)
    table_model.setDataArray(good_data)

    table_view = DigitalStateTableView()
    table_view.setModel(table_model)

    layout = QtWidgets.QVBoxLayout(win)
    layout.addWidget(table_view)
    
    qtbot.addWidget(win)
    with qtbot.waitActive(win, timeout=TestingFlags.WAIT_ACTIVE_TIMEOUT):
        pass

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
    qtbot.wait(TestingFlags.TEST_WAIT_SHORT)
    assert starting_rows>>1 == table_model.rowCount()


def test_manualEditData(qtbot, win):
    if TestingFlags.ENABLE_MANUAL_TESTING is False: return

    good_data = [ ['state','gui_name','is_used'],
                  [0, "BTN 1", True],
                  [1, "BTN 2", True],
                  [2, "BTN 3", True],
                  [3, "BTN 4", True]]

 
    table_model = DigitalStateTableModel(allow_is_used = True)
    table_model.setDataArray(good_data)


    table_view = DigitalStateTableView()
    table_view.setModel(table_model)

    layout = QtWidgets.QVBoxLayout(win)
    layout.addWidget(table_view)

    qtbot.addWidget(win)
    with qtbot.waitActive(win, timeout=TestingFlags.WAIT_ACTIVE_TIMEOUT):
        pass

    message = QtWidgets.QMessageBox()
    message.setText("Test that the GUI Name and is Used can be edited\n Row 0 is used must be True\n Right click add and remove bits")
    message.exec_()
    
    qtbot.stopForInteraction()


