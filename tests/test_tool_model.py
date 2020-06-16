#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pytest

from PyQt5 import QtCore, QtWidgets

from linuxnano.flags import TestingFlags
from linuxnano.strings import strings

from linuxnano.tool_model import ToolModel
import xml.etree.ElementTree as ET
import json


#@pytest.fixture()
#def my_tool ():
#    return json_data

#@pytest.fixture()
#def tool_model_1(my_tool):
#    model = ToolModel()
#    model.loadTool(my_tool)

#    return tool_model


def test_ToolModel_loadJSON():
    model = ToolModel()
    file = 'tests/tools/basic_tool_1.json'
    with open(file) as f:
        json_data = json.load(f)

    model.loadJSON(json_data)


        #TODO: assert json_data == json.loads(model.asJSON())



def test_Tool_Model_build_a_tool():
    model = ToolModel()

    root_index =  model.index(0, 0, QtCore.QModelIndex())

    tool_index = model.insertChild(root_index, strings.TOOL_NODE)
    sys1_index = model.insertChild(tool_index, strings.SYSTEM_NODE)
    dev1_index = model.insertChild(sys1_index, strings.DEVICE_NODE)

    icon = model.insertChild(dev1_index, strings.DEVICE_ICON_NODE)
    d_in_index = model.insertChild(dev1_index, strings.D_IN_NODE)
    d_out_index = model.insertChild(dev1_index, strings.D_OUT_NODE)
    a_in_index = model.insertChild(dev1_index, strings.A_IN_NODE)
    a_out_index = model.insertChild(dev1_index, strings.A_OUT_NODE)
    bool_var_index = model.insertChild(dev1_index, strings.BOOL_VAR_NODE)
    float_var_index = model.insertChild(dev1_index, strings.FLOAT_VAR_NODE)




'''Fix below '''









def itest_ToolModel_rowCount(tool_model_1):
    tool_index = tool_model_1.index(0, 0, QtCore.QModelIndex())
    system_index = tool_index.child(0, 0)
    device_index = system_index.child(0, 0)

    assert tool_model_1.rowCount(tool_index) == 1
    assert tool_model_1.rowCount(system_index) == 3
    assert tool_model_1.rowCount(device_index) == 4

def itest_ToolModel_columnCount(tool_model_1):
    tool_index = tool_model_1.index(0, 0, QtCore.QModelIndex())
    assert tool_model_1.columnCount(tool_index) == 2

def itest_ToolModel_possibleChildren(tool_model_1):
    tool_index = tool_model_1.index(0, 0, QtCore.QModelIndex())
    system_index = tool_index.child(0, 0)
    device_index = system_index.child(0, 0)

    assert tool_model_1.possibleChildren(tool_index) == [strings.SYSTEM_NODE]
    assert tool_model_1.possibleChildren(system_index) == [strings.DEVICE_NODE]
    assert tool_model_1.possibleChildren(device_index) == [strings.DEVICE_ICON_NODE, strings.D_IN_NODE, strings.D_OUT_NODE, strings.A_IN_NODE, strings.A_OUT_NODE]


def itest_ToolModel_allowedInsertRows(tool_model_1):
    tool_index = tool_model_1.index(0, 0, QtCore.QModelIndex())
    system_index = tool_index.child(0, 0)
    device_index = system_index.child(0, 0)

    assert tool_model_1.allowedInsertRows(tool_index, strings.SYSTEM_NODE) == [0,1]
    assert tool_model_1.allowedInsertRows(system_index, strings.DEVICE_NODE) == [0,1,2,3]
    assert tool_model_1.allowedInsertRows(device_index, strings.D_IN_NODE) == [1,2,3,4]

def itest_ToolModel_insertChild(tool_model_1):
    tool_index = tool_model_1.index(0, 0, QtCore.QModelIndex())
    system_index = tool_index.child(0, 0)
    device_index = system_index.child(0, 0)

    num_devices = tool_model_1.rowCount(system_index)
    new_device_index = tool_model_1.insertChild(system_index, strings.DEVICE_NODE)

    assert new_device_index is not False
    assert num_devices + 1 == tool_model_1.rowCount(system_index)


    bad_index = tool_model_1.insertChild(system_index, "Dig_Inptu_Node")
    assert bad_index == False

    bad_index = tool_model_1.insertChild(system_index, strings.DEVICE_NODE, 843)
    assert bad_index == False

    bad_index = tool_model_1.insertChild(system_index, strings.SYSTEM_NODE)
    assert bad_index == False


def itest_ToolModel_removeRows(tool_model_1):
    tool_index = tool_model_1.index(0, 0, QtCore.QModelIndex())
    system_index = tool_index.child(0, 0)
    device_index = system_index.child(0, 0)

    num_devices = tool_model_1.rowCount(system_index)

    tool_model_1.removeRows(0, 1, system_index)

    assert num_devices - 1 == tool_model_1.rowCount(system_index)


    assert False == tool_model_1.removeRows(-1, 1, system_index)
    assert False == tool_model_1.removeRows('dog', 1, system_index)
    assert False == tool_model_1.removeRows(0, -10, system_index)
    assert False == tool_model_1.removeRows(0, 'cat', system_index)


def itest_ToolModel_data(tool_model_1):
    tool_index = tool_model_1.index(0, 0, QtCore.QModelIndex())
    system_index = tool_index.child(0, 0)


    device_index = system_index.child(0, 0)
    name_string = 'Foreline Valve'
    assert name_string == tool_model_1.data(device_index, QtCore.Qt.DisplayRole)
    assert name_string == tool_model_1.data(device_index, QtCore.Qt.EditRole)

    device_index = system_index.child(1, 1)
    assert strings.DEVICE_NODE == tool_model_1.data(device_index, QtCore.Qt.DisplayRole)
    assert strings.DEVICE_NODE == tool_model_1.data(device_index, QtCore.Qt.EditRole)

    device_index = system_index.child(1, 2)
    desc_string = 'a valve'
    assert desc_string == tool_model_1.data(device_index, QtCore.Qt.DisplayRole)
    assert desc_string == tool_model_1.data(device_index, QtCore.Qt.EditRole)

def itest_ToolModel_setData(tool_model_1):
    tool_index = tool_model_1.index(0, 0, QtCore.QModelIndex())
    system_index = tool_index.child(0, 0)


    device_index = system_index.child(0, 0)
    name_string = 'NEW Name Here'
    assert True == tool_model_1.setData(device_index, name_string)
    assert name_string == tool_model_1.data(device_index, QtCore.Qt.DisplayRole)


    device_index = system_index.child(1, 1)
    tool_model_1.setData(device_index, "Cant set")
    assert strings.DEVICE_NODE == tool_model_1.data(device_index, QtCore.Qt.DisplayRole)

    device_index = system_index.child(1, 2)
    description_string = 'This is the new description for the device'
    assert True == tool_model_1.setData(device_index, description_string)
    assert description_string == tool_model_1.data(device_index, QtCore.Qt.DisplayRole)


def itest_ToolModel_headerData(tool_model_1):
    assert "Name" == tool_model_1.headerData(0, QtCore.Qt.Horizontal, QtCore.Qt.DisplayRole)
    assert "Type" == tool_model_1.headerData(1, QtCore.Qt.Horizontal, QtCore.Qt.DisplayRole)

#TODO Not sure if these flags make sense currently
def itest_ToolModel_flag(tool_model_1):
    tool_index = tool_model_1.index(0, 0, QtCore.QModelIndex())
    system_index = tool_index.child(0, 0)
    device_index = system_index.child(0, 0)

    assert tool_model_1.flags(system_index) == QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable
    assert tool_model_1.flags(device_index) == QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable

def itest_ToolModel_parent(tool_model_1):
    tool_index = tool_model_1.index(0, 0, QtCore.QModelIndex())
    system_index = tool_index.child(0, 0)
    device_index = system_index.child(0, 0)

    assert system_index == tool_model_1.parent(device_index)
    assert tool_index == tool_model_1.parent(system_index)

#TODO Add once there's system Icons ??
#def itest_ToolModel_systemIcons(tool_model_1):
#    tool_index = tool_model_1.index(0, 0, QtCore.QModelIndex())
#    system_index = tool_index.child(0, 0)
#    device_index = system_index.child(0, 0)
#
#
#    icons = tool_model_1.systemIcons(system_index)
#
#
#    #TODO! Add once we stat using the icons again
#    assert len(icons) == 2




    # QtCore.Qt.DecorationRole:
