#!/usr/bin/python3
# -*- coding: utf-8 -*-
from PyQt5 import QtGui, QtWidgets
from linuxnano.strings import strings

class ToolTreeView(QtWidgets.QTreeView):
    def __init__(self, parent=None):
        QtWidgets.QTreeView.__init__(self, parent)

    def contextMenuEvent(self, event):
        if self.selectionModel().selection().indexes():
            item = self.selectedIndexes()[0]
            current_index = item.model().mapToSource(item)
            node = current_index.internalPointer()

            #Setup the menu
            menu = QtWidgets.QMenu(self)
            add_menu = menu.addMenu('Add')

            if current_index.internalPointer().typeInfo() is not strings.DEVICE_ICON_NODE:
                menu.addAction("Delete")
            menu.addAction("Export")

            if current_index.internalPointer().typeInfo() == strings.SYSTEM_NODE:
                add_menu.addAction('System')

            possible_children = self.model().possibleChildren(current_index)
            for possible_child in possible_children:
                if   possible_child == strings.DEVICE_NODE : add_menu.addAction('Device')
                elif possible_child == strings.D_IN_NODE   : add_menu.addAction('Digital Input')
                elif possible_child == strings.A_IN_NODE   : add_menu.addAction('Analog Input')
                elif possible_child == strings.D_OUT_NODE  : add_menu.addAction('Digital Output')
                elif possible_child == strings.A_OUT_NODE  : add_menu.addAction('Analog Output')

            #Do the action from the menu
            action = menu.exec_(self.mapToGlobal(event.pos()))

            if action is not None:
                if   action.text() == "System"          : self.model().insertChild(current_index.parent(), strings.SYSTEM_NODE, current_index.row()+1)
                elif action.text() == "Device"          :
                    new_index = self.model().insertChild(current_index, strings.DEVICE_NODE)
                    self.model().insertChild(new_index, strings.DEVICE_ICON_NODE)
                elif action.text() == "Digital Input"   : new_index = self.model().insertChild(current_index, strings.D_IN_NODE)
                elif action.text() == "Analog Input"    : self.model().insertChild(current_index, strings.A_IN_NODE)
                elif action.text() == "Digital Output"  : self.model().insertChild(current_index, strings.D_OUT_NODE)
                elif action.text() == "Analog Output"   : self.model().insertChild(current_index, strings.A_OUT_NODE)

                elif action.text() == "Delete":
                    result = QtWidgets.QMessageBox.question(self,"Delete...?", "Are you sure you want to delete " + str(node.name),
                                                              QtWidgets.QMessageBox.Yes| QtWidgets.QMessageBox.No)

                    if result == QtWidgets.QMessageBox.Yes:
                        self.model().removeRows(current_index.row(),1,current_index.parent())

                elif action.text() == "Export":
                    options = QtWidgets.QFileDialog.Options()
                    #FIXME GTK Error
                    #options |= QtWidgets.QFileDialog.DontUseNativeDialog

                    export_dialog = QtWidgets.QFileDialog(options=options)
                    export_dialog.setFileMode(QtWidgets.QFileDialog.AnyFile)

                    export_dialog.setWindowTitle('Export Node as XML')
                    #export_dialog.setDirectory(EXPORT_DIR)
                    export_dialog.setAcceptMode(QtWidgets.QFileDialog.AcceptSave)
                    export_dialog.setNameFilter('XML files (*.xml)')
                    export_dialog.setDefaultSuffix('xml')
                    if export_dialog.exec_() == QtWidgets.QFileDialog.Accepted:
                        print("current index type: ", current_index.internalPointer().typeInfo())
                        #if current_index.internalPointer().typeInfo() == strings.TOOL_NODE:
                        #    print('get the parent')
                        #    current_index = current_index.parent()

                        file = open(export_dialog.selectedFiles()[0],'w')
                        file.write(current_index.internalPointer().asXml())
                        file.close()
