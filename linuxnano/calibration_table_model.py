#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtGui, QtWidgets
from linuxnano.message_box import MessageBox
import linuxnano.strings

import copy
import numpy as np
import itertools
from scipy.interpolate import interp1d



class CalibrationTableModel(QtCore.QAbstractTableModel):
    '''Stores analog value calibration, i.e. HAL units to software units
        - HAL: An analog value from HAL
        - GUI: A scaled value from the gui

        HAL Value  GUI Value
           0.0         0
           1.0        50
           2.0        250
           3.0        350
           4.0        450
           5.0        750
    '''

    def __init__(self, parent = None):
        super().__init__(parent)
        self._headers = ['HAL Value', 'GUI Value']
        self._data  = [[0.0, 0.0],
                       [10.0, 1000]]



    def halValueColumn(self):
        return 0

    def guiValueColumn (self):
        return 1

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
        data.append(['hal_value', 'gui_value'])
     
        data_main = copy.deepcopy(self._data)
        data += data_main

        return data


    def setDataArray(self, data):
        '''
            in format [ ['hal_value', 'gui_value' ],
                        [        0.0,        0.01 ],
                        [        2.0,       11.57 ],
                        [        5.0,       46.00 ],
                        [        9.0,        9183 ] ]
        '''
        data_main = []

        #Data validation first
        try:
            if data[0] == ['hal_value', 'gui_value']:
                data_main = data[1:]
            else:
                MessageBox("Invalid calibration table data, first row must be ['hal_value', 'gui_value'].", "Row 0:", data[0])
                return False


            num_rows = len(data_main)
          
            #Need minimum 2 points to draw a line
            if num_rows < 2:
                MessageBox('Invalid number of rows, must have 2 or more for calibration table', 'Calibration Table:', data)
                return False 


            #Check that these are all floats
            for i, row in enumerate(data_main):
               if not isinstance(row[0], (int, float)):
                    MessageBox('Calibration table must be of type int or float', row[0], 'is of type:', type(row[0]))
                    return False 
               
               if not isinstance(row[1], (int, float)):
                    MessageBox('Calibration table must be of type int or float', row[1], 'is of type:', type(row[1]))
                    return False 


            #Check that these are all increasing values
            hal_values = [row[0] for row in data_main]  
            gui_values = [row[1] for row in data_main] 


            hal_is_increasing = all(i < j for i, j in zip(hal_values, hal_values[1:])) 
            
            gui_is_increasing = all(i < j for i, j in zip(gui_values, gui_values[1:])) 
            gui_is_decreasing = all(i > j for i, j in zip(gui_values, gui_values[1:])) 

            
            if not (hal_is_increasing):
                MessageBox('Calibration table hal values must increasing in order', 'Calibration Table:', data)
                return False 

            if not (gui_is_increasing ^ gui_is_decreasing):
                MessageBox('Calibration table gui values must ordered either increasing or decreasing', 'Calibration Table:', data)
                return False 


        except Exception as e:
            MessageBox('Failed setting calibration table data array', 'Calibration Table: ', data, '\n', e)
            return False

       
        #Set the data now
        self.beginResetModel()
        for i, row in enumerate(data_main):
            data_main[i][0] = float(row[0])
            data_main[i][1] = float(row[1])
      
        self._data = copy.deepcopy(data_main)

        self.endResetModel()
        return True


            
        
    def data(self, index, role):
        row = index.row()
        col = index.column()

        if role == QtCore.Qt.EditRole or role == QtCore.Qt.DisplayRole:
            return self._data[row][col]
        
        if role == QtCore.Qt.ToolTipRole:
            return "These values are used to scale the numbers in HAL to the units in LinuxNano"
   
        if role == QtCore.Qt.TextAlignmentRole:
            if col == 0:
                return QtCore.Qt.AlignCenter
            else:
                return QtCore.Qt.AlignRight
   

    def setData(self, index, value, role = QtCore.Qt.EditRole):
        if role == QtCore.Qt.EditRole:
            if not isinstance(value, (int, float)):
                MessageBox("Must be integer or float type", 'Value: ', value)
                return False
            
            row = index.row()
            col = index.column()
            num_rows = len(self._data)




            if col == self.halValueColumn():
                if row < num_rows-1:
                    if value >= self._data[row+1][col]:
                        MessageBox('Hal value must be less than next index','Next index: ', self._data[row+1][col])
                        return False
                if row > 0:
                    if value <= self._data[row-1][col]:
                        MessageBox('Hal value must be more than previous index','Previous index: ', self._data[row-1][col])
                        return False

            elif col == self.guiValueColumn():


                #Check if the gui values are increasing or decreasing if we have more then 2
                if self.rowCount() > 2:
                    gui_values = [row[self.guiValueColumn()] for row in self._data] 
                    gui_is_increasing = all(i < j for i, j in zip(gui_values, gui_values[1:])) 

                    if gui_is_increasing:
                        if row < num_rows-1:
                            if value >= self._data[row+1][col]:
                                MessageBox('GUI value must be less than next index','Next index: ', self._data[row+1][col])
                                return False
                        if row > 0:
                            if value <= self._data[row-1][col]:
                                MessageBox('GUI value must be more than previous index','Previous index: ', self._data[row-1][col])
                                return False
                    else:
                        if row < num_rows-1:
                            if value <= self._data[row+1][col]:
                                MessageBox('GUI value must be more than next index','Next index: ', self._data[row+1][col])
                                return False
                        if row > 0:
                            if value >= self._data[row-1][col]:
                                MessageBox('GUI value must be less than previous index','Previous index: ', self._data[row-1][col])
                                return False



            self._data[row][col] = float(value)
            self.dataChanged.emit(index, index)
        
            return True
        return False




    def flags(self, index):
        if index.row() >= 0 and index.row() < len(self._data):
            return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable 

        else:
            return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable


    def removeRows(self, position, rows=1, index=QtCore.QModelIndex()):
        if self.rowCount() > 2:
            self.beginRemoveRows(QtCore.QModelIndex(), position, position + rows - 1)       
            self._data = self._data[:position] + self._data[position + rows:]
            self.endRemoveRows()
            return True
        
    def insertRows(self, position, rows=1, index=QtCore.QModelIndex()):
        #min two rows in this dataset
        #numpy.linspace(start, stop, num=50, endpoint=True, retstep=False, dtype=None, axis=0)
        if position == 0:
           
            hal_inc      = self._data[position][0] - self._data[position+1][0]
            new_hal_vals = [self._data[position][0] + hal_inc*i for i in range(1,rows+1)] 
            new_hal_vals.reverse() 
            
            gui_inc      = self._data[position][1] - self._data[position+1][1]
            new_gui_vals = [self._data[position][1] + gui_inc*i for i in range(1,rows+1)] 
            new_gui_vals.reverse() 
           
        
        elif position == len(self._data):
           
            hal_inc      = self._data[position-1][0] - self._data[position-2][0]
            new_hal_vals = [self._data[position-1][0] + hal_inc*i for i in range(1,rows+1)] 
            
            gui_inc      = self._data[position-1][1] - self._data[position-2][1]
            new_gui_vals = [self._data[position-1][1] + gui_inc*i for i in range(1,rows+1)] 
           

        else:
            new_hal_vals = np.linspace(self._data[position-1][0], self._data[position][0], rows+1, endpoint=False)
            new_hal_vals = new_hal_vals.tolist()
            new_hal_vals.pop(0)
            
            new_gui_vals = np.linspace(self._data[position-1][1], self._data[position][1], rows+1, endpoint=False)
            new_gui_vals = new_gui_vals.tolist()
            new_gui_vals.pop(0)

        
        self.beginInsertRows(QtCore.QModelIndex(), position, position + rows - 1)
        
        for row in range(rows):
            self._data.insert(position + row,  [new_hal_vals[row], new_gui_vals[row]])#"%s_%s"% (itemSelected, self.added))
        
        self.endInsertRows()
        
        return True

        
        


       


    #def setNumberOfStates(self, num_states):

    #    if not num_states in [1,2,3,4]:
    #        MessageBox('Invalid number of states, must be 1,2,3 or 4', num_states)
    #        return False

    #    if num_states == self.numberOfStates():
    #        return True

    #
    #    current_greater_than_col = [inner[self.greaterThanColumn()] for inner in self._data] 
    #    current_name_col         = [inner[self.nameColumn()]        for inner in self._data] 
    #    
    #    current_max = 0.0
    #   

    #    self.beginResetModel()

    #    if   num_states == 1: new_tbl = [[0]]
    #    elif num_states == 2: new_tbl = [[0],[1]]
    #    elif num_states == 3: new_tbl = [[0],[1],[2]]
    #    elif num_states == 4: new_tbl = [[0],[1],[2],[3]]
    #  
    #        

    #    #Add the name and is used column from the old data if it exits
    #    for i, row in enumerate(new_tbl):
    #        if i == 0:
    #            row.append(None)
    #            row.append(current_name_col[i])

    #        elif i < len(current_name_col):
    #            current_max = current_greater_than_col[i]
    #            row.append(current_greater_than_col[i])
    #            row.append(current_name_col[i])
    #            
    #        else:
    #            current_max += 1.0
    #            row.append(current_max)
    #            row.append('GUI Name')


    #    self._data = new_tbl
    #    self._number_of_states = num_states
    #    self.endResetModel()
    #    return True



    #TODO change the name of this method?
    def states(self):
        name_col = self.nameColumn()
        return [row[name_col] for row in self._data]





##==============================##






    #def possibleRanges(self):
    #    firstColumn =  [item[0] for item in self.__states]
    #    return firstColumn


    #def stateFromPins(self,pins):
    #    '''This is used to look up what state corresponds to a list of pins being True/False'''
    #    
    #    
    #    for i, tblState in enumerate(self.__states):
    #        tblStatePins = tblState[1:]
    #       
    #        flag = True
    #        for j, tblValue in enumerate(tblStatePins):
    #            if tblValue != pins[j]:
    #                flag = False

    #        if flag == True:
    #            return tblState[0]

   # def indexFromValue(self,value):
   #     i = 0

   #     while i < self.rowCount():

   #         low  = self.__ranges[i][1]
   #         high = self.__ranges[i][2]

   #       
   #         if (value >= low ) and (value <= high) :
   #             return i
   #         else:
   #             i += 1

   #     return None



   # def scaledNumber(self, value):
   #     i = 0

   #     while i < self.rowCount():

   #         low  = self.__ranges[i][1]
   #         high = self.__ranges[i][2]

   #         if (value >= low ) and (value <= high) :
   #        
   #             x_min = self.__ranges[i][1]
   #             x_max = self.__ranges[i][2]
   #             y_min = self.__ranges[i][3]
   #             y_max = self.__ranges[i][4]
   #          
   #             number = y_min
   #             number += ( (value-x_min)/(x_max-x_min) ) * (y_max-y_min)
   #             return number 
   #             
   #         else:
   #             i += 1

   #     # XXX should be an error
   #     return 0


