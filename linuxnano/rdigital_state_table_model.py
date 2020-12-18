#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtGui, QtWidgets

import copy
import itertools


class DigitalStateTableModel(QtCore.QAbstractTableModel):
    '''This table is used to store information about a Digital IO nodes states, including:
            - value
            - if that output button should be used in the manual view
            (state 0 cannot be a No)

         state  bit_0  Name  Is Used?
            0:     0    ""    Yes
            1:     1    ""    Yes

         state  bit_1  bit_0  Name  Is Used?
            0:     0      0    ""     Yes
            1:     0      1    ""     Yes
            2:     1      0    ""      No
            3:     1      1    ""     Yes

    '''
    def __init__(self, parent = None, allow_is_used=False):
        super().__init__(parent)
        self._allow_is_used = allow_is_used
        self._allowed_hal_pins = []
        self._hal_pins = ['None']

        if self._allow_is_used:
            self._data  = [ [False, "Off", True],
                            [True , "On" , True]]
        else:
            self._data  = [ [False, "Off"],
                            [True , "On" ]]

    def numberOfBits(self):
        return len(self._hal_pins)

    def nameColumn(self):
        return self.numberOfBits()

    def isUsedColumn(self):
        if self._allow_is_used:
            return self.numberOfBits() + 1
        else:
            return False

    def rowCount(self, parent=None):
        return len(self._data)

    def columnCount(self, parent=None):
        return len(self._data[0])

    def headerData(self, section, orientation, role):
        if role == QtCore.Qt.DisplayRole:
            if orientation == QtCore.Qt.Horizontal:
                if   section == self.nameColumn()  : return 'GUI Name'
                elif self._allow_is_used and section == self.isUsedColumn(): return 'Is Used'
                elif section < len(self._hal_pins):
                    head = self._hal_pins[::-1] #flip the list since bit 0 is on the right
                    return head[section]

            else:
                return str(section).format("%1")


    def allowedHalPins(self):
        return self._allowed_hal_pins

    def setAllowedHalPins(self, value):
        if not all(isinstance(s, str) for s in value):
            raise Exception('setAllowedHalPins must recieve a list of strings')

        self._allowed_hal_pins = value  #TODO make a copy?


    def data(self, index, role):
        row = index.row()
        col = index.column()

        if role == QtCore.Qt.EditRole or role == QtCore.Qt.DisplayRole:
            return self._data[row][col]

        if role == QtCore.Qt.ToolTipRole:
            if   col == self.nameColumn():
                return "This is the string used to refer to this in the manual page"
            elif col == self.isUsedColumn():
                return "Determines if a button for this state shows up on the manual page"

        if role == QtCore.Qt.BackgroundColorRole:
            if self._data[row][col] == True and col < self.numberOfBits():
                return QtGui.QColor(123, 156, 209)


    def setData(self, index, value, role = QtCore.Qt.EditRole):
        if role == QtCore.Qt.EditRole:
            row = index.row()
            col = index.column()

            #First isUsed must always be true
            if col == self.isUsedColumn() and row == 0:
                self._data[row][col] = True
                return False

            # Only the name and isUsed column can be edited
            if col == self.nameColumn() or col == self.isUsedColumn():
                if   col == self.nameColumn()  : value = str(value)
                elif col == self.isUsedColumn(): value = bool(value)

                self._data[row][col] = value
                self.dataChanged.emit(index, index)

                return True

        return False


    def flags(self, index):
        #First row must always be enabled since it boots off
        if   index.column() == self.isUsedColumn() and index.row() == 0:
            return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable

        elif self._allow_is_used and index.column() == self.isUsedColumn():
            return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable

        elif index.column() == self.nameColumn():
            return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable

        else:
            return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable


    def bitAtColumn(self, col):
        if col < 0 or col >= self.numberOfBits():
            raise Exception('Invalid column sent to bitAtColumn in digital state table model.')

        a = list(range(self.numberOfBits()))
        a.reverse()
        return a[col]


    def setHalPin(self, bit, value):
        self.beginResetModel()
        self._hal_pins[bit] = str(value)
        self.endResetModel()
        return True

    def halPins(self):
        return self._hal_pins

    def setHalPins(self, value):
        self.setNumberOfBits(len(value))
        self._hal_pins = value

    def setNumberOfBits(self, num_bits):
        if not num_bits in [1,2,3,4]:
            raise ValueError('Invalid number of bits, must be 1,2,3 or 4')

        if num_bits == self.numberOfBits():
            return True

        current_name_col = [inner[self.nameColumn()] for inner in self._data]
        if self._allow_is_used:
            current_is_used_col = [inner[self.isUsedColumn()] for inner in self._data]

        #_hal_pins in format: ['bit_3', 'bit_2', 'bit_1', 'bit_0']
        self.beginResetModel()

        while len(self._hal_pins) > num_bits:
            self._hal_pins.pop(-1)

        while len(self._hal_pins) < num_bits:
            self._hal_pins.append('None')

        #Build the truth table of False, True
        truth_tbl = [list(item) for item in itertools.product([False,True], repeat=num_bits)]

        #Add the name and is used column from the old data if it exits
        for i, row in enumerate(truth_tbl):
            if i < len(current_name_col):
                row.append(current_name_col[i])
                if self._allow_is_used:
                    row.append(current_is_used_col[i])
            else:
                row.append('GUI Name')
                if self._allow_is_used:
                    row.append(True)

        self._data = truth_tbl
        self.endResetModel()
        return True



    def states(self):
        return [row[self.nameColumn()] for row in self._data]

    def setStates(self, data):

        #Check the number of rows corresponds to the number of bits
        if len(data) != 2<<(self.numberOfBits()-1):
            raise ValueError('Invalid number of rows in state data, rows must correlate to number of bits')

        if not all(isinstance(x, str) for x in data):
            raise TypeError('State data GUI Name must be of type string')

        #Set the data now
        self.beginResetModel()
        for i, item in enumerate(data):
            self._data[i][self.nameColumn()] = item
        self.endResetModel()

        return True

    def isUsed(self):
        return [row[self.isUsedColumn()] for row in self._data]

    def setIsUsed(self, data):
        if not self._allow_is_used:
            return False

        #Check the number of rows corresponds to the number of bits
        if len(data) != 2<<(self.numberOfBits()-1):
            raise ValueError('Invalid number of rows in isUsed data, rows must correlate to number of bits')

        if not all(isinstance(x, bool) for x in data):
            raise TypeError('State data is_used must be of type bool')


        self.beginResetModel()
        for i, item in enumerate(data):
            self._data[i][self.isUsedColumn()] = item
        self.endResetModel()

        self._data[0][self.isUsedColumn()] = True

        return True
