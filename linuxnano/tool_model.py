from PyQt5 import QtCore, QtGui



from linuxnano.strings import strings
from linuxnano.data import Node, ToolNode, SystemNode, DeviceNode, DeviceIconNode, DigitalInputNode, DigitalOutputNode, AnalogInputNode, AnalogOutputNode
from linuxnano.message_box import MessageBox


class ToolModel(QtCore.QAbstractItemModel):
    '''The tool model represents an entire tool in a tree structure.'''

    def __init__(self, parent=None):
        super().__init__(parent)
        self._root_node = Node()

    def asXml(self):
        return self._root_node.asXml()

    #TODO: Do we clear the current tree if there's one?
    def loadTool(self, tool_tree):
        try:
            root = tool_tree.getroot()
            root_index = self.createIndex(0,0,self._root_node)

            for tool_item in root.findall(strings.TOOL_NODE):
                tool_index = self.insertChild(root_index, strings.TOOL_NODE)
                tool_index.internalPointer().loadAttribFromXML(tool_item)


                for system_item in tool_item.findall(strings.SYSTEM_NODE):
                    system_index = self.insertChild(tool_index, strings.SYSTEM_NODE)

                    for device_item in system_item.findall(strings.DEVICE_NODE):
                        device_index = self.insertChild(system_index, strings.DEVICE_NODE)


                        device_icon_xml = device_item.find(strings.DEVICE_ICON_NODE)
                        device_icon_index = self.insertChild(device_index, strings.DEVICE_ICON_NODE)


                        #TODO add code to force a manual icon if it's not there

                        for xml_item in device_item.findall(strings.D_IN_NODE):
                            d_in_index = self.insertChild(device_index, strings.D_IN_NODE)
                            d_in_index.internalPointer().loadAttribFromXML(xml_item)

                        for xml_item in device_item.findall(strings.D_OUT_NODE):
                            d_out_index = self.insertChild(device_index, strings.D_OUT_NODE)
                            d_out_index.internalPointer().loadAttribFromXML(xml_item)

                        for xml_item in device_item.findall(strings.A_IN_NODE):
                            a_in_index = self.insertChild(device_index, strings.A_IN_NODE)
                            a_in_index.internalPointer().loadAttribFromXML(xml_item)

                        for xml_item in device_item.findall(strings.A_OUT_NODE):
                            a_out_index = self.insertChild(device_index, strings.A_OUT_NODE)
                            a_out_index.internalPointer().loadAttribFromXML(xml_item)

                        #Must load after analog nodes since we have an analog node name
                        if device_icon_xml is not None:
                           device_icon_index.internalPointer().loadAttribFromXML(device_icon_xml)

                        device_index.internalPointer().loadAttribFromXML(device_item)
                    system_index.internalPointer().loadAttribFromXML(system_item)

            return True

        except Exception as e:
            MessageBox("Failed to load tool from element tree", e)
            return False


    def rowCount(self, parent):
        '''Returns the number of children'''
        if not parent.isValid():
            parentNode = self._root_node
        else:
            parentNode = parent.internalPointer()

        return parentNode.childCount()

    def columnCount(self, parent):
        '''Number of columns the QTreeView displays '''
        return 2

    def possibleChildren(self, index):
        node_type = index.internalPointer().typeInfo()

        if   node_type == strings.TOOL_NODE:
            return [strings.SYSTEM_NODE]

        elif node_type == strings.SYSTEM_NODE:
            return [strings.DEVICE_NODE]

        elif node_type == strings.DEVICE_NODE:
            return [strings.DEVICE_ICON_NODE,
                    strings.D_IN_NODE,
                    strings.D_OUT_NODE,
                    strings.A_IN_NODE,
                    strings.A_OUT_NODE]

        elif node_type == strings.DEVICE_ICON_NODE:
            return []

        elif node_type in [strings.DIGITAL_INPUT_NODE, strings.DIGITAL_OUTPUT_NODE, strings.ANALOG_INPUT_NODE, strings.ANALOG_OUTPUT_NODE]:
            return []


    def allowedInsertRows(self, node_index, new_child_type):
        node = node_index.internalPointer()
        node_type = node.typeInfo()

        if   node_type == 'root' and new_child_type == strings.TOOL_NODE:
            return [0]

        elif node_type == strings.TOOL_NODE and new_child_type == strings.SYSTEM_NODE:
            return list(range(1+node.childCount()))

        elif node_type == strings.SYSTEM_NODE and new_child_type == strings.DEVICE_NODE:
            return list(range(1+node.childCount()))

        #Row 0 for the device is always the manual_icon_node
        elif node_type == strings.DEVICE_NODE and new_child_type == strings.DEVICE_ICON_NODE:
            return [0]

        elif node_type == strings.DEVICE_NODE and new_child_type in [strings.D_IN_NODE, strings.D_OUT_NODE, strings.A_IN_NODE, strings.A_OUT_NODE]:
            return list(range(1,1+node.childCount()))

        return []



    def insertChild(self, parent_index, child_type, preferred_row = None):
        parent_node  = parent_index.internalPointer()
        allowed_rows = self.allowedInsertRows(parent_index, child_type)

        if not allowed_rows:
            msg = "Child of type " + child_type + " cannot be inserted into " + parent_node.typeInfo()
            MessageBox(msg)
            return False


        if preferred_row is None:
            insert_row = allowed_rows[-1]

        elif preferred_row in allowed_rows:
            insert_row = preferred_row
        else:
            MessageBox("Attempting to insert child in tool model at bad row", "row: ", preferred_row, "allowed rows: ", allowed_rows)
            return False


        if insert_row is not False:
            self.beginInsertRows(parent_index, insert_row, insert_row)

            if    child_type == strings.TOOL_NODE        : parent_node.insertChild(insert_row, ToolNode())
            elif  child_type == strings.SYSTEM_NODE      : parent_node.insertChild(insert_row, SystemNode())
            elif  child_type == strings.DEVICE_NODE      : parent_node.insertChild(insert_row, DeviceNode())
            elif  child_type == strings.DEVICE_ICON_NODE : parent_node.insertChild(insert_row, DeviceIconNode())
            elif  child_type == strings.D_IN_NODE        : parent_node.insertChild(insert_row, DigitalInputNode())
            elif  child_type == strings.D_OUT_NODE       : parent_node.insertChild(insert_row, DigitalOutputNode())
            elif  child_type == strings.A_IN_NODE        : parent_node.insertChild(insert_row, AnalogInputNode())
            elif  child_type == strings.A_OUT_NODE       : parent_node.insertChild(insert_row, AnalogOutputNode())

            else: MessageBox('Attempting to insert unknown node of type', child_type)

            self.endInsertRows()

            new_child_index = self.index(insert_row, 0, parent_index)
            return new_child_index





    def removeRows(self, row, count, parent_index):
        parent_node = parent_index.internalPointer()

        if not isinstance(  row, int):
            MessageBox("Tool Model removeRows 'row' must be of type 'int', is of type: ", type(row))
            return False

        if not isinstance(count, int):
            MessageBox("Tool Model removeRows 'count' must be of type 'int', is of type: ", type(count))
            return False

        if   row <  0:
            MessageBox("Tool Model removeRows 'row' must be >= 0, is: ", row)
            return False

        if count <= 0:
            MessageBox("Tool Model removeRows 'count' must be > 0, is: ", count)
            return False


        self.beginRemoveRows(parent_index, row, row+count-1)

        for i in list(range(count)):
            parent_node.removeChild(row)

        self.endRemoveRows()



    def data(self, index, role):
        """INPUTS: QModelIndex, int"""
        """OUTPUT: QVariant, strings are cast to QString which is a QVariant"""
        '''Views access data through this interface '''

        if not index.isValid():
            return None

        node = index.internalPointer()

        if role == QtCore.Qt.DisplayRole or role == QtCore.Qt.EditRole:
            return node.data(index.column())


        #TODO Fix this! and and testing
        elif role == QtCore.Qt.DecorationRole:
            if index.column() == 0:
                resource = node.iconResource()
                return QtGui.QIcon(QtGui.QPixmap(resource))


    def setData(self, index, value, role=QtCore.Qt.EditRole):
        """INPUTS: QModelIndex, QVariant, int (flag)"""
        print('setData')
        if type(value) == type(QtCore.QVariant()):
            value = value.toPyObject()

        if index.isValid() and role == QtCore.Qt.EditRole:
            node = index.internalPointer()
            node.setData(index.column(), value)
            self.dataChanged.emit(index, index)
            return True

        return False


    def headerData(self, section, orientation, role):
        if role == QtCore.Qt.DisplayRole:
            if section == 0:
                return "Name"
            elif section == 1:
                return "Type"

    def flags(self, index):
        node = index.internalPointer()
        flag = QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable

        if (index.column() == 0) and node.typeInfo() == strings.DEVICE_NODE:
            return flag | QtCore.Qt.ItemIsEditable

        return flag


    def parent(self, index):
        node = index.internalPointer()
        parent_node = node.parent()

        if parent_node == self._root_node:
            return QtCore.QModelIndex()

        if index.isValid():
            return self.createIndex(parent_node.row(), 0, parent_node)



    def index(self, row, column, parent_index):
        if parent_index.isValid():
            parent_node = parent_index.internalPointer()
        else:
            parent_node = self._root_node

        child_item = parent_node.child(row)

        if child_item:
            return self.createIndex(row, column, child_item)
        else:
            return QtCore.QModelIndex()


    def systemIcons(self, index):
        node = index.internalPointer()
        icon_children = []

        if node.typeInfo() == strings.SYSTEM_NODE:
            for device_child in node.children():
                for child in device_child.children():
                    if child.typeInfo() == strings.DEVICE_ICON_NODE:
                        if index.isValid():
                            icon_children.append(self.createIndex(child.row(), 0, child))

        return icon_children


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
        self.sourceModel().removeRows(row,count, index)


    def iconChildrenForSystem(self, index):
        return self.sourceModel().iconChildrenForSystem(index)

    def insertChild(self, parent_index, node_type, preferred_row = None):
        return self.sourceModel().insertChild(parent_index, node_type, preferred_row)

    def possibleChildren(self, index):
        return self.sourceModel().possibleChildren(index)
