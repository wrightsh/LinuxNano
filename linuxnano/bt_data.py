from PyQt5 import QtCore, QtGui, QtXml, QtWidgets
import xml.etree.ElementTree as ET

from linuxnano.strings import strings
from linuxnano.message_box import MessageBox
import json

class Node:
    def __init__(self, parent=None):
        super().__init__()

        self._parent = parent
        self._children = []

        self._x_pos = 80
        self._y_pos = 0

        if parent is not None:
            parent.addChild(self)

    def loadAttrs(self, data):
        try:
            #Get all the attributes of the node
            attrs = iter(self.attrs().items())
            for key, value in attrs:
                if key in data:
                    setattr(self, key, data[key])

        except Exception as e:
            MessageBox("Error setting attribute", e, key, value)

    def convertToDict(self, o):
        data = {"type_info": o.typeInfo(),
                "children" : o.children()}

        attrs = iter(o.attrs().items())
        for key, value in attrs:
            data[key] = value

        return data

    def asJSON(self):
        data = json.dumps(self, default=self.convertToDict,  sort_keys=True, indent=4)
        return data

    def attrs(self):
        kv = {}

        my_classes = self.__class__.__mro__
        for cls in my_classes:
            for k, v in sorted(iter(cls.__dict__.items())):
                if isinstance(v, property):
                    kv[k] = v.fget(self)
        return kv

    def typeInfo(self):
        return 'root'

    def isLeaf(self):
        return False

    def parent(self):
        return self._parent

    def child(self, row):
        return self._children[row]

    def addChild(self, child):
        self._children.append(child)
        child._parent = self

    def insertChild(self, position, child):
        if position < 0 or position > len(self._children):
            return False

        self._children.insert(position, child)
        child._parent = self
        return True

    def children(self):
        return self._children

    def childCount(self):
        return len(self._children)

    def removeChild(self, position):
        if position < 0 or position >= len(self._children):
            return False

        child = self._children.pop(position)
        child._parent = None

        return True

    def row(self):
        if self._parent is not None:
            return self._parent._children.index(self)

    def data(self, column):
        if   column is 0: return self.typeInfo()
        elif column is 1: return self.x_pos
        elif column is 2: return self.y_pos

    def setData(self, column, value):
        if   column is 0: pass
        elif column is 1: self.x_pos = value
        elif column is 2: self.y_pos = value

    def width(self):
        return 120

    def height(self):
        return 60

    #Properties get saved to JSON
    def x_pos():
        def fget(self): return self._x_pos
        def fset(self, value): self._x_pos = int(value)
        return locals()
    x_pos = property(**x_pos())

    def y_pos():
        def fget(self): return self._y_pos
        def fset(self, value): self._y_pos = int(value)
        return locals()
    y_pos = property(**y_pos())


class SequenceNode(Node):
    def __init__(self, parent=None):
        super().__init__(parent)

    def typeInfo(self):
        return strings.SEQUENCE_NODE

    def isLeaf(self):
        return False



class SelectorNode(Node):
    def __init__(self, parent=None):
        super().__init__(parent)

    def typeInfo(self):
        return strings.SELECTOR_NODE

    def isLeaf(self):
        return False


class WhileNode(Node):
    def __init__(self, parent=None):
        super().__init__(parent)

    def typeInfo(self):
        return strings.WHILE_NODE

    def isLeaf(self):
        return False


class SetOutputNode(Node):
    def __init__(self, parent=None):
        super().__init__(parent)

    def typeInfo(self):
        return strings.SET_OUTPUT_NODE

    def isLeaf(self):
        return True


class WaitTimeNode(Node):
    def __init__(self, parent=None):
        super().__init__(parent)

        self._wait_time = 0

    def typeInfo(self):
        return strings.WAIT_TIME_NODE

    def isLeaf(self):
        return True

    def data(self, column):
        r = super().data(column)
        if   column is 10: r = self.wait_time
        return r

    def setData(self, column, value):
        super().setData(column, value)
        if   column is 10: self.wait_time = value


    #Properties get saved to JSON
    def wait_time():
        def fget(self): return self._wait_time
        def fset(self, value): self._wait_time = float(value)
        return locals()
    wait_time = property(**wait_time())
