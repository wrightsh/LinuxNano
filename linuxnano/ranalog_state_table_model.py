#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtGui, QtWidgets
from linuxnano.message_box import MessageBox
import copy


class AnalogStateTableModel(QtCore.QAbstractTableModel):
    '''This table is used to store information about a Analog IO nodes states, including:
            - value
            - 1,2,3 or 4 states

         state     X >= This      Name      
            0:     None         "default"  

         state     X >= This      Name      
            0:     None         "Hi Vac"  
            1:     3.72 mTorr   "Low Vac"  

         state  >X           Name    
            0:  None       "Hi Vac"  
            1:  1 Torr     "Low Vac" 
            2:  750 Torr   "Atmo"    
            3:  950 Torr   "Atmo"    

    '''

    def __init__(self, parent = None):
        super().__init__(parent)
       
        self._number_of_states = 1
        self._headers = ['State', 'Greater Than', 'GUI Name']
        self._data  = [[0,  None, 'name_of_state']]



    def greaterThanColumn(self):
        return 1

    def nameColumn(self):
        return 2

    def rowCount(self, parent=None):
        return len(self._data)
    
    def columnCount(self, parent=None):
        return len(self._data[0])

    def headerData(self, section, orientation, role):
        if role == QtCore.Qt.DisplayRole:
            if orientation == QtCore.Qt.Horizontal:
                return self._headers[section]
            else:
                return 

    def dataArray(self):
        data = []
        data.append(['state', 'greater_than', 'gui_name'])
         
        data_main = copy.deepcopy(self._data)
        data += data_main

        return data
            
    def setDataArray(self, data):
        '''
            in format [ ['state', 'greater_than', 'gui_name' ],
                        [     0 ,           None,   'name_a'],
                        [     1 ,           1.11,   'name_b'],
                        [     2 ,           2.34,   'name_c'],
                        [     3 ,           9.99,   'name_d']]
        '''
        data_main = []
        
        #Data validation first
        try:
            if data[0] == ['state', 'greater_than','gui_name']:
                data_main = data[1:]
            
            else:
                MessageBox("Invalid analog state table data, first row must be ['state', 'greater_than', 'gui_name'].", "Row 0:", data[0])
                return False

            num_rows = len(data_main)
            
            #Array must be length 2,4,8 or 16
            if num_rows <= 0:
                MessageBox('Invalid number of rows in state data, must have at least 1', 'Analog State Table:', data)
                return False 
            
            if num_rows > 4:
                MessageBox('Invalid number of rows in state data, must have 1-4', 'Analog State Table:', data)
                return False 
           


            for i, row in enumerate(data_main):
                if not len(row) == 3:
                    MessageBox('Must have 3 columns state_index, grater_than, gui_name', row)
                    return False

                if not row[0] == i:
                    MessageBox('Index column must be 0 or 0,1 or 0,1,2 or 0,1,2,3', row[0])
                    return False
              

                #greater_than column checks
                if i == 0 and row[self.greaterThanColumn()] != None:
                    MessageBox('State data greater_than row 0 must be None', 'Analog State Table:', data)
                    return False

                if i == 1:
                    prev_greater_than = row[self.greaterThanColumn()]
              
                if i > 1 and prev_greater_than >= row[self.greaterThanColumn()]:
                    MessageBox('State data greater_than must be sequential:', row[self.greaterThanColumn()], 'is not larger then:', prev_greater_than)
                    return False


                if i > 0 and not isinstance(row[self.greaterThanColumn()], float):
                    MessageBox('State data greater_than must be of type float', row[self.greaterThanColumn()], 'is of type:', type(row[self.greaterThanColumn()]))
                    return False


                #name column checks
                if not isinstance(row[self.nameColumn()], str):
                    MessageBox('State data GUI Name must be of type string', row[self.nameColumn()], 'is of type: ', type(row[self.nameColumn()]))
                    return False



        except Exception as e:
            MesssageBox('State table data array testing failed', 'Analog State Table: ', data, '\n', e)
            return False


        self.setNumberOfStates(num_rows)
        
        #Set the data now
        self.beginResetModel()
        for i, row in enumerate(data_main):
            data_main[i][0] = int(row[0])
            if i > 0:
                data_main[i][1] = float(row[1])
            data_main[i][2] = str(row[2])
      
        self._data = copy.deepcopy(data_main)

        self.endResetModel()
        return True


    def data(self, index, role):
        row = index.row()
        col = index.column()

        if role == QtCore.Qt.EditRole or role == QtCore.Qt.DisplayRole:
            return self._data[row][col]
        
        if role == QtCore.Qt.ToolTipRole:
            if   col == self.greaterThanColumn():
                return "If the analog value is greater then this value (but not greater then the next row) then it's in this state"
            elif col == self.nameColumn():
                return "This is the string used to refer to this in the manual page"
   
        if role == QtCore.Qt.TextAlignmentRole:
            if col == 0:
                return QtCore.Qt.AlignCenter
            else:
                return QtCore.Qt.AlignRight
   


    def setData(self, index, value, role = QtCore.Qt.EditRole):

        if role == QtCore.Qt.EditRole:
            row = index.row()
            col = index.column()
            num_rows = len(self._data)
           
            if col == self.greaterThanColumn():
                if row == 0:
                    MessageBox("Row 0 greater_than must be 'None'", 'Attempting to set to: ', value)
                    return False
         
                if row < num_rows-1 and row > 0:
                    if value >= self._data[row+1][col]:
                        MessageBox('Greater than value must be less than next index','Next index: ', self._data[row+1][col])
                        return False

                if row > 1:
                    if value <= self._data[row-1][col]:
                        MessageBox('Greater than value must be more than previous index','Previous index: ', self._data[row-1][col])
                        return False


                self._data[row][col] = float(value)
                self.dataChanged.emit(index, index)
                return True



            if col == self.nameColumn():
                self._data[row][col] = str(value)
                self.dataChanged.emit(index, index)
                return True

        MessageBox("Failed editing analog state table data.", 'Attempted to set index: ', index, '\nto: ', value)
            
        return False


    def flags(self, index):
        #First row must always be enabled since it boots off
        if   index.column() == self.nameColumn():
            return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable 

        elif index.row() > 0 and index.column() == self.greaterThanColumn():
            return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable 

        else:
            return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable

        
       
    def numberOfStates(self):
        return self._number_of_states

    def setNumberOfStates(self, num_states):

        if not num_states in [1,2,3,4]:
            MessageBox('Invalid number of states, must be 1,2,3 or 4', num_states)
            return False

        if num_states == self.numberOfStates():
            return True

    
        current_greater_than_col = [inner[self.greaterThanColumn()] for inner in self._data] 
        current_name_col         = [inner[self.nameColumn()]        for inner in self._data] 
        
        current_max = 0.0
       

        self.beginResetModel()

        if   num_states == 1: new_tbl = [[0]]
        elif num_states == 2: new_tbl = [[0],[1]]
        elif num_states == 3: new_tbl = [[0],[1],[2]]
        elif num_states == 4: new_tbl = [[0],[1],[2],[3]]
      
            

        #Add the name and is used column from the old data if it exits
        for i, row in enumerate(new_tbl):
            if i == 0:
                row.append(None)
                row.append(current_name_col[i])

            elif i < len(current_name_col):
                current_max = current_greater_than_col[i]
                row.append(current_greater_than_col[i])
                row.append(current_name_col[i])
                
            else:
                current_max += 1.0
                row.append(current_max)
                row.append('GUI Name')


        self._data = new_tbl
        self._number_of_states = num_states
        self.endResetModel()
        return True



    #TODO change the name of this method?
    def states(self):
        name_col = self.nameColumn()
        return [row[name_col] for row in self._data]




