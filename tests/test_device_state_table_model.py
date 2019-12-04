#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pytest
import copy

from PyQt5 import QtCore, QtWidgets, QtGui

from linuxnano.flags import TestingFlags
from linuxnano.device_state_table_model import DeviceStateTableModel



def array_print(array):
    print('\n'.join(['\t'.join([str(cell) for cell in row]) for row in array]))


#First is the name of the node...
@pytest.fixture
def bad_node_states():

    tbl_1 = [['Output' ]]
    
    tbl_2 = [['Intensity', 'off',1]]
    
    tbl_3 = [['Power', 'off','low','med', 'high'],
             ['Intensity', 'open']]
    
    return [tbl_1, tbl_2, tbl_3]


@pytest.fixture
def good_node_states():

    tbl_1 = [['Power', 'off','on']]
    
    tbl_2 = [['Intensity', 'off','low','med', 'high']]
    
    tbl_3 = [['Output', 'off','on'],
             ['Limit Switch', 'closed', 'open']]
    
    tbl_4 = [['Intensity', 'off','low','med', 'high'],
             ['Limit Switch', 'closed', 'open']]
    
    tbl_5 = [['Intensity', 'off','low', 'high']]
    
    tbl_6 = [['Intensity', 'off','low','high'],
             ['Limit Switch', 'closed', 'open']]
    
    return [tbl_1,tbl_2, tbl_3, tbl_4, tbl_5, tbl_6]


@pytest.fixture
def good_truth_tables():
    
    tbl_1 = [['off'],
             ['on']]

    tbl_2 = [['off'],
             ['low'],
             ['med'],
             ['high']]

    tbl_3 = [['closed'      , 'off'],
             ['closed'      ,  'on'],
             [  'open'      , 'off'],
             [  'open'      ,  'on']]

    tbl_4 = [['closed',  'off'],
             ['closed',  'low'],
             ['closed',  'med'],
             ['closed', 'high'],
             [  'open',  'off'],
             [  'open',  'low'],
             [  'open',  'med'],
             [  'open', 'high']]

    tbl_5 = [['off'],
             ['low'],
             ['high']]

    tbl_6 = [['closed',  'off'],
             ['closed',  'low'],
             ['closed', 'high'],
             [  'open',  'off'],
             [  'open',  'low'],
             [  'open', 'high']]


    return [tbl_1, tbl_2, tbl_3, tbl_4, tbl_5, tbl_6]

