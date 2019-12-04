#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtGui, QtWidgets
from linuxnano.message_box import MessageBox

import copy
import itertools


class DigitalStateTableModel(QtCore.QAbstractTableModel):
    '''This table is used to store information about a Digital IO nodes states, including:
            - value
            - if that output button should be used in the manual view
            (state 0 cannot be a No)


         state  bit_0  Name  Used?
            0:     0    ""    Yes
            1:     1    ""    Yes

         state  bit_1  bit_0  Name  used?
            0:     0      0    ""     Yes
            1:     0      1    ""     Yes
            2:     1      0    ""      No
            3:     1      1    ""     Yes

    '''

    def __init__(self, parent = None, allow_is_used=False):
        super().__init__(parent)
        self._allow_is_used = allow_is_used
        self._number_of_bits = 1
        
        if self._allow_is_used:
            self._headers = ['bit_0', 'GUI Name', 'Is Used']
            self._data  = [ [False  ,  "Off", True],
                            [True   ,  "On", True]]

        else:
            self._headers = ['bit_0', 'GUI Name']
            self._data  = [ [False  ,  "Off"],
                            [True   ,  "On"]]


    def numberOfBits(self):
        return self._number_of_bits
    
    def nameColumn(self):
        return self._number_of_bits

    def isUsedColumn(self):
        if self._allow_is_used:
            return self._number_of_bits + 1
        else:
            return False

    def rowCount(self, parent=None):
        return len(self._data)
    
    def columnCount(self, parent=None):
        return len(self._data[0])

    def headerData(self, section, orientation, role):
        if role == QtCore.Qt.DisplayRole:
            if orientation == QtCore.Qt.Horizontal:
                return self._headers[section]
            else:
                return str(section).format("%1")

    def dataArray(self):
        data = []

        if self._allow_is_used:
            data.append(['state', 'gui_name', 'is_used'])
            for i, row in enumerate(self._data):
                name = self._data[i][self.nameColumn()]
                is_used = self._data[i][self.isUsedColumn()]

                data.append([i, name, is_used])
        
        else:
            data.append(['state', 'gui_name'])
            for i, row in enumerate(self._data):
                name = self._data[i][self.nameColumn()]
                
                data.append([i, name])
            
        return data
            
    

    def setDataArray(self, data):
        '''
            in format [ ['state', 'GUI Name', 'Is Used'],
                        [     0 , "Name_a"  , True],
                        [     1 , "Name_b"  , True],
                        [     2 , "Name_c"  , True],
                        [     3 , "Name_d"  , True]]
        '''
        #Data validation first
        try:
            if self._allow_is_used and data[0] == ['state', 'gui_name', 'is_used']:
                data_main = data[1:]
            
            elif not self._allow_is_used and data[0] == ['state', 'gui_name']:
                data_main = data[1:]
            else:
                if self._allow_is_used:
                    MessageBox('Invalid digital state table data.', "Row 0 should be ['state', 'gui_name', 'is_used'] but is", data[0])
                else:
                    MessageBox('Invalid digital state table data.', "Row 0 should be ['state', 'gui_name'] but is", data[0])
                return False

            num_rows = len(data_main)
            
            #Array must be length 2,4,8 or 16
            if not num_rows in [2,4,8,16]:
                MessageBox('Invalid number of rows in state data, must be 2,4,8 or 16', 'Digital State Table: ', data)
                return False 
           

            for i, row in enumerate(data_main):
                if not len(row) in [2,3]:
                    MessageBox('Must have 2 or 3 columns state_index, GUI Name, Is_Used (optional)', row)
                    return False

                if row[0] != i:
                    MessageBox('Index column must be 0,1 or 0,1,2,3 or 0,1,2...7, or 0,1,2...15', 'Digital State Table: ', data)
                    return False

                if not isinstance(row[1], str):
                    MessageBox('State data GUI Name must be of type string', row[1])
                    return False

                if len(row) == 3:
                    if not isinstance(row[2],bool):
                        MessageBox('State data is_used must be of type bool', row[2], 'is of type: ', type(row[2]))
                        return False




        except Exception as e:
            MesssageBox('State table data array testing failed', 'Digital State Table:\n', data, '\n', e)
            return False


        self.beginResetModel()
        
        if   num_rows == 2 : num_bits = 1
        elif num_rows == 4 : num_bits = 2
        elif num_rows == 8 : num_bits = 3
        elif num_rows == 16: num_bits = 4
            
        self.setNumberOfBits(num_bits)
          
            
        #Set the data now
        for i, row in enumerate(data_main):
            self._data[i][self.nameColumn()] = row[1]
            
            if self._allow_is_used and len(row) == 3:
                self._data[i][self.isUsedColumn()] = row[2]

        self.endResetModel()
        return True


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

        

    def setNumberOfBits(self, num_bits):

        if not num_bits in [1,2,3,4]:
            MessageBox('Invalid number of bits, must be 1,2,3 or 4',num_bits)
            return False

        if num_bits == self.numberOfBits():
            return True

        current_name_col = [inner[self.nameColumn()] for inner in self._data] 
        
        if self._allow_is_used:
            current_is_used_col = [inner[self.isUsedColumn()] for inner in self._data] 
       

        self.beginResetModel()

        if   num_bits == 1:
            self._headers = ['bit_0']
        elif num_bits == 2:
            self._headers = ['bit_1', 'bit_0']
        elif num_bits == 3:
            self._headers = ['bit_2', 'bit_1', 'bit_0']
        elif num_bits == 4:
            self._headers = ['bit_3', 'bit_2', 'bit_1', 'bit_0']
        
       
        self._headers.append('GUI Name')
        if self._allow_is_used:
            self._headers.append('Is Used')


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
        self._number_of_bits = num_bits
        self.endResetModel()
        return True


    #TODO change the name of this method?
    def states(self):
        name_col = self.nameColumn()
        return [row[name_col] for row in self._data]





