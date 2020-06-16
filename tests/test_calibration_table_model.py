#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pytest
import copy

from PyQt5 import QtCore, QtWidgets, QtGui

from linuxnano.flags import TestingFlags
from linuxnano.calibration_table_model import CalibrationTableModel


def array_print(array):
    print('\n'.join(['\t'.join([str(cell) for cell in row]) for row in array]))

@pytest.fixture
def good_data_arrays():
    tbl_1 = [['hal_value', 'gui_value'],
             [   0,  0.00],
             [  10,  0.63],
             [  50,  3.10],
             [ 100,  9.66],
             [ 255, 24.00]]

    tbl_2 = [['hal_value', 'gui_value'],
             [     0,    0.00],
             [  4000,    0.63],
             [ 16000,   24.00]]

    tbl_3 = [['hal_value', 'gui_value'],
             [     0,   0.00],
             [   255, -70.63]]


    return [tbl_1, tbl_2, tbl_3]
#TODO need to allow either increasing or decreasing
@pytest.fixture
def bad_data_arrays():
    tbl_1 = [['hal_value', 'gui_value'],
             [  10,  0.00],
             [  10,  0.63],
             [ 255, 24.00]]

    tbl_2 = [['hal_value', 'gui_value'],
             [  10,  0.00],
             [   1,  0.63],
             [ 255, 24.00]]

    tbl_3 = [['hal_value', 'gui_value'],
             [0,  0.00],
             ['cat', 0,00]]

    tbl_4 = [['hal_value', 'gui_value'],
             [0,    0.00]]

    tbl_5 = [['hal_value', 'gui_value'],
             [     10,    0.00],
             [ -40.45,    0.63],
             [ -600.1,   24.00]]

    tbl_6 = [['hal_value', 'gui_value'],
             [     10, 10],
             [ -40.45,  5],
             [ -600.1,  0]]

    return [tbl_1, tbl_2, tbl_3, tbl_4, tbl_5, tbl_6]


def test_rowCount(good_data_arrays):
    table_model = CalibrationTableModel()

    for good_data in good_data_arrays:
        table_model.setDataArray(good_data)
        assert table_model.rowCount() == len(good_data)-1

def test_columnCount(good_data_arrays):
    table_model = CalibrationTableModel()

    for good_data in good_data_arrays:
        table_model.setDataArray(good_data)
        assert table_model.columnCount() == 2

def test_headerData(good_data_arrays):
    table_model = CalibrationTableModel()

    for good_data in good_data_arrays:
        table_model.setDataArray(good_data)

        assert "HAL Value" == table_model.headerData(0,QtCore.Qt.Horizontal,QtCore.Qt.DisplayRole)
        assert "GUI Value" == table_model.headerData(1,QtCore.Qt.Horizontal,QtCore.Qt.DisplayRole)
        assert "0"         == table_model.headerData(0,QtCore.Qt.Vertical,QtCore.Qt.DisplayRole)



def test_setDataArray(good_data_arrays, bad_data_arrays):
    table_model = CalibrationTableModel()

    for good_data in good_data_arrays:
        table_model.setDataArray(good_data)
        assert good_data == table_model.dataArray()


    for bad_data in bad_data_arrays:
        with pytest.raises(Exception) as e_info:
            table_model.setDataArray(bad_data)



def test_dataArray(good_data_arrays):
    table_model = CalibrationTableModel()

    for good_data in good_data_arrays:
        table_model.setDataArray(good_data)

        returned_array = table_model.dataArray()
        returned_array_copy = copy.deepcopy(returned_array)

        for i, row in enumerate(returned_array):
            for j, val in enumerate(row):
                returned_array[i][j] = None

        assert returned_array_copy == table_model.dataArray()