@pytest.fixture
def good_data_arrays():

    tbl_1 = [ ['state', 'status', 'icon_layer', 'is_warning', 'warning_timeout', 'warning_message', 'is_alarm', 'alarm_timeout', 'alarm_message', 'triggers_action', 'action_timeout', 'action', 'log_entrance'],
              [   0   , 'Off'         , 'layer_0'   , False,  0.0,           '', False, 0.0,         '', False, 0.0, None,  True],
              [   1   , 'On'          , 'layer_1'   , False,  0.0,           '', False, 0.0,         '', False, 0.0, None,  True]]
                                                            
    tbl_2 = [ ['state', 'status', 'icon_layer', 'is_warning', 'warning_timeout', 'warning_message', 'is_alarm', 'alarm_timeout', 'alarm_message', 'triggers_action', 'action_timeout', 'action', 'log_entrance'],
              [   0   , 'Off'         , 'layer_0'   , False,  0.0,           '', False, 0.0,         '', False, 0.0, None,  True],
              [   1   , 'Low'         , 'layer_0'   , False,  0.0,           '', False, 0.0,         '', False, 0.0, None,  True],
              [   2   , 'Med'         , 'layer_0'   , False,   15, 'my warning', False,  20, 'my alarm',  True,  20, None,  True],
              [   3   , 'High'        , 'layer_1'   , False,  0.0,           '', False, 0.0,         '', False, 0.0, None,  True]]
                                                      
    tbl_3 = [ ['state', 'status', 'icon_layer', 'is_warning', 'warning_timeout', 'warning_message', 'is_alarm', 'alarm_timeout', 'alarm_message', 'triggers_action', 'action_timeout', 'action', 'log_entrance'],
              [   0   , 'Closed'      , 'layer_0'   , False,  0.0,           '', False, 0.0,         '', False, 0.0, None,  True],
              [   1   , 'Opening'     , 'layer_0'   , False,  0.0,           '', False, 0.0,         '', False, 0.0, None, False],
              [   2   , 'Closing'     , 'layer_0'   , False,  0.0,           '', False, 0.0,         '', False, 0.0, None,  True],
              [   3   , 'Open'        , 'layer_1'   , False,  0.0,           '', False, 0.0,         '', False, 0.0, None,  True]]
                                                            
    tbl_4 = [ ['state', 'status', 'icon_layer', 'is_warning', 'warning_timeout', 'warning_message', 'is_alarm', 'alarm_timeout', 'alarm_message', 'triggers_action', 'action_timeout', 'action', 'log_entrance'],
              [   0   , 'Closed'      , 'layer_0'   , False,  0.0,           '', False, 0.0,         '', False, 0.0, None,  True],
              [   1   , 'Opening'     , 'layer_0'   , False,  0.0,           '', False, 0.0,         '', False, 0.0, None,  True],
              [   2   , 'Closing'     , 'layer_0'   , False,  0.0,           '', False, 0.0,         '', False, 0.0, None,  True],
              [   3   , 'Closing'     , 'layer_0'   , False,  0.0,           '', False, 0.0,         '', False, 0.0, None,  True],
              [   4   , 'Closing'     , 'layer_0'   , False,  0.0,           '', False, 0.0,         '', False, 0.0, None,  True],
              [   5   , 'Closing'     , 'layer_0'   , False,  0.0,           '', False, 0.0,         '', False, 0.0, None,  True],
              [   6   , 'Closing'     , 'layer_0'   , False,  0.0,           '', False, 0.0,         '', False, 0.0, None,  True],
              [   7   , 'Open'        , 'layer_1'   , False,  0.0,           '', False, 0.0,         '', False, 0.0, None,  True]]
                                                            
    tbl_5 = [ ['state', 'status', 'icon_layer', 'is_warning', 'warning_timeout', 'warning_message', 'is_alarm', 'alarm_timeout', 'alarm_message', 'triggers_action', 'action_timeout', 'action', 'log_entrance'],
              [   0   , 'Off'         , 'layer_0'   , False,  0.0,           '', False, 0.0,         '', False, 0.0, None,  True],
              [   1   , 'Low'         , 'layer_0'   , False,  0.0,           '', False, 0.0,         '', False, 0.0, None,  True],
              [   2   , 'High'        , 'layer_1'   , False,  0.0,           '', False, 0.0,         '', False, 0.0, None,  True]]
                                                            
    tbl_6 = [ ['state', 'status', 'icon_layer', 'is_warning', 'warning_timeout', 'warning_message', 'is_alarm', 'alarm_timeout', 'alarm_message', 'triggers_action', 'action_timeout', 'action', 'log_entrance'],
              [   0   , 'Closed'      , 'layer_0'   , False,  0.0,           '', False, 0.0,         '', False, 0.0, None,  True],
              [   1   , 'Opening'     , 'layer_0'   , False,  0.0,           '', False, 0.0,         '', False, 0.0, None,  True],
              [   2   , 'Closing'     , 'layer_0'   , False,  0.0,           '', False, 0.0,         '', False, 0.0, None,  True],
              [   3   , 'Closing'     , 'layer_0'   , False,  0.0,           '', False, 0.0,         '', False, 0.0, None,  True],
              [   4   , 'Closing'     , 'layer_0'   , False,  0.0,           '', False, 0.0,         '', False, 0.0, None,  True],
              [   5   , 'Open'        , 'layer_1'   , False,  0.0,           '', False, 0.0,         '', False, 0.0, None,  True]]


    return [tbl_1, tbl_2, tbl_3, tbl_4, tbl_5, tbl_6]


