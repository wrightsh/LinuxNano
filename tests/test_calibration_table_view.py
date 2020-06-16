#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pytest
import sys, traceback

from linuxnano.message_box import MessageBox
from PyQt5 import QtCore, QtWidgets, QtGui

from linuxnano.flags import TestingFlags
from linuxnano.views.widgets.calibration_table_view import CalibrationTableView
from linuxnano.calibration_table_model import CalibrationTableModel


################# View Tests ####################

def excepthook(exc_type, exc_value, exc_tb):
    tb = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
    MessageBox(tb)

def test_setModel(qtbot):
    table_view  = CalibrationTableView()
    table_model = CalibrationTableModel()
    qtbot.addWidget(table_view)

    table_view.setModel(table_model)


def test_getModel(qtbot):
    table_view  = CalibrationTableView()
    table_model = CalibrationTableModel()
    qtbot.addWidget(table_view)

    table_view.setModel(table_model)
    assert table_model == table_view.getModel()



@pytest.fixture
def open_window(qtbot):
    def callback(window):
        widget = window()
        qtbot.addWidget(widget)
        widget.resize(400,400)
        widget.show()
        widget.setWindowTitle(widget.__class__.__name__)
        qtbot.wait_for_window_shown(widget)
        qtbot.wait(TestingFlags.TEST_WAIT_LONG)

        sys.excepthook = excepthook
        return widget
    return callback


def test_addRemoveRows(qtbot, open_window):
    table_model = CalibrationTableModel()
    table_view = open_window(CalibrationTableView)
    table_view.setModel(table_model)

    starting_count = table_model.rowCount()

    #Find a QRect of a row
    cell_rect = table_view.visualRect(table_model.index(1,1,QtCore.QModelIndex()))

    #Add One After
    table_view.setSelection(cell_rect, QtCore.QItemSelectionModel.Select)
    table_view.addRowAfterSelected()
    assert (starting_count+1) ==  table_model.rowCount()
    qtbot.wait(TestingFlags.TEST_WAIT_SHORT)

    #Remove One
    table_view.setSelection(cell_rect, QtCore.QItemSelectionModel.Select)
    table_view.removeSelectedRow()
    assert (starting_count) ==  table_model.rowCount()
    qtbot.wait(TestingFlags.TEST_WAIT_SHORT)

    #Add One Before
    table_view.setSelection(cell_rect, QtCore.QItemSelectionModel.Select)
    table_view.addRowBeforeSelected()
    assert (starting_count+1) ==  table_model.rowCount()
    qtbot.wait(TestingFlags.TEST_WAIT_SHORT)


def test_contextMenuEvent(qtbot, open_window):
    table_model = CalibrationTableModel()
    table_view = open_window(CalibrationTableView)
    table_view.setModel(table_model)

    if TestingFlags.ENABLE_MANUAL_TESTING:
        message = QtWidgets.QMessageBox()
        message.setText("Test the right click menu on the table.\nHal values must be increasing.\nGui values can be increasing or decreasing")
        message.exec_()
        qtbot.stopForInteraction()