def test_setData_increasing():
    tbl_1 = [['hal_value', 'gui_value'],
             [          0,        0.00],
             [         10,        0.60],
             [         50,        3.10],
             [        100,        9.00],
             [        160,       24.00]]

    table_model = CalibrationTableModel()
    table_model.setDataArray(tbl_1)


    #These should succeed at changing the data
    index = table_model.index(0,0, QtCore.QModelIndex())
    table_model.setData(index, -12.3, QtCore.Qt.EditRole)
    assert -12.3 == table_model.data(index,  QtCore.Qt.DisplayRole)

    index = table_model.index(0,1, QtCore.QModelIndex())
    table_model.setData(index, -1., QtCore.Qt.EditRole)
    assert -1. == table_model.data(index,  QtCore.Qt.DisplayRole)


    #These should fail at changing the data
    index = table_model.index(0,0, QtCore.QModelIndex())
    with pytest.raises(Exception) as e_info:
        table_model.setData(index, 3999, QtCore.Qt.EditRole)

    index = table_model.index(0,1, QtCore.QModelIndex())
    with pytest.raises(Exception) as e_info:
        table_model.setData(index, 16000, QtCore.Qt.EditRole)

    index = table_model.index(2,0, QtCore.QModelIndex())
    with pytest.raises(Exception) as e_info:
        table_model.setData(index, 'cat', QtCore.Qt.EditRole)

    #These should work
    index = table_model.index(2,0, QtCore.QModelIndex())
    table_model.setData(index, 10.01, QtCore.Qt.EditRole)
    assert 10.01 == table_model.data(index,  QtCore.Qt.DisplayRole)

    index = table_model.index(2,1, QtCore.QModelIndex())
    table_model.setData(index, 8.999, QtCore.Qt.EditRole)
    assert 8.999 == table_model.data(index,  QtCore.Qt.DisplayRole)

def test_setData_decreasing():
    tbl_1 = [['hal_value', 'gui_value'],
             [        0.0,        1000],
             [        2.5,         900],
             [        5.0,         300],
             [        7.5,           0],
             [       10.0,        -100]]

    table_model = CalibrationTableModel()
    table_model.setDataArray(tbl_1)

    gui_col = 1
    #These should succeed at changing the data
    index = table_model.index(0,gui_col, QtCore.QModelIndex())
    table_model.setData(index, 1200, QtCore.Qt.EditRole)
    assert 1200 == table_model.data(index,  QtCore.Qt.DisplayRole)

    index = table_model.index(4,gui_col, QtCore.QModelIndex())
    table_model.setData(index, -101, QtCore.Qt.EditRole)
    assert -101 == table_model.data(index,  QtCore.Qt.DisplayRole)


    #This should fail
    index = table_model.index(4,gui_col, QtCore.QModelIndex())
    with pytest.raises(Exception) as e_info:
        table_model.setData(index, 0, QtCore.Qt.EditRole)

def test_setData_increasing_to_decreasing():
    tbl_1 = [['hal_value', 'gui_value'],
             [        0.0,        10],
             [       10.0,       100]]

    table_model = CalibrationTableModel()
    table_model.setDataArray(tbl_1)

    gui_col = 1

    #If there's just two rows we can change if it's increasing or decreasing
    index = table_model.index(0,gui_col, QtCore.QModelIndex())
    table_model.setData(index, 1200, QtCore.Qt.EditRole)
    assert 1200 == table_model.data(index,  QtCore.Qt.DisplayRole)

    #If there's just two rows we can change if it's increasing or decreasing
    index = table_model.index(1,gui_col, QtCore.QModelIndex())
    table_model.setData(index, 12000, QtCore.Qt.EditRole)
    assert 12000 == table_model.data(index,  QtCore.Qt.DisplayRole)