@pytest.fixture
def bad_data_arrays():

    #state mispelled 
    tbl_1 = [ ['stiate', 'status', 'icon_layer', 'is_warning', 'warning_timeout', 'warning_message', 'is_alarm', 'alarm_timeout', 'alarm_message', 'triggers_action', 'action_timeout', 'action', 'log_entrance'],
              
            
            
              [   0   , 'Off'         , 'layer_0'   , False,  0.0,           '', False, 0.0,         '', False, 0.0, None,  True],
              [   1   , 'On'          , 'layer_1'   , False,  0.0,           '', False, 0.0,         '', False, 0.0, None,  True]]
            
            
    #Warning timeout contains string
    tbl_2 = [ ['state', 'status', 'icon_layer', 'is_warning', 'warning_timeout', 'warning_message', 'is_alarm', 'alarm_timeout', 'alarm_message', 'triggers_action', 'action_timeout', 'action', 'log_entrance'],
              [   0   , 'Off'         , 'layer_0'   , False,  'ham',           '', False, 0.0,         '', False, 0.0, None,  True],
              [   1   , 'Low'         , 'layer_0'   , False,  0.0,           '', False, 0.0,         '', False, 0.0, None,  True],
              [   2   , 'Med'         , 'layer_0'   , False,   15, 'my warning', False,  20, 'my alarm',  True,  20, None,  True],
              [   3   , 'High'        , 'layer_1'   , False,  0.0,           '', False, 0.0,         '', False, 0.0, None,  True]]
                                                      
    #state order wrong
    tbl_3 = [ ['state', 'status', 'icon_layer', 'is_warning', 'warning_timeout', 'warning_message', 'is_alarm', 'alarm_timeout', 'alarm_message', 'triggers_action', 'action_timeout', 'action', 'log_entrance'],
              [   3   , 'Closed'      , 'layer_0'   , False,  0.0,           '', False, 0.0,         '', False, 0.0, None,  True],
              [   2   , 'Opening'     , 'layer_0'   , False,  0.0,           '', False, 0.0,         '', False, 0.0, None, False],
              [   1   , 'Closing'     , 'layer_0'   , False,  0.0,           '', False, 0.0,         '', False, 0.0, None,  True],
              [   0   , 'Open'        , 'layer_1'   , False,  0.0,           '', False, 0.0,         '', False, 0.0, None,  True]]
                                                            
    #state contains ham
    tbl_4 = [ ['state', 'status', 'icon_layer', 'is_warning', 'warning_timeout', 'warning_message', 'is_alarm', 'alarm_timeout', 'alarm_message', 'triggers_action', 'action_timeout', 'action', 'log_entrance'],
              [   0   , 'Closed'      , 'layer_0'   , False,  0.0,           '', False, 0.0,         '', False, 0.0, None,  True],
              [   1   , 'Opening'     , 'layer_0'   , False,  0.0,           '', False, 0.0,         '', False, 0.0, None,  True],
              [   'ham'   , 'Closing'     , 'layer_0'   , False,  0.0,           '', False, 0.0,         '', False, 0.0, None,  True],
              [   3   , 'Closing'     , 'layer_0'   , False,  0.0,           '', False, 0.0,         '', False, 0.0, None,  True],
              [   4   , 'Closing'     , 'layer_0'   , False,  0.0,           '', False, 0.0,         '', False, 0.0, None,  True],
              [   5   , 'Closing'     , 'layer_0'   , False,  0.0,           '', False, 0.0,         '', False, 0.0, None,  True],
              [   6   , 'Closing'     , 'layer_0'   , False,  0.0,           '', False, 0.0,         '', False, 0.0, None,  True],
              [   7   , 'Open'        , 'layer_1'   , False,  0.0,           '', False, 0.0,         '', False, 0.0, None,  True]]
                                                            
    #missing a row
    tbl_5 = [ ['state', 'status', 'icon_layer', 'is_warning', 'warning_timeout', 'warning_message', 'is_alarm', 'alarm_timeout', 'alarm_message', 'triggers_action', 'action_timeout', 'action', 'log_entrance'],
              [   0   , 'Off'         , 'layer_0'   , False,  0.0,           '', False, 0.0,         '', False, 0.0, None,  True],
              [   2   , 'High'        , 'layer_1'   , False,  0.0,           '', False, 0.0,         '', False, 0.0, None,  True]]
                                                            
    #warning message is number not string
    tbl_6 = [ ['state', 'status', 'icon_layer', 'is_warning', 'warning_timeout', 'warning_message', 'is_alarm', 'alarm_timeout', 'alarm_message', 'triggers_action', 'action_timeout', 'action', 'log_entrance'],
              [   0   , 'Closed'      , 'layer_0'   , False,  0.0,           '', False, 0.0,         '', False, 0.0, None,  True],
              [   1   , 'Opening'     , 'layer_0'   , False,  0.0,           '', False, 0.0,         '', False, 0.0, None,  True],
              [   2   , 'Closing'     , 'layer_0'   , False,  0.0,           '', False, 0.0,         '', False, 0.0, None,  True],
              [   3   , 'Closing'     , 'layer_0'   , False,  0.0,           '', False, 0.0,         '', False, 0.0, None,  True],
              [   4   , 'Closing'     , 'layer_0'   , False,  0.0,           8.9, False, 0.0,         '', False, 0.0, None,  True],
              [   5   , 'Open'        , 'layer_1'   , False,  0.0,           '', False, 0.0,         '', False, 0.0, None,  True]]
            


    return [tbl_1, tbl_2, tbl_3, tbl_4, tbl_5, tbl_6]




