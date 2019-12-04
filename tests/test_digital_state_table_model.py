#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pytest
import copy

from PyQt5 import QtCore, QtWidgets, QtGui

from linuxnano.flags import TestingFlags
from linuxnano.digital_state_table_model import DigitalStateTableModel



def array_print(array):
    print('\n'.join(['\t'.join([str(cell) for cell in row]) for row in array]))


@pytest.fixture
def good_dataArray_data():

    good_data_1 = [['state','gui_name','is_used']]
    good_data_2 = [['state','gui_name','is_used']]
    good_data_3 = [['state','gui_name','is_used']]
    good_data_4 = [['state','gui_name','is_used']]
    
    
    good_data_1 += [[0, "BTN 1", True],
                    [1 , "BTN 2", True]]
        
    good_data_2 += [[0, "BTN 1", True],
                    [1, "BTN 2", True],
                    [2, "BTN 3", True],
                    [3, "BTN 4", True]]
       
    good_data_3 += [[0, "BTN 1", True],
                    [1, "BTN 2", True],
                    [2, "BTN 3", True],
                    [3, "BTN 4", True],

                    [4, "BTN 5", True],
                    [5, "BTN 6", True],
                    [6, "BTN 7", True],
                    [7, "BTN 8", True]]

    good_data_4 +=[[0, "BTN 1", True],
                   [1, "BTN 2", True],
                   [2, "BTN 3", True],
                   [3, "BTN 4", True],

                   [4, "BTN 5", True],
                   [5, "BTN 6", True],
                   [6, "BTN 7", True],
                   [7, "BTN 8", True],

                   [8, "BTN 9", True],
                   [9, "BTN 10", True],
                   [10, "BTN 11", True],
                   [11, "BTN 12", True],

                   [12, "BTN 13", True],
                   [13, "BTN 14", True],
                   [14, "BTN 15", True],
                   [15, "BTN 16", True]]
    
    return [good_data_1, good_data_2, good_data_3, good_data_4]

@pytest.fixture
def good_dataArray_data_2():

    good_data_1 = [['state','gui_name']]
    good_data_2 = [['state','gui_name']]
    good_data_3 = [['state','gui_name']]
    good_data_4 = [['state','gui_name']]
    
    
    good_data_1 += [[0, "BTN 1",],
                    [1 , "BTN 2"]]
        
    good_data_2 += [[0, "BTN 1",],
                    [1, "BTN 2",],
                    [2, "BTN 3",],
                    [3, "BTN 4",]]
       
    good_data_3 += [[0, "BTN 1",],
                    [1, "BTN 2",],
                    [2, "BTN 3",],
                    [3, "BTN 4",],

                    [4, "BTN 5",],
                    [5, "BTN 6",],
                    [6, "BTN 7",],
                    [7, "BTN 8",]]

    good_data_4 +=[[ 0, "BTN 1"],
                   [ 1, "BTN 2"],
                   [ 2, "BTN 3"],
                   [ 3, "BTN 4"],

                   [ 4, "BTN 5"],
                   [ 5, "BTN 6"],
                   [ 6, "BTN 7"],
                   [ 7, "BTN 8"],

                   [ 8, "BTN 9"],
                   [ 9, "BTN 10"],
                   [10, "BTN 11"],
                   [11, "BTN 12"],

                   [12, "BTN 13"],
                   [13, "BTN 14"],
                   [14, "BTN 15"],
                   [15, "BTN 16"]]
    
    return [good_data_1, good_data_2, good_data_3, good_data_4]

@pytest.fixture
def bad_dataArray_data(): 

    bad_data_1 = [['state','gui_name','is_used']]
    bad_data_2 = [['state','gui_name','is_used']]
    bad_data_3 = [['state','gui_name','is_used']]
    bad_data_4 = [['state','gui_name','is_used']]
    
    bad_data_5 = ['stiate','gui_name','is_used']
    
    bad_data_1 += [ [0, "BTN 1", True],
                    [1, "BTN 2", True],
                    [2, "BTN 4", True]] 
    
    bad_data_2 += [ [0, "BTN 1", True],
                    ['True', "BTN 2", True],
                    [2, "BTN 4", True]] 
   
    bad_data_2 += [ [0, "BTN 1", True],
                    ["BTN 2", True],
                    [2, "BTN 4", True]]


    bad_data_4 += [ [0, "BTN 1", "True"],
                    [1 , "BTN 2", True]] 

    bad_data_5 += [[0, "BTN 1", True],
                   [1 , "BTN 2", True]]

    return [bad_data_1, bad_data_2, bad_data_3, bad_data_4]

