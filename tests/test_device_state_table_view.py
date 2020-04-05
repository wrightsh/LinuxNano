#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pytest
from PyQt5 import QtCore, QtWidgets, QtGui

from linuxnano.flags import TestingFlags
from linuxnano.views.widgets.device_state_table_view import DeviceStateTableView
from linuxnano.device_state_table_model import DeviceStateTableModel


#Sending a list ['one','two','etc'] so we don't use *enumerated
def enum(enumerated):
    enums = dict(zip(enumerated, range(len(enumerated))))
    enums["names"] = enumerated
    return type('enum', (), enums)


@pytest.fixture
def open_window(qtbot):
    def callback(window):
        widget = window()
        qtbot.addWidget(widget)
        widget.resize(1200,600)
        widget.show()
        qtbot.wait_for_window_shown(widget)
        qtbot.wait(TestingFlags.TEST_WAIT_LONG)
        return widget
    return callback


def test_getModel(qtbot):
    table_view  = DeviceStateTableView()
    table_model = DeviceStateTableModel()
    qtbot.addWidget(table_view)

    table_view.setModel(table_model)
    assert table_model == table_view.getModel()


def test_manualEditData(qtbot, open_window):
    if TestingFlags.ENABLE_MANUAL_TESTING is False: return

    table_model = DeviceStateTableModel()

    node_states = [ ('output', ['close', 'open']),
                    ('open_limit', ['is_not_open','is_open']) ]

    device_states = [ ['state', 'status', 'icon_layer', 'is_warning', 'warning_timeout', 'warning_message', 'is_alarm', 'alarm_timeout', 'alarm_message', 'triggers_action','action_timeout', 'action', 'log_entrance'],
                      [0, 'Closed' , 'layer_0', False, 0.0, '', False, 0.0, '', False, 0.0, None, True],
                      [1, 'Opening', 'layer_0', False, 0.0, '', False, 0.0, '', False, 0.0, None, True],
                      [2, 'Closing', 'layer_1', False, 0.0, '', False, 0.0, '', False, 0.0, None, True],
                      [3, 'High'   , 'layer_0', False, 0.0, '', False, 0.0, '', False, 0.0, None, False]]



    table_model.setNodeStates(node_states)
    table_model.setDeviceStates(device_states)

    table_view = open_window(DeviceStateTableView)
    table_view.setWindowTitle("Device State Table View")
    table_view.setModel(table_model)

    layer_list = ['layer_0','layer_1','layer_2','layer_3']
    table_view.setIconLayerList(enum(layer_list))



    message = QtWidgets.QMessageBox()
    message.setText("Manual testing of the device state table view\n -  Turning is_warning, is_alarm or triggers_action to False should make those non-editable")
    message.exec_()

    qtbot.stopForInteraction()
