#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pytest

from PyQt5 import QtCore, QtWidgets, QtGui

from linuxnano.flags import TestingFlags
from linuxnano.views.widgets.state_table_views import AnalogStateTableView
from linuxnano.analog_state_table_model import AnalogStateTableModel
from linuxnano.views.widgets.scientific_spin import ScientificDoubleSpinBox


def test_setModel(qtbot):
    table_view  = AnalogStateTableView()
    table_model = AnalogStateTableModel()
    qtbot.addWidget(table_view)
    
    table_view.setModel(table_model)


def test_getModel(qtbot):
    table_view  = AnalogStateTableView()
    table_model = AnalogStateTableModel()
    qtbot.addWidget(table_view)
    
    table_view.setModel(table_model)
    assert table_model == table_view.getModel()


@pytest.fixture()
def win():
    win = QtWidgets.QWidget()
    win.resize(600,600)
    win.setWindowTitle("Analog State Table View")
    win.show()

    yield win


def test_ScientificSDoubleSpinBox(qtbot):
    wid = ScientificDoubleSpinBox()
  
    wid.setValue(1.01e-6)
    assert 1.01e-6 == wid.value()
    
    wid.setValue(1.01e6)
    assert 1.01e6 == wid.value()

    wid.setValue(1.01e2)
    assert 101 == wid.value()
    
    wid.setValue(-9001.1)
    assert -9001.1 == wid.value()



def test_addRemoveStates(qtbot, win):
   
    good_data = [['state','greater_than', 'gui_name'],
                 [      0,          None,  "State 1"],
                 [      1,          4.00,  "State 2"]]
       

    table_model = AnalogStateTableModel()
    table_model.setDataArray(good_data)

    table_view = AnalogStateTableView()
    table_view.setModel(table_model)

    layout = QtWidgets.QVBoxLayout(win)
    layout.addWidget(table_view)
    
    qtbot.addWidget(win)
    with qtbot.waitActive(win, timeout=TestingFlags.WAIT_ACTIVE_TIMEOUT):
        pass

    starting_rows = table_model.rowCount()

    #Add One
    table_view.addState()
    qtbot.wait(TestingFlags.TEST_WAIT_SHORT)
    assert starting_rows+1 == table_model.rowCount()
    
    #Remove One
    table_view.removeState()
    qtbot.wait(TestingFlags.TEST_WAIT_SHORT)
    assert starting_rows == table_model.rowCount()
   
    #Remove Another
    table_view.removeState()
    qtbot.wait(TestingFlags.TEST_WAIT_SHORT)
    assert starting_rows-1 == table_model.rowCount()
    
    #Remove One Too Many!
    qtbot.wait(TestingFlags.TEST_WAIT_SHORT)
    assert starting_rows-1 == table_model.rowCount()
    
    #Add One
    table_view.addState()
    qtbot.wait(TestingFlags.TEST_WAIT_SHORT)
    assert starting_rows == table_model.rowCount()


def test_manualEditData(qtbot, win):
    if TestingFlags.ENABLE_MANUAL_TESTING is False: return
    
    good_data = [['state','greater_than', 'gui_name'],
                 [      0,          None,  "State 1"],
                 [      1,          2.00,  "State 2"],
                 [      2,          3.00,  "State 3"],
                 [      3,          4.00,  "State 4"]]
       
 
    table_model = AnalogStateTableModel()
    table_model.setDataArray(good_data)


    table_view = AnalogStateTableView()
    table_view.setModel(table_model)

    layout = QtWidgets.QVBoxLayout(win)
    layout.addWidget(table_view)

    qtbot.addWidget(win)
    with qtbot.waitActive(win, timeout=TestingFlags.WAIT_ACTIVE_TIMEOUT):
        pass

    message = QtWidgets.QMessageBox()
    message.setText("State 0 greater than should be None, others must be sequential.\n All gui names should be editable\n Right click add and remove states")
    message.exec_()
    
    qtbot.stopForInteraction()


