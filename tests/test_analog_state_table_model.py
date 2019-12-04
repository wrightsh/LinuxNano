#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pytest
import copy

from PyQt5 import QtCore, QtWidgets, QtGui

from linuxnano.flags import TestingFlags
from linuxnano.analog_state_table_model import AnalogStateTableModel



def array_print(array):
    print('\n'.join(['\t'.join([str(cell) for cell in row]) for row in array]))


@pytest.fixture
def good_dataArray_data():

    good_data_1 = [['state','greater_than', 'gui_name']]
    good_data_2 = [['state','greater_than', 'gui_name']]
    good_data_3 = [['state','greater_than', 'gui_name']]
    good_data_4 = [['state','greater_than', 'gui_name']]
    
    
    good_data_1 += [[0, None,  "Normal"]]

    good_data_2 += [[0, None, "State 1"],
                    [1, 2.00, "State 2"]]

    good_data_3 += [[0, None, "State 1"],
                    [1, 2.00, "State 2"],
                    [2, 3.00, "State 3"]]

    good_data_4 += [[0, None, "State 1"],
                    [1, 2.00, "State 2"],
                    [2, 3.00, "State 3"],
                    [3, 4.00, "State 4"]]

    return [good_data_1, good_data_2, good_data_3, good_data_4]


@pytest.fixture
def bad_dataArray_data():

    bad_data_1 = [['state','greater_than', 'gui_name', 'is_used']]
    bad_data_2 = [['greater_than','state','gui_name']]
    bad_data_3 = [['state','greater_than', 'gui_name']]
    bad_data_4 = [['state','greater_than', 'gui_name']]
    bad_data_5 = [['state','greater_than', 'gui_name']]
    bad_data_6 = [['state','greater_than', 'gui_name']]
    
   
    #No is_used column
    bad_data_1 += [[0, None,  "Low", True],
                   [1, 1.23, "High", True]]
    
    #Flipped state / greater_than column
    bad_data_2 += [[None, 0,  "Low", True],
                   [1.23, 1,"High", True]]


    #missed a comma
    bad_data_3 += [[0,  None,  "Low"],
                   [1, "High"]]


    #First greater_than must be None
    bad_data_4 += [[0,  3.33,  "Low", True],
                    [1, 1.23, "High", True]]
       

    #col 1 must be 0,1,2,3 ect. 
    bad_data_5 += [[0, None, "State 1"],
                   [2, 2.00, "State 2"],
                   [3, 4.00, "State 4"]]
    
    #Must be increasing greater than col. 
    bad_data_6 += [[0, None, "State 1"],
                   [1, 2.00, "State 2"],
                   [2, 3.01, "State 2"],
                   [3, -4.1, "State 4"]]


    return [bad_data_1, bad_data_2, bad_data_3, bad_data_4, bad_data_5, bad_data_6]




def test_rowCount(good_dataArray_data):
    
    for good_data in good_dataArray_data:
        table_model = AnalogStateTableModel()
        table_model.setDataArray(good_data)
        assert table_model.rowCount() == len(good_data)-1
        
def test_columnCount(good_dataArray_data):
    for good_data in good_dataArray_data:
        table_model = AnalogStateTableModel()
        table_model.setDataArray(good_data)
        
        assert table_model.columnCount() == 3
 

def test_headerData(good_dataArray_data):
    for good_data in good_dataArray_data:
        table_model = AnalogStateTableModel()
        table_model.setDataArray(good_data)

        num_cols = len(good_data[0]) 
        num_rows = len(good_data) - 1

        #check horizontal header header
        assert 'State'        == table_model.headerData(0, QtCore.Qt.Horizontal, QtCore.Qt.DisplayRole)
        assert 'Greater Than' == table_model.headerData(1, QtCore.Qt.Horizontal, QtCore.Qt.DisplayRole)
        assert 'GUI Name'     == table_model.headerData(2, QtCore.Qt.Horizontal, QtCore.Qt.DisplayRole)



def test_setDataArray(good_dataArray_data, bad_dataArray_data):

    for good_data in good_dataArray_data:
        table_model = AnalogStateTableModel()
        table_model.setDataArray(good_data)
        assert good_data == table_model.dataArray()
   
    for bad_data in bad_dataArray_data:
        table_model = AnalogStateTableModel()
        table_model.setDataArray(bad_data)
        assert bad_data != table_model.dataArray()

def test_dataArray(good_dataArray_data):
    #Check if we get the array back and start editing it that we're editing a copy and not the classes actual _data
    
    for good_data in good_dataArray_data:
        table_model = AnalogStateTableModel()
        table_model.setDataArray(good_data)
        
        returned_array = table_model.dataArray()
        returned_array_copy = copy.deepcopy(returned_array)
        
        for i, row in enumerate(returned_array):
            for j, val in enumerate(row):
                returned_array[i][j] = None
        
        assert returned_array_copy == table_model.dataArray()

   
def test_data(good_dataArray_data):
    for good_data in good_dataArray_data:
        table_model = AnalogStateTableModel()
        table_model.setDataArray(good_data)

        good_data_main = good_data[1:]
        for i, row in enumerate(good_data_main):
            assert good_data_main[i][1] == table_model.data(table_model.index(i,table_model.greaterThanColumn(),QtCore.QModelIndex()), QtCore.Qt.DisplayRole)
            assert good_data_main[i][2] == table_model.data(table_model.index(i,table_model.nameColumn(),QtCore.QModelIndex()), QtCore.Qt.DisplayRole)

def test_setData(good_dataArray_data):
    for good_data in good_dataArray_data:
        table_model = AnalogStateTableModel()
        table_model.setDataArray(good_data)



        greater_than_col = table_model.greaterThanColumn()
        name_col         = table_model.nameColumn()

        num_cols = len(good_data[0])
        num_rows = len(good_data)-1 #not including the header row


        #Try setting some of the greaterThan column
        if num_rows > 1:
            table_model.setData(table_model.index(1, greater_than_col, QtCore.QModelIndex()), 0.876, QtCore.Qt.EditRole)
            val = table_model.data(table_model.index(1, greater_than_col, QtCore.QModelIndex()),  QtCore.Qt.DisplayRole)
            assert val == 0.876

            tmp_val = table_model.data(table_model.index(num_rows-1, greater_than_col, QtCore.QModelIndex()),  QtCore.Qt.DisplayRole)
            tmp_val = tmp_val + 1
            table_model.setData(table_model.index(num_rows-1, greater_than_col, QtCore.QModelIndex()), tmp_val, QtCore.Qt.EditRole)
            val = table_model.data(table_model.index(num_rows-1, greater_than_col, QtCore.QModelIndex()),  QtCore.Qt.DisplayRole)
            assert val == tmp_val


        #Try setting some of the name column
        table_model.setData(table_model.index(0, name_col, QtCore.QModelIndex()), "Fast Off", QtCore.Qt.EditRole)
        val = table_model.data(table_model.index(0, name_col, QtCore.QModelIndex()),  QtCore.Qt.DisplayRole)
        assert val == "Fast Off"

        table_model.setData(table_model.index(num_rows-1, name_col, QtCore.QModelIndex()), "Start", QtCore.Qt.EditRole)
        val = table_model.data(table_model.index(num_rows-1, name_col, QtCore.QModelIndex()),  QtCore.Qt.DisplayRole)
        assert val == "Start"

def test_setNumberOfStates():
    table_model = AnalogStateTableModel()
    good_data_1 = [ ['state','greater_than', 'gui_name'],
                    [      0,          None,      'Low'],
                    [      1,          1.0,     'High']]


    table_model.setDataArray(good_data_1)
    table_model.setNumberOfStates(2)

    assert good_data_1 == table_model.dataArray()
    #set it to different number of states
    for i in [1,2,3,4,1]:
        table_model.setNumberOfStates(i)
        arr = table_model.dataArray()
        assert len(arr)-1 == i
        assert arr[1][2] == 'Low'
        
        if   i == 3:
            assert arr[3][1] > arr[2][1]
        elif i == 4:
            assert arr[3][1] > arr[2][1]
            assert arr[4][1] > arr[3][1]

    
    last_good_arr = table_model.dataArray()

    #Set to some not allowed numbers
    for i in [0,-1,5,10]:
        assert False == table_model.setNumberOfStates(i)
        assert last_good_arr == table_model.dataArray()



def test_setDataGreaterThanIsSequential(good_dataArray_data):
    good_data = [['state','greater_than', 'gui_name'],
                [      0,          None,  "State 1"],
                [      1,         -2.00,  "State 2"],
                [      2,          3.00,  "State 3"],
                [      3,          4.00,  "State 4"]]
       
    
    table_model = AnalogStateTableModel()
    table_model.setDataArray(good_data)
    greater_than_col = table_model.greaterThanColumn()


    table_model.setData(table_model.index(3, greater_than_col, QtCore.QModelIndex()), -9.1, QtCore.Qt.EditRole)
    val = table_model.data(table_model.index(3, greater_than_col, QtCore.QModelIndex()),  QtCore.Qt.DisplayRole)
    assert val == 4.00
    
    table_model.setData(table_model.index(3, greater_than_col, QtCore.QModelIndex()), 3.00, QtCore.Qt.EditRole)
    val = table_model.data(table_model.index(3, greater_than_col, QtCore.QModelIndex()),  QtCore.Qt.DisplayRole)
    assert val == 4.00
    
    table_model.setData(table_model.index(2, greater_than_col, QtCore.QModelIndex()), 3.1, QtCore.Qt.EditRole)
    val = table_model.data(table_model.index(2, greater_than_col, QtCore.QModelIndex()),  QtCore.Qt.DisplayRole)
    assert val == 3.1
    
    table_model.setData(table_model.index(1, greater_than_col, QtCore.QModelIndex()), -23.1, QtCore.Qt.EditRole)
    val = table_model.data(table_model.index(1, greater_than_col, QtCore.QModelIndex()),  QtCore.Qt.DisplayRole)
    assert val == -23.1





def test_flags(good_dataArray_data):
    for good_data in good_dataArray_data:
        table_model = AnalogStateTableModel()
        table_model.setDataArray(good_data)

        greater_than_col = table_model.greaterThanColumn()
        name_col         = table_model.nameColumn()

        flags = table_model.flags(table_model.index(0, greater_than_col, QtCore.QModelIndex()))
        assert flags == QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable
        
        flags = table_model.flags(table_model.index(0, name_col, QtCore.QModelIndex()))
        assert flags == QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable
        
        flags = table_model.flags(table_model.index(len(good_data)-2, name_col, QtCore.QModelIndex()))
        assert flags == QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable
        


def test_states(good_dataArray_data):
    for good_data in good_dataArray_data:
        table_model = AnalogStateTableModel()
        table_model.setDataArray(good_data)

        states   = table_model.states()
        states_2 = copy.deepcopy(table_model.states())

        assert len(states) == len(good_data)-1
        for state in states:
            assert isinstance(state, str)

        #Check that we have a copy of them
        for state in states:
            state = state + '-false'
        assert states_2 == table_model.states()


