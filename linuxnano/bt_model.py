from PyQt5 import QtCore, QtGui

from linuxnano.strings import strings
from linuxnano.bt_data import Node, SequenceNode, SelectorNode, WhileNode, SetOutputNode, WaitTimeNode
from linuxnano.message_box import MessageBox

class BTModel(QtCore.QAbstractItemModel):
    #Behavior tree model
    def __init__(self, parent=None):
        super().__init__(parent)
        self._root_node = Node()


    def asJSON(self):
        return self._root_node.asJSON()

    def loadJSON(self, json):
        try:
            if json['type_info'] == 'root':
                root_index = self.createIndex(0, 0, self._root_node)
                root_index.internalPointer().loadAttrs(json)

                for child in json['children']:
                    index = self.insertChild(root_index, child['type_info'])
                    index.internalPointer().loadAttrs(child)
                    self._recurseJSON(index, child)

        except Exception as e:
            MessageBox("Failed to behavior from JSON", e)
            return False


    def _recurseJSON(self, parent_index, json):
        for child in json['children']:
            index = self.insertChild(parent_index, child['type_info'])
            index.internalPointer().loadAttrs(child)
            self._recurseJSON(index, child)






    def rowCount(self, parent):
        '''Returns the number of children'''
        if not parent.isValid():
            parentNode = self._root_node
        else:
            parentNode = parent.internalPointer()

        return parentNode.childCount()

    def columnCount(self, parent):
        '''Number of columns the QTreeView displays '''
        return 1


    def insertChild(self, parent_index, child_type, insert_row = None):
        parent_node  = parent_index.internalPointer()

        if insert_row is None:
            insert_row = parent_index.internalPointer().childCount()

        if insert_row is not False:
            self.beginInsertRows(parent_index, insert_row, insert_row)

            if    child_type == strings.SEQUENCE_NODE    : parent_node.insertChild(insert_row, SequenceNode())
            elif  child_type == strings.SELECTOR_NODE    : parent_node.insertChild(insert_row, SelectorNode())
            elif  child_type == strings.WHILE_NODE       : parent_node.insertChild(insert_row, WhileNode())
            elif  child_type == strings.SET_OUTPUT_NODE  : parent_node.insertChild(insert_row, SetOutputNode())
            elif  child_type == strings.WAIT_TIME_NODE   : parent_node.insertChild(insert_row, WaitTimeNode())

            else: MessageBox('Attempting to insert unknown node of type', child_type)

            self.endInsertRows()

            new_child_index = self.index(insert_row, 0, parent_index)
            return new_child_index


    def removeRows(self, row, count, parent_index):
        parent_node = parent_index.internalPointer()

        if not isinstance(  row, int):
            MessageBox("Behavior Tree Model removeRows 'row' must be of type 'int', is of type: ", type(row))
            return False

        if not isinstance(count, int):
            MessageBox("Behavior Tree Model removeRows 'count' must be of type 'int', is of type: ", type(count))
            return False

        if   row <  0:
            MessageBox("Behavior Tree Model removeRows 'row' must be >= 0, is: ", row)
            return False

        if count <= 0:
            MessageBox("Behavior Tree Model removeRows 'count' must be > 0, is: ", count)
            return False


        self.beginRemoveRows(parent_index, row, row+count-1)

        for i in list(range(count)):
            parent_node.removeChild(row)

        self.endRemoveRows()



    def data(self, index, role):
        if not index.isValid():
            return None

        node = index.internalPointer()

        if role == QtCore.Qt.DisplayRole or role == QtCore.Qt.EditRole:
            return node.data(index.column())


        elif role == QtCore.Qt.DecorationRole:
            if index.column() == 0:
                return None
                #resource = node.iconResource()
                #return QtGui.QIcon(QtGui.QPixmap(resource))


    def setData(self, index, value, role=QtCore.Qt.EditRole):
        if type(value) == type(QtCore.QVariant()):
            value = value.toPyObject()

        if index.isValid() and role == QtCore.Qt.EditRole:
            node = index.internalPointer()
            node.setData(index.column(), value)
            self.dataChanged.emit(index, index)
            return True

        return False

    def headerData(self, section, orientation, role):
        if role == QtCore.Qt.DisplayRole and section == 0:
            return "Type"

    def supportedDropActions(self):
        return QtCore.Qt.MoveAction

    def flags(self, index):
        node = index.internalPointer()

        return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable | \
               QtCore.Qt.ItemIsDragEnabled | QtCore.Qt.ItemIsDropEnabled


    def parent(self, index):
        node = index.internalPointer()
        parent_node = node.parent()

        if parent_node == self._root_node:
            return QtCore.QModelIndex()

        if index.isValid():
            return self.createIndex(parent_node.row(), 0, parent_node)



    def index(self, row, column, parent_index):
        #if not self.hasIndex(row, column, parent_index):
        #    return QtCore.QModelIndex()

        if parent_index.isValid():
            parent_node = parent_index.internalPointer()
        else:
            parent_node = self._root_node

        child_item = parent_node.child(row)

        if child_item:
            return self.createIndex(row, column, child_item)
        else:
            return QtCore.QModelIndex()
