#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pytest
from PyQt5 import QtCore, QtWidgets, QtGui
from linuxnano.views.widgets.behavior_editor_view import BTEditor
from linuxnano.bt_model import BTModel
import xml.etree.ElementTree as ET

#from linuxnano.tool_model import ToolModel

#from linuxnano.message_box import MessageBox
from linuxnano.flags import TestingFlags
from linuxnano.strings import strings
import json

@pytest.fixture
def open_window(qtbot):
    def callback(window):
        widget = window()
        qtbot.addWidget(widget)
        widget.resize(900,900)
        widget.show()
        widget.setWindowTitle(widget.__class__.__name__)
        qtbot.wait_for_window_shown(widget)
        qtbot.wait(TestingFlags.TEST_WAIT_LONG)
        return widget
    return callback


@pytest.fixture()
def tool_model():
    tree = ET.parse('tests/tools/tool_model_1.xml')
    tool_model = ToolModel()
    tool_model.loadTool(tree)

    return tool_model


def test_one(qtbot, open_window):
    editor = open_window(BTEditor)
    editor2 = open_window(BTEditor)


    bt_model = BTModel()

    file = 'tests/behaviors/test_1.json'
    with open(file) as f:
        json_data = json.load(f)

    bt_model.loadJSON(json_data)


    #tree = open_window(QtWidgets.QTreeView)
    #tree.setModel(bt_model)

    editor.setModel(bt_model)
    editor2.setModel(bt_model)
    assert editor.isVisible()




    #print(bt_model.asJSON())

    index =  bt_model.index(0, 0, QtCore.QModelIndex())

    #qtbot.wait(TestingFlags.TEST_WAIT_LONG)
    #bt_model.setData(index.siblingAtColumn(1), -300)
    #qtbot.wait(TestingFlags.TEST_WAIT_LONG)
    #bt_model.setData(index.siblingAtColumn(2), -300)

    print(index.siblingAtColumn(1))







    #export_dialog = QtWidgets.QFileDialog()
    #export_dialog.setFileMode(QtWidgets.QFileDialog.AnyFile)
#
    #export_dialog.setWindowTitle('Export as XML')
    #export_dialog.setAcceptMode(QtWidgets.QFileDialog.AcceptSave)
    #export_dialog.setNameFilter('XML files (*.xml)')
    #export_dialog.setDefaultSuffix('xml')
#
    #if export_dialog.exec_() == QtWidgets.QFileDialog.Accepted:
    #    file = open(export_dialog.selectedFiles()[0],'w')
    #    tree = ET.ElementTree(bt_model._root_node.asXml())
#
#
    #    tree.write(file, encoding='unicode')


        #file = open(export_dialog.selectedFiles()[0],'w')
        #file.write(bt_model._root_node.asXml())
        #file.close()

    if TestingFlags.ENABLE_MANUAL_TESTING:
        #MessageBox("Device Editor Testing")
        qtbot.stopForInteraction()