@pytest.fixture
def bad_dataArray_data_2(): 

    bad_data_1 = [['state','gui_name']]
    bad_data_2 = [['state','gui_name']]
    bad_data_3 = [['state','gui_name']]
    bad_data_4 = [['state','gui_name']]
    
    bad_data_5 = ['stiate','gui_name']
    
    bad_data_1 += [ [0, "BTN 1"],
                    [1, "BTN 2"],
                    [2, "BTN 4"]] 
    
    bad_data_2 += [ [0, "BTN 1"],
                    ['True', "BTN 2"],
                    [2, "BTN 4"]] 
   
    bad_data_2 += [ [0, "BTN 1"],
                    ["BTN 2"],
                    [2, "BTN 4"]]

    bad_data_4 += [ [0, "BTN 1", True],
                    [1 , "BTN 2", True]] 



    return [bad_data_1, bad_data_2, bad_data_3, bad_data_4]

def test_setDataArray(good_dataArray_data, bad_dataArray_data, good_dataArray_data_2, bad_dataArray_data_2):

    for good_data in good_dataArray_data:
        table_model = DigitalStateTableModel(allow_is_used = True)
        table_model.setDataArray(good_data)
        assert good_data == table_model.dataArray()
   
    for good_data in good_dataArray_data_2:
        table_model = DigitalStateTableModel(allow_is_used = False)
        table_model.setDataArray(good_data)
        assert good_data == table_model.dataArray()
   
    for bad_data in bad_dataArray_data:
        table_model = DigitalStateTableModel(allow_is_used = True)
        table_model.setDataArray(bad_data)
        assert bad_data != table_model.dataArray()
    
    for bad_data in bad_dataArray_data_2:
        table_model = DigitalStateTableModel(allow_is_used = False)
        table_model.setDataArray(bad_data)
        assert bad_data != table_model.dataArray()
    
        
def test_dataArray(good_dataArray_data, good_dataArray_data_2):
    #Check if we get the array back and start editing it that we're editing a copy and not the classes actual _data
    
    for good_data in good_dataArray_data:
        table_model = DigitalStateTableModel(allow_is_used = True)
        table_model.setDataArray(good_data)
        
        returned_array = table_model.dataArray()
        returned_array_copy = copy.deepcopy(returned_array)
        
        for i, row in enumerate(returned_array):
            for j, val in enumerate(row):
                returned_array[i][j] = None
        
        assert returned_array_copy == table_model.dataArray()
   
    for good_data in good_dataArray_data_2:
        table_model = DigitalStateTableModel(allow_is_used = False)
        table_model.setDataArray(good_data)
        assert good_data == table_model.dataArray()
   
        returned_array = table_model.dataArray()
        returned_array_copy = copy.deepcopy(returned_array)
        
        for i, row in enumerate(returned_array):
            for j, val in enumerate(row):
                returned_array[i][j] = None
        
        assert returned_array_copy == table_model.dataArray()

        
def test_rowCount(good_dataArray_data, good_dataArray_data_2):
    
    for good_data in good_dataArray_data:
        table_model = DigitalStateTableModel(allow_is_used = True)
        table_model.setDataArray(good_data)
        assert table_model.rowCount() == len(good_data)-1
        
    for good_data in good_dataArray_data_2:
        table_model = DigitalStateTableModel(allow_is_used = False)
        table_model.setDataArray(good_data)
        assert table_model.rowCount() == len(good_data)-1 
        