def test_removeRows():
    table_model = CalibrationTableModel()

    tbl_1 = [['hal_value', 'gui_value'],
             [          0,        0.00],
             [         10,        0.63],
             [         50,        3.10],
             [        100,        9.66],
             [        255,       24.00]]


    #Try removing 2 rows
    number_to_remove = 2
    row_index = 1
    table_model.setDataArray(tbl_1)
    table_model.removeRows(row_index,number_to_remove)

    tbl_2 = [['hal_value', 'gui_value'],
             [          0,        0.00],
             [        100,        9.66],
             [        255,       24.00]]

    assert tbl_2 == table_model.dataArray()


    #Try removing 1 row
    number_to_remove = 1
    row_index = 0
    table_model.removeRows(row_index,number_to_remove)

    tbl_3 = [['hal_value', 'gui_value'],
             [        100,        9.66],
             [        255,       24.00]]

    assert tbl_3 == table_model.dataArray()

    #Try removing 1 row too many!
    number_to_remove = 1
    row_index = 0
    table_model.removeRows(row_index,number_to_remove)

    assert tbl_3 == table_model.dataArray()





def test_insertRows():
    tbl_1 = [['hal_value', 'gui_value'],
             [          0,        0.00],
             [         10,        0.60],
             [         50,        3.10],
             [        100,        9.00],
             [        160,       24.00]]

    table_model = CalibrationTableModel()
    table_model.setDataArray(tbl_1)


   #First try adding 1 row
    number_to_add = 1
    row_index = 1 #it's inserted above this index

    tbl_2 = [['hal_value', 'gui_value'],
             [          0,         0.00],
             [          5,         0.30],
             [         10,         0.60],
             [         50,         3.10],
             [        100,         9.00],
             [        160,        24.00]]

    table_model.insertRows(row_index,number_to_add)
    assert tbl_2 == table_model.dataArray()


    #Try adding 2 rows
    number_to_add = 2
    row_index = 5 #it's inserted above this index
    tbl_3 = [['hal_value', 'gui_value'],
             [          0,         0.00],
             [          5,         0.30],
             [         10,         0.60],
             [         50,         3.10],
             [        100,         9.00],
             [        120,         14.0],
             [        140,         19.0],
             [        160,        24.00]]

    table_model.insertRows(row_index,number_to_add)
    assert tbl_3 == table_model.dataArray()


    #Try adding 2 rows at beginning
    number_to_add = 2
    row_index = 0 #it's inserted above this index
    tbl_4 = [['hal_value', 'gui_value'],
             [        -10,        -0.60],  #row 0
             [         -5,        -0.30],
             [          0,         0.00],
             [          5,         0.30],
             [         10,         0.60],
             [         50,         3.10],
             [        100,         9.00],
             [        120,         14.0],
             [        140,         19.0],
             [        160,        24.00]] #row 9


    table_model.insertRows(row_index,number_to_add)
    assert tbl_4 == table_model.dataArray()


    #Try adding 2 rows at the end
    number_to_add = 2
    row_index = 10 #it's inserted above this index

    tbl_5 = [['hal_value', 'gui_value'],
             [        -10,        -0.60],  #row 0
             [         -5,        -0.30],
             [          0,         0.00],
             [          5,         0.30],
             [         10,         0.60],
             [         50,         3.10],
             [        100,         9.00],
             [        120,         14.0],
             [        140,         19.0],
             [        160,        24.00],
             [        180,        29.00],
             [        200,        34.00]] #row 11

    table_model.insertRows(row_index,number_to_add)
    assert tbl_5 == table_model.dataArray()


def test_flags(good_data_arrays):

    table_model = CalibrationTableModel()
    hal_col = table_model.halValueColumn()
    gui_col = table_model.halValueColumn()

    for good_data in good_data_arrays:
        table_model.setDataArray(good_data)

        main_data = good_data[1:]


        for i, row in enumerate(main_data):
            hal_flags = table_model.flags(table_model.index(i, hal_col, QtCore.QModelIndex()))
            gui_flags = table_model.flags(table_model.index(i, gui_col, QtCore.QModelIndex()))

            assert hal_flags == QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable
            assert gui_flags == QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable
