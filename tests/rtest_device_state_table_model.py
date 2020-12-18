#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pytest
import copy

from PyQt5 import QtCore, QtWidgets, QtGui

from linuxnano.flags import TestingFlags
from linuxnano.device_state_table_model import DeviceStateTableModel


def array_print(array):
    print('\n'.join(['\t'.join([str(cell) for cell in row]) for row in array]))

@pytest.fixture
def good_node_states():
    data_1 = [ ('output', ['off','on']) ]

    data_2 = [ ('output', ['off', 'low','med','high']) ]

    data_3 = [ ('output', ['close', 'open']),
               ('closed_limit', ['is_not_closed','is_closed']),
               ('open_limit', ['is_not_open','is_open']) ]

    data_4 = [ ('output', ['off', 'low', 'med', 'high']),
               ('open_limit', ['is_not_open', 'is_open']) ]

    return [data_1, data_2, data_3, data_4]


@pytest.fixture
def good_truth_tables():

    tbl_1 = [['off'],
             ['on']]

    tbl_2 = [['off'],
             ['low'],
             ['med'],
             ['high']]

    tbl_3 = [ ['is_not_open', 'is_not_closed', 'close'],
              ['is_not_open', 'is_not_closed', 'open' ],
              ['is_not_open', 'is_closed'    , 'close'],
              ['is_not_open', 'is_closed'    , 'open' ],
              ['is_open'    , 'is_not_closed', 'close'],
              ['is_open'    , 'is_not_closed', 'open' ],
              ['is_open'    , 'is_closed'    , 'close'],
              ['is_open'    , 'is_closed'    , 'open' ]]

    tbl_4 = [ ['is_not_open', 'off' ],
              ['is_not_open', 'low' ],
              ['is_not_open', 'med' ],
              ['is_not_open', 'high'],
              ['is_open'    , 'off' ],
              ['is_open'    , 'low' ],
              ['is_open'    , 'med' ],
              ['is_open'    , 'high']]

    return [tbl_1, tbl_2, tbl_3, tbl_4]

@pytest.fixture
def good_device_states():

    tbl_1 = [ ['state', 'status', 'icon_layer', 'is_warning', 'warning_timeout', 'warning_message', 'is_alarm', 'alarm_timeout', 'alarm_message', 'triggers_action', 'action_timeout', 'action', 'log_entrance'],
              [0, 'off', 'layer_0', False, 0.0, '', False, 0.0, '', False, 0.0, None, True],
              [1, 'on' , 'layer_1', False, 0.0, '', False, 0.0, '', False, 0.0, None, True]]

    tbl_2 = [ ['state', 'status', 'icon_layer', 'is_warning', 'warning_timeout', 'warning_message', 'is_alarm', 'alarm_timeout', 'alarm_message', 'triggers_action', 'action_timeout', 'action', 'log_entrance'],
              [0, 'off' , 'layer_0', False, 0.0,           '', False, 0.0,         '', False, 0.0, None, True],
              [1, 'low' , 'layer_0', False, 0.0,           '', False, 0.0,         '', False, 0.0, None, True],
              [2, 'med' , 'layer_0', False,  15, 'my_warning', False,  20, 'my alarm',  True,  20, None, True],
              [3, 'high', 'layer_1', False, 0.0,           '', False, 0.0,         '', False, 0.0, None, True]]

    tbl_3 = [ ['state', 'status', 'icon_layer', 'is_warning', 'warning_timeout', 'warning_message', 'is_alarm', 'alarm_timeout', 'alarm_message', 'triggers_action', 'action_timeout', 'action', 'log_entrance'],
              [0, 'closing', 'layer_0', False,  0.0,           '', False, 0.0,         '', False, 0.0, None,  True],
              [1, 'opening', 'layer_0', False,  0.0,           '', False, 0.0,         '', False, 0.0, None,  True],
              [2, 'closed' , 'layer_0', False,  0.0,           '', False, 0.0,         '', False, 0.0, None,  True],
              [3, 'opening', 'layer_0', False,  0.0,           '', False, 0.0,         '', False, 0.0, None,  True],
              [4, 'closing', 'layer_0', False,  0.0,           '', False, 0.0,         '', False, 0.0, None,  True],
              [5, 'open'   , 'layer_0', False,  0.0,           '', False, 0.0,         '', False, 0.0, None,  True],
              [6, 'fault'  , 'layer_0', False,  0.0,           '', False, 0.0,         '', False, 0.0, None,  True],
              [7, 'fault'  , 'layer_1', False,  0.0,           '', False, 0.0,         '', False, 0.0, None,  True]]

    tbl_4 = [ ['state', 'status', 'icon_layer', 'is_warning', 'warning_timeout', 'warning_message', 'is_alarm', 'alarm_timeout', 'alarm_message', 'triggers_action', 'action_timeout', 'action', 'log_entrance'],
              [0, 'not_open - off' , 'layer_0', False,  0.0, '', False, 0.0, '', False, 0.0, None,  True],
              [1, 'not_open - low' , 'layer_0', False,  0.0, '', False, 0.0, '', False, 0.0, None,  True],
              [2, 'not_open - med' , 'layer_0', False,  0.0, '', False, 0.0, '', False, 0.0, None,  True],
              [3, 'not_open - high', 'layer_0', False,  0.0, '', False, 0.0, '', False, 0.0, None,  True],
              [4, 'open - off'     , 'layer_0', False,  0.0, '', False, 0.0, '', False, 0.0, None,  True],
              [5, 'open - low'     , 'layer_0', False,  0.0, '', False, 0.0, '', False, 0.0, None,  True],
              [6, 'open - med'     , 'layer_0', False,  0.0, '', False, 0.0, '', False, 0.0, None,  True],
              [7, 'open - high'    , 'layer_1', False,  0.0, '', False, 0.0, '', False, 0.0, None,  True]]

    return [tbl_1, tbl_2, tbl_3, tbl_4]