def test_setNodeStates(good_node_states, good_truth_tables, bad_node_states):

    table_model = DeviceStateTableModel()
    for i, good_states in enumerate(good_node_states):
        table_model.setNodeStates(good_states)
        assert good_truth_tables[i] == table_model.truthTable()

    last_good_tbl = table_model.truthTable()

    for bad_states in bad_node_states:
        table_model.setNodeStates(bad_states)
        assert last_good_tbl == table_model.truthTable()
 
def test_setDataArray(good_node_states, good_data_arrays, bad_data_arrays):

    table_model = DeviceStateTableModel()
    
    for i, good_states in enumerate(good_node_states):

        assert True == table_model.setNodeStates(good_states)
        assert True == table_model.setDataArray(good_data_arrays[i])
        assert good_data_arrays[i] == table_model.dataArray()

    for i, good_states in enumerate(good_node_states):
        assert True == table_model.setNodeStates(good_states)
        array = table_model.dataArray()
        
        
        table_model.setDataArray(bad_data_arrays[i])
        assert array == table_model.dataArray()




def test_dataArray(good_node_states, good_data_arrays):
    #Make sure we are getting a copy of the data, and can't directly edit it

    table_model = DeviceStateTableModel()
    
    for i, good_states in enumerate(good_node_states):
        table_model.setNodeStates(good_states)
        table_model.setDataArray(good_data_arrays[i])

        returned_array = table_model.dataArray()
        returned_array_copy = copy.deepcopy(returned_array)
        
        for i, row in enumerate(returned_array):
            for j, val in enumerate(row):
                returned_array[i][j] = None

        assert returned_array_copy == table_model.dataArray()

def test_rowCount(good_node_states, good_data_arrays):

    table_model = DeviceStateTableModel()
    for i, good_states in enumerate(good_node_states):
        table_model.setNodeStates(good_states)
        table_model.setDataArray(good_data_arrays[i])

        assert table_model.rowCount() == len(good_data_arrays[i]) - 1
        
def test_columnCount(good_node_states, good_truth_tables, good_data_arrays):

    table_model = DeviceStateTableModel()
    for i, good_states in enumerate(good_node_states):
        table_model.setNodeStates(good_states)
        
        array     = good_data_arrays[i]
        truth_tbl = good_truth_tables[i]
        
        table_model.setDataArray(array)

        assert table_model.columnCount() == len(array[0])-1 + len(truth_tbl[0]) #-1 from dropping the 'state' col in exchange for the truth table
        
def test_headerData(good_node_states, good_truth_tables, good_data_arrays):
    
    table_model = DeviceStateTableModel()
    for i, good_states in enumerate(good_node_states):
        table_model.setNodeStates(good_states)
        table_model.setDataArray(good_data_arrays[i])
    
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
    
#TODO maybe improve this testing...
def test_addRemoveStateAfterLoad():

    table_model = DeviceStateTableModel()
       
    states = [['Output', 'off','on']]
    
    new_states = [['Output', 'off','on'],
                  ['Limit Switch', 'closed', 'open']]

    data = [ ['state', 'status', 'icon_layer', 'is_warning', 'warning_timeout', 'warning_message', 'is_alarm', 'alarm_timeout', 'alarm_message', 
                                                                                            'triggers_action', 'action_timeout', 'action', 'log_entrance'],
             [   0   , 'Off'         , 'layer_0'   , False,  0.0,           '', False, 0.0,         '', False, 0.0, None,  True],
             [   1   , 'On'          , 'layer_1'   , False,  0.0,           '', False, 0.0,         '', False, 0.0, None,  True]]
                                                            
   

    table_model.setNodeStates(states)
    table_model.setDataArray(data)
    
    table_model.setNodeStates(new_states)
    
    table_model.setNodeStates(states)
    table_model.setDataArray(data)

def test_flags(good_node_states, good_truth_tables, good_data_arrays):
    
    table_model = DeviceStateTableModel()
    for i, good_states in enumerate(good_node_states):
        table_model.setNodeStates(good_states)
        table_model.setDataArray(good_data_arrays[i])


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
    

#TODO Add more testing here.... 
def test_setData(good_node_states, good_truth_tables, good_data_arrays):
    
    table_model = DeviceStateTableModel()
    for i, good_states in enumerate(good_node_states):
        table_model.setNodeStates(good_states)
        table_model.setDataArray(good_data_arrays[i])


        index = table_model.index(0, table_model.statusColumn(), QtCore.QModelIndex())
        table_model.setData(index, "A test status", QtCore.Qt.EditRole)
        assert "A test status" == table_model.data(index,  QtCore.Qt.DisplayRole)


        index = table_model.index(1, table_model.statusColumn(), QtCore.QModelIndex())
        table_model.setData(index, "A second test status", QtCore.Qt.EditRole)
        assert "A second test status" == table_model.data(index,  QtCore.Qt.DisplayRole)


        index = table_model.index(0, 0, QtCore.QModelIndex())
        prev_val = table_model.data(index,  QtCore.Qt.DisplayRole)
        table_model.setData(index, "We cant edit this", QtCore.Qt.EditRole)
        assert prev_val == table_model.data(index,  QtCore.Qt.DisplayRole)



        #Test set icon layer
        index = table_model.index(0, table_model.iconLayerColumn(), QtCore.QModelIndex())
        table_model.setData(index, 'layer_2', QtCore.Qt.EditRole)
        assert 'layer_2' == table_model.data(index,  QtCore.Qt.DisplayRole)


        #Test warning timeout
        index = table_model.index(1, table_model.warningTimeoutColumn(), QtCore.QModelIndex())
        
        table_model.setData(index, 95, QtCore.Qt.EditRole)
        assert 95 == table_model.data(index,  QtCore.Qt.DisplayRole)
        
        table_model.setData(index, None, QtCore.Qt.EditRole)
        assert None == table_model.data(index,  QtCore.Qt.DisplayRole)
       

        #Test alarm timeout
        index = table_model.index(1, table_model.alarmTimeoutColumn(), QtCore.QModelIndex())
        
        table_model.setData(index, 95, QtCore.Qt.EditRole)
        assert 95 == table_model.data(index,  QtCore.Qt.DisplayRole)
        
        table_model.setData(index, None, QtCore.Qt.EditRole)
        assert None == table_model.data(index,  QtCore.Qt.DisplayRole)


        #Test action timeout
        index = table_model.index(1, table_model.actionTimeoutColumn(), QtCore.QModelIndex())
        
        table_model.setData(index, 95, QtCore.Qt.EditRole)
        assert 95 == table_model.data(index,  QtCore.Qt.DisplayRole)
        
        table_model.setData(index, None, QtCore.Qt.EditRole)
        assert None == table_model.data(index,  QtCore.Qt.DisplayRole)
       

        #Test warning message
        index = table_model.index(1, table_model.warningMessageColumn(), QtCore.QModelIndex())
        
        table_model.setData(index, 'some text here', QtCore.Qt.EditRole)
        assert 'some text here' == table_model.data(index,  QtCore.Qt.DisplayRole)
        
        table_model.setData(index, '', QtCore.Qt.EditRole)
        assert '' == table_model.data(index,  QtCore.Qt.DisplayRole)
       
        #Test alarm message
        index = table_model.index(1, table_model.alarmMessageColumn(), QtCore.QModelIndex())
        
        table_model.setData(index, 'some alarm text here', QtCore.Qt.EditRole)
        assert 'some alarm text here' == table_model.data(index,  QtCore.Qt.DisplayRole)
        
        table_model.setData(index, '', QtCore.Qt.EditRole)
        assert '' == table_model.data(index,  QtCore.Qt.DisplayRole)
       
       

        #TODO figure out the action
        
        
        #Test set log entrance
        index = table_model.index(1, table_model.logEntranceColumn(), QtCore.QModelIndex())
        
        table_model.setData(index, False, QtCore.Qt.EditRole)
        assert False == table_model.data(index,  QtCore.Qt.DisplayRole)
        
        table_model.setData(index, True, QtCore.Qt.EditRole)
        assert True == table_model.data(index,  QtCore.Qt.DisplayRole)
        
       

        

#TODO test truthTable 
