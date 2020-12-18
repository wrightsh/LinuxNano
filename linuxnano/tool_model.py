from PyQt5 import QtCore, QtGui

from linuxnano.strings import strings, col, typ
from linuxnano.data import Node, ToolNode, SystemNode, DeviceNode, DeviceIconNode, DigitalInputNode, DigitalOutputNode, AnalogInputNode, AnalogOutputNode
from linuxnano.data import BoolVarNode, FloatVarNode
from linuxnano.message_box import MessageBox



class ToolModel(QtCore.QAbstractItemModel):
    '''The tool model represents an entire tool in a tree structure.'''

    def __init__(self, parent=None):
        super().__init__(parent)
        self._root_node = ToolNode()

    def asJSON(self):
        return self._root_node.asJSON()

    def loadJSON(self, json):
        try:
            if json['type_info'] == typ.TOOL_NODE:
                self._root_node.loadAttrs(json)

                for child in json['children']:
                    index = self.insertChild(self.createIndex(0, 0, self._root_node), child['type_info'])
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
        #Number of children
        if not parent.isValid():
            parentNode = self._root_node
        else:
            parentNode = parent.internalPointer()

        return parentNode.childCount()

    def columnCount(self, parent):
        return 2 #Number of columns the QTreeView displays

    def possibleChildren(self, index):
        node_type = index.internalPointer().typeInfo()

        if   node_type == typ.TOOL_NODE:
            return [typ.SYSTEM_NODE]

        elif node_type == typ.SYSTEM_NODE:
            return [typ.DEVICE_NODE]

        elif node_type == typ.DEVICE_NODE:
            return [typ.DEVICE_ICON_NODE,
                    typ.D_IN_NODE,
                    typ.D_OUT_NODE,
                    typ.A_IN_NODE,
                    typ.A_OUT_NODE,
                    typ.BOOL_VAR_NODE,
                    typ.FLOAT_VAR_NODE]

        elif node_type == typ.DEVICE_ICON_NODE:
            return []

        elif node_type in [typ.D_IN_NODE, typ.D_OUT_NODE, typ.A_IN_NODE, typ.A_OUT_NODE, typ.BOOL_VAR_NODE, typ.FLOAT_VAR_NODE]:
            return []

    #def allowedInsertRows(self, node_index, new_child_type):
    #    node = node_index.internalPointer()
    #    node_type = node.typeInfo()

    #    if   node_type == 'root' and new_child_type == strings.TOOL_NODE:
    #        return [0]

    #    elif node_type == strings.TOOL_NODE and new_child_type == strings.SYSTEM_NODE:
    #        return list(range(1+node.childCount()))

    #    elif node_type == strings.SYSTEM_NODE and new_child_type == strings.DEVICE_NODE:
    #        return list(range(1+node.childCount()))

    #    #Row 0 for the device is always the manual_icon_node
    #    elif node_type == strings.DEVICE_NODE and new_child_type == strings.DEVICE_ICON_NODE:
    #        return [0]
    #    elif node_type == strings.DEVICE_NODE and new_child_type in [strings.D_IN_NODE, strings.D_OUT_NODE, strings.A_IN_NODE, strings.A_OUT_NODE, strings.BOOL_VAR_NODE, strings.FLOAT_VAR_NODE]:
    #        return list(range(1,1+node.childCount()))
    #    return []

    def insertChild(self, parent_index, child_type, insert_row = None):
        parent_node  = parent_index.internalPointer()
        #allowed_rows = self.allowedInsertRows(parent_index, child_type)

        if insert_row is None:
            insert_row = parent_index.internalPointer().childCount()

        #if not allowed_rows:
        #    msg = "Child of type " + child_type + " cannot be inserted into " + parent_node.typeInfo()
        #    MessageBox(msg)
        #    return False
        #if preferred_row is None:
        #    insert_row = allowed_rows[-1]
        #elif preferred_row in allowed_rows:
        #    insert_row = preferred_row
        #else:
        #    MessageBox("Attempting to insert child in tool model at bad row", "row: ", preferred_row, "allowed rows: ", allowed_rows)
        #    return False


        if insert_row is not False:
            self.beginInsertRows(parent_index, insert_row, insert_row)

            if    child_type == typ.TOOL_NODE        : parent_node.insertChild(insert_row, ToolNode())
            elif  child_type == typ.SYSTEM_NODE      : parent_node.insertChild(insert_row, SystemNode())
            elif  child_type == typ.DEVICE_NODE      : parent_node.insertChild(insert_row, DeviceNode())
            elif  child_type == typ.DEVICE_ICON_NODE : parent_node.insertChild(insert_row, DeviceIconNode())
            elif  child_type == typ.D_IN_NODE        : parent_node.insertChild(insert_row, DigitalInputNode())
            elif  child_type == typ.D_OUT_NODE       : parent_node.insertChild(insert_row, DigitalOutputNode())
            elif  child_type == typ.A_IN_NODE        : parent_node.insertChild(insert_row, AnalogInputNode())
            elif  child_type == typ.A_OUT_NODE       : parent_node.insertChild(insert_row, AnalogOutputNode())
            elif  child_type == typ.BOOL_VAR_NODE    : parent_node.insertChild(insert_row, BoolVarNode())
            elif  child_type == typ.FLOAT_VAR_NODE   : parent_node.insertChild(insert_row, FloatVarNode())

            else: MessageBox('Attempting to insert unknown node of type', child_type)

            self.endInsertRows()

            new_child_index = self.index(insert_row, 0, parent_index)
            return new_child_index


    def removeRows(self, row, count, parent_index):
        parent_node = parent_index.internalPointer()

        if not isinstance(row, int):
            raise TypeError("Tool Model removeRows 'row' must be of type 'int")

        if not isinstance(count, int):
            raise TypeError("Tool Model removeRows 'count' must be of type 'int'")

        if row < 0:
            raise ValueError("Tool Model removeRows 'row' must be >= 0")

        if count <= 0:
            raise ValueError("Tool Model removeRows 'count' must be > 0")

        self.beginRemoveRows(parent_index, row, row+count-1)

        for i in list(range(count)):
            parent_node.removeChild(row)

        self.endRemoveRows()


    def data(self, index, role):
        #Views access data through this interface, index is a QModelIndex
        #Returns a QVariant, strings are cast to QString which is a QVariant"""

        if not index.isValid():
            return None

        node = index.internalPointer()

        if role == QtCore.Qt.DisplayRole or role == QtCore.Qt.EditRole:
            return node.data(index.column())

        elif role == QtCore.Qt.DecorationRole:
            if index.column() == 0:
                return None


    def setData(self, index, value, role=QtCore.Qt.EditRole):
        if type(value) == type(QtCore.QVariant()):
            value = value.toPyObject()

        if index.isValid() and role == QtCore.Qt.EditRole and value is not None: #FIXME this might break something
        #if index.isValid() and role == QtCore.Qt.EditRole:
            node = index.internalPointer()
            node.setData(index.column(), value)
            self.dataChanged.emit(index, index)

            if index.column() == col.HAL_VALUE and node.typeInfo() in typ.HAL_NODES:
                self.dataChanged.emit(index.siblingAtColumn(col.VALUE), index.siblingAtColumn(col.VALUE))

            if index.column() == col.HAL_PIN and node.typeInfo() in typ.HAL_NODES:
                self.dataChanged.emit(index.siblingAtColumn(col.HAL_PIN_TYPE), index.siblingAtColumn(col.HAL_PIN_TYPE))


            if index.column() == col.POS and node.typeInfo() == typ.DEVICE_ICON_NODE:
                self.dataChanged.emit(index.siblingAtColumn(col.X), index.siblingAtColumn(col.X))
                self.dataChanged.emit(index.siblingAtColumn(col.Y), index.siblingAtColumn(col.Y))

            return True

        return False


    def headerData(self, section, orientation, role):
        if role == QtCore.Qt.DisplayRole:
            if   section == 0: return "Name"
            elif section == 1: return "Type"

    def flags(self, index):
        node = index.internalPointer()
        flag = QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable

        if (index.column() == 1) and node.typeInfo() == typ.DEVICE_NODE:
            return flag | QtCore.Qt.ItemIsEditable

        return flag


    def parent(self, index):
        if index.internalPointer() == self._root_node:
            return QtCore.QModelIndex()


        elif index is not None and index.isValid():
            node = index.internalPointer()
            parent_node = node.parent()
            return self.createIndex(parent_node.row(), 0, parent_node)

    def index(self, row, column, parent_index):
        if parent_index is not None and parent_index.isValid():
            parent_node = parent_index.internalPointer()
            child_item = parent_node.child(row)
            return self.createIndex(row, column, child_item)

        else:
            return self.createIndex(row, column, self._root_node)


    def indexesOfType(self, index_type, parent_index=None):
        try:
            parent_node = parent_index.internalPointer() if parent_index.isValid() else self._root_node
        except:
            parent_index = self.index(0, 0, QtCore.QModelIndex())
            parent_node = self._root_node

        indexes = []

        for row in range(self.rowCount(parent_index)):
            index = parent_index.child(row, 0)

            if index.internalPointer().typeInfo() == index_type:
                indexes.append(index)

            indexes += self.indexesOfType(index_type, index)

        return indexes



    #def systemIcons(self, index):
    #    node = index.internalPointer()
    #    icon_children = []

    #    if node.typeInfo() == strings.SYSTEM_NODE:
    #        for device_child in node.children():
    #            for child in device_child.children():
    #                if child.typeInfo() == strings.DEVICE_ICON_NODE:
    #                    if index.isValid():
    #                        icon_children.append(self.createIndex(child.row(), 0, child))

    #    return icon_children

    #def deviceIconIndex(self, index):
    #    node = index.internalPointer()
    #    if node.typeInfo() == strings.DEVICE_NODE:
    #            for child in node.children():
    #                if child.typeInfo() == strings.DEVICE_ICON_NODE:
    #                    return self.createIndex(row?????,)



        #if role == SceneGraphModel.sortRole:
        #    return node.typeInfo()

        #if role == SceneGraphModel.filterRole:
        #    return node.typeInfo()






## Taken from: http://gaganpreet.in/blog/2013/07/04/qtreeview-and-custom-filter-models/
class LeafFilterProxyModel(QtCore.QSortFilterProxyModel):
    ''' Class to override the following behaviour:
            If a parent item doesn't match the filter,
            none of its children will be shown.

        This Model matches items which are descendants
        or ascendants of matching items.
    '''


    def filterAcceptsRow(self, row_num, source_parent):
        ''' Overriding the parent function '''

        # Check if the current row matches
        if self.filter_accepts_row_itself(row_num, source_parent):
            return True

        # Traverse up all the way to root and check if any of them match
        if self.filter_accepts_any_parent(source_parent):
            return True

        # Finally, check if any of the children match
        return self.has_accepted_children(row_num, source_parent)

    def filter_accepts_row_itself(self, row_num, parent):
        return super(LeafFilterProxyModel, self).filterAcceptsRow(row_num, parent)

    def filter_accepts_any_parent(self, parent):
        ''' Traverse to the root node and check if any of the
            ancestors match the filter
        '''
        while parent.isValid():
            if self.filter_accepts_row_itself(parent.row(), parent.parent()):
                return True
            parent = parent.parent()
        return False

    def has_accepted_children(self, row_num, parent):
        ''' Starting from the current node as root, traverse all
            the descendants and test if any of the children match
        '''
        model = self.sourceModel()
        source_index = model.index(row_num, 0, parent)

        children_count =  model.rowCount(source_index)
        for i in range(children_count):
            if self.filterAcceptsRow(i, source_index):
                return True

        return False

    def removeRows(self, row, count, index):
        self.sourceModel().removeRows(row, count, index)

    def insertChild(self, parent_index, node_type, preferred_row = None):
        return self.sourceModel().insertChild(parent_index, node_type, preferred_row)

    def possibleChildren(self, index):
        return self.sourceModel().possibleChildren(index)
