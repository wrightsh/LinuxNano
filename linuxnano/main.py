#!/usr/bin/env python3
# -.- coding: utf-8 -.-
import sys
from PyQt5 import QtCore, QtGui, QtWidgets

import xml.etree.ElementTree as ET
from linuxnano.tool_model import ToolModel
from linuxnano.tool_editor import ToolEditor
from linuxnano.tool_manual_view import ToolManualView
from linuxnano.strings import strings

from linuxnano.hardware import HalReader

import gc, pprint

# sudo halcompile --install linuxnano/HAL/hardware_sim.comp
# clear; pytest 'tests/test_device_manual_view.py' -k 'test_two' -s

class Window(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super().__init__()

        self.reader = HalReader()

        tree = ET.parse('tests/tools/tool_model_1.xml')
        self.tool_model = ToolModel()
        self.tool_model.loadTool(tree)

        self.setWindowTitle('LinuxNano')
        self.resize(800,600)

        manual_view = ToolManualView(self.tool_model)
        manual_view.setWindowTitle('Manual')

        manual_view2 = ToolManualView(self.tool_model)
        manual_view2.setWindowTitle('Manual-2')

        tool_editor = ToolEditor()
        tool_editor.setModel(self.tool_model)
        tool_editor.setWindowTitle('Tool Editor')

        dock1 = QtWidgets.QDockWidget('Manual', self)
        dock1.setWidget(manual_view)


        dock2 = QtWidgets.QDockWidget('Tool Editor', self)
        dock2.setWidget(tool_editor)

        dock3 = QtWidgets.QDockWidget('Manual-2', self)
        dock3.setWidget(manual_view2)

        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, dock1)
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, dock2)
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, dock3)
        self.tabifyDockWidget(dock1, dock2)
        self.tabifyDockWidget(dock2, dock3)


        self.reader.setModel(self.tool_model)
        #self.reader.start()


        extractAction = QtWidgets.QAction("collect garbage", self)
        extractAction.triggered.connect(self.collectGarbage)

        stopAction = QtWidgets.QAction("Stop Hal Reader", self)
        stopAction.triggered.connect(self.stopReader)

        startAction = QtWidgets.QAction("Start Hal Reader", self)
        startAction.triggered.connect(self.startReader)

        self.file_menu = self.menuBar().addMenu('&File')
        self.file_menu.addAction(extractAction)
        self.file_menu.addAction(stopAction)
        self.file_menu.addAction(startAction)


    def collectGarbage(self):
        pp = pprint.PrettyPrinter(indent=4)
        pp.pprint(gc.get_stats())
        gc.collect()
        pp.pprint(gc.get_stats())


    def closeEvent(self, event):
        quit_msg = "Are you sure you want to exit the program?"
        reply = QtWidgets.QMessageBox.question(self, 'Message', quit_msg, QtWidgets.QMessageBox.Yes, QtWidgets.QMessageBox.No)

        if reply == QtWidgets.QMessageBox.Yes:
            self.reader.stop()
            event.accept()
        else:
            event.ignore()

    def startReader(self):
        self.reader.start()


    def stopReader(self):
        self.reader.stop()










if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    #app.setStyle("fusion") #Changing the style
    w = Window()
    w.show()
    sys.exit(app.exec_())