def test_setNodeStates(good_node_states, good_truth_tables):
    table_model = DeviceStateTableModel()

    for i, good_states in enumerate(good_node_states):
        table_model.setNodeStates(good_states)
        assert good_truth_tables[i] == table_model.truthTable()

    with pytest.raises(TypeError):
        table_model.setNodeStates([ (1, ['off', True]) ])

    with pytest.raises(TypeError):
        table_model.setNodeStates([ ('output', ['off', True]) ])

    with pytest.raises(TypeError):
        table_model.setNodeStates([ ('output', 'off','on') ])


def test_setDeviceStates(good_node_states, good_device_states):
    table_model = DeviceStateTableModel()

    for i, good_states in enumerate(good_node_states):
        assert True == table_model.setNodeStates(good_states)
        assert True == table_model.setDeviceStates(good_device_states[i])
        assert good_device_states[i] == table_model.deviceStates()

    table_model.setNodeStates([ ('output', ['off','on']) ])

    with pytest.raises(TypeError):
        states = [ ['istate', 'status', 'icon_layer', 'is_warning', 'warning_timeout', 'warning_message', 'is_alarm', 'alarm_timeout', 'alarm_message', 'triggers_action', 'action_timeout', 'action', 'log_entrance'],
                   [0, 'Device Off', 'layer_0', False, 0.0, '', False, 0.0, '', False, 0.0, None, True],
                   [1, 'Device On' , 'layer_1', False, 0.0, '', False, 0.0, '', False, 0.0, None, True]]
        table_model.setDeviceStates(states)

    with pytest.raises(ValueError):
        states = [ ['state', 'status', 'icon_layer', 'is_warning', 'warning_timeout', 'warning_message', 'is_alarm', 'alarm_timeout', 'alarm_message', 'triggers_action', 'action_timeout', 'action', 'log_entrance'],
                   [1, 'Device Off', 'layer_0', False, 0.0, '', False, 0.0, '', False, 0.0, None, True],
                   [1, 'Device On' , 'layer_1', False, 0.0, '', False, 0.0, '', False, 0.0, None, True]]
        table_model.setDeviceStates(states)

    with pytest.raises(TypeError):
        states = [ ['state', 'status', 'icon_layer', 'is_warning', 'warning_timeout', 'warning_message', 'is_alarm', 'alarm_timeout', 'alarm_message', 'triggers_action', 'action_timeout', 'action', 'log_entrance'],
                   [0, 'Device Off', False, False, 0.0, '', False, 0.0, '', False, 0.0, None, True],
                   [1, 'Device On' , 'layer_1', False, 0.0, '', False, 0.0, '', False, 0.0, None, True]]
        table_model.setDeviceStates(states)


def test_rowCount(good_node_states, good_device_states):
    table_model = DeviceStateTableModel()

    for i, good_states in enumerate(good_node_states):
        table_model.setNodeStates(good_states)
        table_model.setDeviceStates(good_device_states[i])
        assert table_model.rowCount() == len(good_device_states[i]) - 1


