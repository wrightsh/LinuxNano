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
def good_states():
    pins_1 = ['pin_a']
    pins_2 = ['pin_b','pin_a']
    pins_3 = ['pin_c','pin_b','pin_a']
    pins_4 = ['pin_d','pin_c','pin_b','pin_a']

    data_1 = ['btn_1', 'btn_2']
    data_2 = ['btn_1', 'btn_2', 'btn_2', 'btn_4']
    data_3 = ['btn_1', 'btn_2', 'btn_2', 'btn_4', 'btn_5', 'btn_6', 'btn_7', 'btn_8']

    data_4 = ['btn_1', 'btn_2', 'btn_2', 'btn_4', 'btn_5', 'btn_6', 'btn_7', 'btn_8',
              'btn_9', 'btn_10', 'btn_11', 'btn_12', 'btn_13', 'btn_14', 'btn_15', 'btn_16']

    is_used_1 = [True, True]
    is_used_2 = [True, True, False, True]
    is_used_3 = [True, True, False, True, True, True, False, True]
    is_used_4 = [True, True, False, True, True, True, False, True,
                 True, True, False, True, True, True, False, True]

    return [ (pins_1, data_1, is_used_1),
             (pins_2, data_2, is_used_2),
             (pins_3, data_3, is_used_3),
             (pins_4, data_4, is_used_4)]



def test_setDataArray(good_states):
    for data in good_states:
        table_model = DigitalStateTableModel(allow_is_used = True)
        table_model.setHalPins(data[0])
        table_model.setStates(data[1])
        table_model.setIsUsed(data[2])

        assert data[0] == table_model.halPins()
        assert data[1] == table_model.states()
        assert data[2] == table_model.isUsed()


    table_model.setHalPins(['pin_a'])

    with pytest.raises(ValueError):
        data = ['btn_1', 'btn_2', 'btn_1_too_many']
        table_model.setStates(data)

    with pytest.raises(TypeError):
        data = [True, 'false']
        table_model.setIsUsed(data)

    with pytest.raises(TypeError):
        data = [ ("BTN 1", True),
                 ("BTN 4", True)]
        table_model.setStates(data)




#TODO Figure out if there's any logic in this
def test_dataArray(good_states):
    #Check if we get the array back and start editing it that we're editing a copy and not the classes actual _data
    for data in good_states:
        table_model = DigitalStateTableModel(allow_is_used = True)
        table_model.setHalPins(data[0])
        table_model.setStates(data[1])

        returned_array = table_model.states()
        returned_array_copy = copy.deepcopy(returned_array)

        returned_array.pop()
        assert returned_array_copy == table_model.states()


def test_rowCount(good_states):
    for data in good_states:
        table_model = DigitalStateTableModel(allow_is_used = True)
        table_model.setHalPins(data[0])
        table_model.setStates(data[1])

        assert table_model.rowCount() == len(data[1])


def test_columnCount(good_states):
    for data in good_states:
        table_model = DigitalStateTableModel(allow_is_used = False)
        table_model.setHalPins(data[0])
        table_model.setStates(data[1])

        if   len(data[1]) == 2 : assert table_model.columnCount() == 2
        elif len(data[1]) == 4 : assert table_model.columnCount() == 3
        elif len(data[1]) == 8 : assert table_model.columnCount() == 4
        elif len(data[1]) == 16: assert table_model.columnCount() == 5


def test_headerData(good_states):
    for data in good_states:
        table_model = DigitalStateTableModel(allow_is_used = True)
        table_model.setHalPins(data[0])
        table_model.setStates(data[1])
        table_model.setIsUsed(data[2])

        assert 'GUI Name' == table_model.headerData(table_model.nameColumn(), QtCore.Qt.Horizontal, QtCore.Qt.DisplayRole)
        assert 'Is Used'  == table_model.headerData(table_model.isUsedColumn(), QtCore.Qt.Horizontal, QtCore.Qt.DisplayRole)
        assert 'Is Used'  != table_model.headerData(0, QtCore.Qt.Horizontal, QtCore.Qt.DisplayRole)

        #check vertical header
        num_rows = len(data[1])
        for row in range(num_rows):
            assert str(row) == table_model.headerData(row, QtCore.Qt.Vertical, QtCore.Qt.DisplayRole)


def test_data(good_states):
    for data in good_states:
        table_model = DigitalStateTableModel(allow_is_used = True)
        table_model.setHalPins(data[0])
        table_model.setStates(data[1])
        table_model.setIsUsed(data[2])

        for i, itm in enumerate(data[1]):
            assert itm == table_model.data(table_model.index(i,table_model.nameColumn(),QtCore.QModelIndex()), QtCore.Qt.DisplayRole)

        for i, itm in enumerate(data[2]):
            assert itm == table_model.data(table_model.index(i,table_model.isUsedColumn(),QtCore.QModelIndex()), QtCore.Qt.DisplayRole)





def test_setData(good_states):
    for data in good_states:
        table_model = DigitalStateTableModel(allow_is_used = True)
        table_model.setHalPins(data[0])
        table_model.setStates(data[1])
        table_model.setIsUsed(data[2])

        is_used_col = table_model.isUsedColumn()
        name_col    = table_model.nameColumn()
        num_bits    = table_model.numberOfBits()
        num_rows    = len(data[1])

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


def test_flags(good_states):
    for data in good_states:
        table_model = DigitalStateTableModel(allow_is_used = True)
        table_model.setHalPins(data[0])
        table_model.setStates(data[1])

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
    table_model = DigitalStateTableModel(allow_is_used = True)

    data_1 = ['BTN 1','BTN 2']

    table_model.setHalPins(['my_pin'])
    table_model.setStates(data_1)

    table_model.setNumberOfBits(1)

    assert data_1 == table_model.states()

    #set it to different number of bits
    for i in [2,3,4,1,1]:
        table_model.setNumberOfBits(i)
        arr = table_model.states()
        assert len(arr) == 2<<(i-1)
        assert arr[0] == "BTN 1"
        assert arr[1] == "BTN 2"

    last_good_arr = table_model.states()

    #Set to some not allowed numbers
    for i in [0,-1,5,10]:
        with pytest.raises(ValueError):
            table_model.setNumberOfBits(i)