def test_columnCount(good_dataArray_data, good_dataArray_data_2):
    for good_data in good_dataArray_data:
        table_model = DigitalStateTableModel(allow_is_used = True)
        table_model.setDataArray(good_data)

        if   len(good_data) == 2+1 : assert table_model.columnCount() == 3
        elif len(good_data) == 4+1 : assert table_model.columnCount() == 4
        elif len(good_data) == 8+1 : assert table_model.columnCount() == 5
        elif len(good_data) == 16+1: assert table_model.columnCount() == 6
    
    for good_data in good_dataArray_data_2:
        table_model = DigitalStateTableModel(allow_is_used = False)
        table_model.setDataArray(good_data)

        if   len(good_data) == 2+1 : assert table_model.columnCount() == 2
        elif len(good_data) == 4+1 : assert table_model.columnCount() == 3
        elif len(good_data) == 8+1 : assert table_model.columnCount() == 4
        elif len(good_data) == 16+1: assert table_model.columnCount() == 5

def test_headerData(good_dataArray_data, good_dataArray_data_2):
    for good_data in good_dataArray_data:
        table_model = DigitalStateTableModel(allow_is_used = True)
        table_model.setDataArray(good_data)

        num_cols = len(good_data[0]) 
        num_rows = len(good_data) - 1

        #check horizontal header header
        if num_rows == 2:
            assert 'bit_0'    == table_model.headerData(0, QtCore.Qt.Horizontal, QtCore.Qt.DisplayRole)
            assert 'GUI Name' == table_model.headerData(1, QtCore.Qt.Horizontal, QtCore.Qt.DisplayRole)
            assert 'Is Used'  == table_model.headerData(2, QtCore.Qt.Horizontal, QtCore.Qt.DisplayRole)

        elif num_rows == 4:
            assert 'bit_1'    == table_model.headerData(0, QtCore.Qt.Horizontal, QtCore.Qt.DisplayRole)
            assert 'bit_0'    == table_model.headerData(1, QtCore.Qt.Horizontal, QtCore.Qt.DisplayRole)
            assert 'GUI Name' == table_model.headerData(2, QtCore.Qt.Horizontal, QtCore.Qt.DisplayRole)
            assert 'Is Used'  == table_model.headerData(3, QtCore.Qt.Horizontal, QtCore.Qt.DisplayRole)

        elif num_rows == 8:
            assert 'bit_2'    == table_model.headerData(0, QtCore.Qt.Horizontal, QtCore.Qt.DisplayRole)
            assert 'bit_1'    == table_model.headerData(1, QtCore.Qt.Horizontal, QtCore.Qt.DisplayRole)
            assert 'bit_0'    == table_model.headerData(2, QtCore.Qt.Horizontal, QtCore.Qt.DisplayRole)
            assert 'GUI Name' == table_model.headerData(3, QtCore.Qt.Horizontal, QtCore.Qt.DisplayRole)
            assert 'Is Used'  == table_model.headerData(4, QtCore.Qt.Horizontal, QtCore.Qt.DisplayRole)
        
        elif num_rows == 16:
            assert 'bit_3'    == table_model.headerData(0, QtCore.Qt.Horizontal, QtCore.Qt.DisplayRole)
            assert 'bit_2'    == table_model.headerData(1, QtCore.Qt.Horizontal, QtCore.Qt.DisplayRole)
            assert 'bit_1'    == table_model.headerData(2, QtCore.Qt.Horizontal, QtCore.Qt.DisplayRole)
            assert 'bit_0'    == table_model.headerData(3, QtCore.Qt.Horizontal, QtCore.Qt.DisplayRole)
            assert 'GUI Name' == table_model.headerData(4, QtCore.Qt.Horizontal, QtCore.Qt.DisplayRole)
            assert 'Is Used'  == table_model.headerData(5, QtCore.Qt.Horizontal, QtCore.Qt.DisplayRole)
        

        #check vertical header
        for row in range(num_rows):
            assert str(row) == table_model.headerData(row, QtCore.Qt.Vertical, QtCore.Qt.DisplayRole)


    #Check with allow_is_used diabled
    for good_data in good_dataArray_data_2:
        table_model = DigitalStateTableModel(allow_is_used = False)
        table_model.setDataArray(good_data)

        num_cols = len(good_data[0]) 
        num_rows = len(good_data) - 1

        #check horizontal header header
        if num_rows == 2:
            assert 'bit_0'    == table_model.headerData(0, QtCore.Qt.Horizontal, QtCore.Qt.DisplayRole)
            assert 'GUI Name' == table_model.headerData(1, QtCore.Qt.Horizontal, QtCore.Qt.DisplayRole)

        elif num_rows == 4:
            assert 'bit_1'    == table_model.headerData(0, QtCore.Qt.Horizontal, QtCore.Qt.DisplayRole)
            assert 'bit_0'    == table_model.headerData(1, QtCore.Qt.Horizontal, QtCore.Qt.DisplayRole)
            assert 'GUI Name' == table_model.headerData(2, QtCore.Qt.Horizontal, QtCore.Qt.DisplayRole)

        elif num_rows == 8:
            assert 'bit_2'    == table_model.headerData(0, QtCore.Qt.Horizontal, QtCore.Qt.DisplayRole)
            assert 'bit_1'    == table_model.headerData(1, QtCore.Qt.Horizontal, QtCore.Qt.DisplayRole)
            assert 'bit_0'    == table_model.headerData(2, QtCore.Qt.Horizontal, QtCore.Qt.DisplayRole)
            assert 'GUI Name' == table_model.headerData(3, QtCore.Qt.Horizontal, QtCore.Qt.DisplayRole)
        
        elif num_rows == 16:
            assert 'bit_3'    == table_model.headerData(0, QtCore.Qt.Horizontal, QtCore.Qt.DisplayRole)
            assert 'bit_2'    == table_model.headerData(1, QtCore.Qt.Horizontal, QtCore.Qt.DisplayRole)
            assert 'bit_1'    == table_model.headerData(2, QtCore.Qt.Horizontal, QtCore.Qt.DisplayRole)
            assert 'bit_0'    == table_model.headerData(3, QtCore.Qt.Horizontal, QtCore.Qt.DisplayRole)
            assert 'GUI Name' == table_model.headerData(4, QtCore.Qt.Horizontal, QtCore.Qt.DisplayRole)
        

        #check vertical header
        for row in range(num_rows):
            assert str(row) == table_model.headerData(row, QtCore.Qt.Vertical, QtCore.Qt.DisplayRole)

def test_data(good_dataArray_data):
    for good_data in good_dataArray_data:
        table_model = DigitalStateTableModel(allow_is_used = True)
        table_model.setDataArray(good_data)

        good_data_main = good_data[1:]
        for i, row in enumerate(good_data_main):
            assert good_data_main[i][1] == table_model.data(table_model.index(i,table_model.nameColumn(),QtCore.QModelIndex()), QtCore.Qt.DisplayRole)
            assert good_data_main[i][2] == table_model.data(table_model.index(i,table_model.isUsedColumn(),QtCore.QModelIndex()), QtCore.Qt.DisplayRole)
           
def test_setData(good_dataArray_data):
    for good_data in good_dataArray_data:
        table_model = DigitalStateTableModel(allow_is_used = True)
        table_model.setDataArray(good_data)



        is_used_col = table_model.isUsedColumn()
        name_col    = table_model.nameColumn()
        num_bits    = table_model.numberOfBits()

        num_cols = len(good_data[0])
        num_rows = len(good_data)-1 #not including the header row


        #Try setting some of the isUsed column
        table_model.setData(table_model.index(0, is_used_col, QtCore.QModelIndex()), False, QtCore.Qt.EditRole)
        val = table_model.data(table_model.index(0, is_used_col, QtCore.QModelIndex()),  QtCore.Qt.DisplayRole)
        assert val == True

        table_model.setData(table_model.index(num_rows-1, is_used_col, QtCore.QModelIndex()), False, QtCore.Qt.EditRole)
        val = table_model.data(table_model.index(num_rows-1, is_used_col, QtCore.QModelIndex()),  QtCore.Qt.DisplayRole)
        assert val == False


        table_model.setData(table_model.index(0, is_used_col, QtCore.QModelIndex()), True, QtCore.Qt.EditRole)
        val = table_model.data(table_model.index(0, is_used_col, QtCore.QModelIndex()),  QtCore.Qt.DisplayRole)
        assert val == True

        table_model.setData(table_model.index(num_rows-1, is_used_col, QtCore.QModelIndex()), True, QtCore.Qt.EditRole)
        val = table_model.data(table_model.index(num_rows-1, is_used_col, QtCore.QModelIndex()),  QtCore.Qt.DisplayRole)
        assert val == True



        #Try setting some of the name column
        table_model.setData(table_model.index(0, name_col, QtCore.QModelIndex()), "Fast Off", QtCore.Qt.EditRole)
        val = table_model.data(table_model.index(0, name_col, QtCore.QModelIndex()),  QtCore.Qt.DisplayRole)
        assert val == "Fast Off"

        table_model.setData(table_model.index(num_rows-1, name_col, QtCore.QModelIndex()), "Start", QtCore.Qt.EditRole)
        val = table_model.data(table_model.index(num_rows-1, name_col, QtCore.QModelIndex()),  QtCore.Qt.DisplayRole)
        assert val == "Start"


        #Try setting 0,0 to True, this should always be false
        table_model.setData(table_model.index(0, 0, QtCore.QModelIndex()), True, QtCore.Qt.EditRole)
        val = table_model.data(table_model.index(0, 0, QtCore.QModelIndex()),  QtCore.Qt.DisplayRole)
        assert val == False


        #Try setting 0,0 to True, this should always be false
        table_model.setData(table_model.index(0, num_bits-1, QtCore.QModelIndex()), False, QtCore.Qt.EditRole)
        val = table_model.data(table_model.index(0, num_bits-1, QtCore.QModelIndex()),  QtCore.Qt.DisplayRole)
        assert val == False

def test_flags(good_dataArray_data):
    for good_data in good_dataArray_data:
        table_model = DigitalStateTableModel(allow_is_used = True)
        table_model.setDataArray(good_data)

        is_used_col = table_model.isUsedColumn()
        name_col    = table_model.nameColumn()

        flags = table_model.flags(table_model.index(0, 0, QtCore.QModelIndex()))
        assert flags == QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable

        flags = table_model.flags(table_model.index(0, is_used_col, QtCore.QModelIndex()))
        assert flags == QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable
                
        flags = table_model.flags(table_model.index(1, name_col, QtCore.QModelIndex()))
        assert flags == QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable
        
        flags = table_model.flags(table_model.index(1, is_used_col, QtCore.QModelIndex()))
        assert flags == QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable

def test_setNumberOfBits():
    table_model = DigitalStateTableModel(allow_is_used = False)
    good_data_1 = [ ['state','gui_name'],
                    [False, "BTN 1"],
                    [True , "BTN 2"]]
        
    table_model.setDataArray(good_data_1)
    table_model.setNumberOfBits(1)

    assert good_data_1 == table_model.dataArray()
  
    #set it to different number of bits
    for i in [2,3,4,1,1]:
        table_model.setNumberOfBits(i)
        arr = table_model.dataArray()
        assert len(arr)-1 == 2<<(i-1)
        assert arr[1][1] == "BTN 1"
        assert arr[2][1] == "BTN 2"

    
    last_good_arr = table_model.dataArray()

    #Set to some not allowed numbers
    for i in [0,-1,5,10]:
        assert False == table_model.setNumberOfBits(i)
        assert last_good_arr == table_model.dataArray()

def test_states(good_dataArray_data, good_dataArray_data_2):
    for good_data in good_dataArray_data:
        table_model = DigitalStateTableModel(allow_is_used = True)
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


    for good_data in good_dataArray_data_2:
        table_model = DigitalStateTableModel(allow_is_used = False)
        table_model.setDataArray(good_data)

        states = table_model.states()

        assert len(states) == len(good_data)-1
        for state in states:
            assert isinstance(state, str)