def test_headerData(good_node_states, good_device_states):
    table_model = DeviceStateTableModel()

    for i, good_states in enumerate(good_node_states):
        table_model.setNodeStates(good_states)
        table_model.setDeviceStates(good_device_states[i])

        #check vertical header
        for row in range(table_model.rowCount()):
            assert str(row) == table_model.headerData(row, QtCore.Qt.Vertical, QtCore.Qt.DisplayRole)

        #Check horizontal headers
        headers = [row[0] for row in good_states]
        headers = headers[::-1]

        for i, val in enumerate(headers):
            assert val == table_model.headerData(i, QtCore.Qt.Horizontal, QtCore.Qt.DisplayRole)

        assert 'Status'                    == table_model.headerData(table_model.statusColumn()         , QtCore.Qt.Horizontal, QtCore.Qt.DisplayRole)
        assert 'Icon Layer\nName'          == table_model.headerData(table_model.iconLayerColumn()      , QtCore.Qt.Horizontal, QtCore.Qt.DisplayRole)
        assert 'Is Warning'                == table_model.headerData(table_model.isWarningColumn()      , QtCore.Qt.Horizontal, QtCore.Qt.DisplayRole)
        assert 'Warning\nTimeout (sec)'    == table_model.headerData(table_model.warningTimeoutColumn() , QtCore.Qt.Horizontal, QtCore.Qt.DisplayRole)
        assert 'Warning Message'           == table_model.headerData(table_model.warningMessageColumn() , QtCore.Qt.Horizontal, QtCore.Qt.DisplayRole)
        assert 'Is Alarm'                  == table_model.headerData(table_model.isAlarmColumn()        , QtCore.Qt.Horizontal, QtCore.Qt.DisplayRole)
        assert 'Alarm\nTimeout (sec)'      == table_model.headerData(table_model.alarmTimeoutColumn()   , QtCore.Qt.Horizontal, QtCore.Qt.DisplayRole)
        assert 'Alarm Message'             == table_model.headerData(table_model.alarmMessageColumn()   , QtCore.Qt.Horizontal, QtCore.Qt.DisplayRole)
        assert 'Triggers\nAction'          == table_model.headerData(table_model.triggersActionColumn() , QtCore.Qt.Horizontal, QtCore.Qt.DisplayRole)
        assert 'Action\nTimeout (sec)'     == table_model.headerData(table_model.actionTimeoutColumn()  , QtCore.Qt.Horizontal, QtCore.Qt.DisplayRole)
        assert 'Action'                    == table_model.headerData(table_model.actionColumn()         , QtCore.Qt.Horizontal, QtCore.Qt.DisplayRole)
        assert 'Log Entrance'              == table_model.headerData(table_model.logEntranceColumn()    , QtCore.Qt.Horizontal, QtCore.Qt.DisplayRole)


def test_flags(good_node_states, good_device_states, good_truth_tables):
    table_model = DeviceStateTableModel()

    for i, good_states in enumerate(good_node_states):
        table_model.setNodeStates(good_states)
        table_model.setDeviceStates(good_device_states[i])

        #No editing of the truth table section
        flags = (QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)
        for i, row in enumerate(good_truth_tables[i]):
            for j, val in enumerate(row):
                    assert table_model.flags(table_model.index(i, j, QtCore.QModelIndex())) == flags

        #Always allow editing of status, icon_layer, is_warning, is_alarm, triggers_action, log_entrance
        flags = (QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable)
        assert table_model.flags(table_model.index(0, table_model.statusColumn()         , QtCore.QModelIndex())) == flags
        assert table_model.flags(table_model.index(0, table_model.iconLayerColumn()      , QtCore.QModelIndex())) == flags
        assert table_model.flags(table_model.index(0, table_model.isWarningColumn()      , QtCore.QModelIndex())) == flags
        assert table_model.flags(table_model.index(0, table_model.isAlarmColumn()        , QtCore.QModelIndex())) == flags
        assert table_model.flags(table_model.index(0, table_model.triggersActionColumn() , QtCore.QModelIndex())) == flags
        assert table_model.flags(table_model.index(0, table_model.logEntranceColumn()    , QtCore.QModelIndex())) == flags

        #TODO add test to check for only allow editing of timeout and message if is_warning is true
