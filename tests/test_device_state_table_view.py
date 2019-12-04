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


def test_setModel(qtbot):
    table_view  = DeviceStateTableView()
    table_model = DeviceStateTableModel()
    qtbot.addWidget(table_view)
    
    table_view.setModel(table_model)


def test_getModel(qtbot):
    table_view  = DeviceStateTableView()
    table_model = DeviceStateTableModel()
    qtbot.addWidget(table_view)
    
    table_view.setModel(table_model)
    assert table_model == table_view.getModel()


@pytest.fixture()
def win():
    win = QtWidgets.QWidget()
    win.resize(1200,600)
    win.setWindowTitle("Device State Table View")
    win.show()

    yield win




def test_manualEditData(qtbot, win):
    if TestingFlags.ENABLE_MANUAL_TESTING is False: return

    table_model = DeviceStateTableModel()
   
    node_states = [['Intensity', 'off','low','high'],
                   ['Limit Switch', 'closed', 'open']]

    data_array = [ ['state', 'status', 'icon_layer', 'is_warning', 'warning_timeout', 'warning_message', 'is_alarm', 'alarm_timeout', 'alarm_message', 
                                                                                                                        'triggers_action','action_timeout', 'action', 'log_entrance'],
                   [   0   , 'Closed'   , 'layer_0'   , False, 0.0, '', False, 0.0, '', False, 0.0, None, True],
                   
                   [   1   , 'Opening' , 'layer_0', False, 0.0,             '', False, 0.0,          '', False, 0.0, None, True],
                   [   2   , 'Closing' , 'layer_1', False, 0.0,             '', False, 0.0,          '', False, 0.0, None, True],
                   [   3   , 'Closed'  , 'layer_0', False, 0.0,             '', False, 0.0,          '', False, 0.0, None, True],
                   [   4   , 'Med'     , 'layer_2',  True, 8.0, 'Some message',  True, 9.0, 'alarm msg',  True, 9.0, None, True],
                   [   5   , 'High'    , 'layer_0', False, 0.0,             '', False, 0.0,          '', False, 0.0, None, False]]
                   


    table_model.setNodeStates(node_states)
    table_model.setDataArray(data_array)

    table_view = DeviceStateTableView()
    layer_list = ['layer_0','layer_1','layer_2','layer_3']
    table_view.setModel(table_model)
    table_view.setIconLayerList(enum(layer_list))


    layout = QtWidgets.QVBoxLayout(win)
    layout.addWidget(table_view)

    qtbot.addWidget(win)
    with qtbot.waitActive(win, timeout=TestingFlags.WAIT_ACTIVE_TIMEOUT):
        pass

    message = QtWidgets.QMessageBox()
    message.setText("Manual testing of the device state table view\n -  Turning is_warning, is_alarm or triggers_action to False should make those non-editable")
    message.exec_()
    
    qtbot.stopForInteraction()




