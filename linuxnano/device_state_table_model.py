#!/usr/bin/python3
# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtGui, QtWidgets
import itertools

import linuxnano.strings
from linuxnano.message_box import MessageBox





class DeviceStateTableModel(QtCore.QAbstractTableModel):
    '''This is owned by the device node.  When setup first calls setNodeStates, passing a 2d array where each row
       has the name of the HalNode followed by it's possible states.  This is used to form a truth table of all 
       possible states.

       setNodeStates is called anytime one of the devices HalNode is added/removed/changed
       dataArray is used to load/save the information in the table
    '''
    def __init__(self, parent = None):
        super().__init__(parent)
        
        self._default_headers = ['Status', 
                                 'Icon Layer\nName', 
                                 'Is Warning',   #True / False
                                 'Warning\nTimeout (sec)',   # 5sec, use 0 for no warning
                                 'Warning Message',   # "Warning: Foreline valve taking longer then 5 seconds to open"
                                 'Is Alarm',   #True / False
                                 'Alarm\nTimeout (sec)',   # 5sec, use 0 for no warning
                                 'Alarm Message',   # "Alarm: Foreline failed to open withing 5 sec time out"
                                 'Triggers\nAction',   #True / False
                                 'Action\nTimeout (sec)',   # 5sec, use 0 for no warning
                                 'Action',   # "set valve_output to True" - TODO need to make interface for setting a devices outputs in a recipe
                                 'Log Entrance'] # True / False

        self._default_data_row = ['unknown status', 'layer_n', False, 0, '', False, 0, '', False, 0, None, True]

        self._headers = self._default_headers
        self._data = [self._default_data_row]

        self._data_array_headers = ['state', 'status', 'icon_layer', 'is_warning', 'warning_timeout', 'warning_message', 'is_alarm', 'alarm_timeout', 'alarm_message', 'triggers_action', 'action_timeout', 'action', 'log_entrance']
        self._truth_table = [['off'],
                             ['on']]


    def statusColumn(self):         return len(self._truth_table[0])
    def iconLayerColumn(self):      return len(self._truth_table[0]) + 1
    def isWarningColumn(self):      return len(self._truth_table[0]) + 2
    def warningTimeoutColumn(self): return len(self._truth_table[0]) + 3
    def warningMessageColumn(self): return len(self._truth_table[0]) + 4
    def isAlarmColumn(self):        return len(self._truth_table[0]) + 5
    def alarmTimeoutColumn(self):   return len(self._truth_table[0]) + 6
    def alarmMessageColumn(self):   return len(self._truth_table[0]) + 7
    def triggersActionColumn(self): return len(self._truth_table[0]) + 8
    def actionTimeoutColumn(self):  return len(self._truth_table[0]) + 9
    def actionColumn(self):         return len(self._truth_table[0]) + 10
    def logEntranceColumn(self):    return len(self._truth_table[0]) + 11
        

    def rowCount(self, parent=None):
        return len(self._data)

    def columnCount(self, parent=None):
        return len(self._data[0])


    #TODO I think this being called too often during load
    def setNodeStates(self, list_of_states):
        states = list_of_states[::-1] #reverses the order
      
        headers = [row[0] for row in states]
        states  = [row[1:] for row in states]

        #First string in each node is the name of the HalNode, rest are the state names
        for row in states:
               
            if len(row) <= 1:
                return False

            for val in row:
                if not (isinstance(val, str) or val == None):
                    MessageBox('Bad states info sent to DeviceStateTableModel', val)
                    return False

        tbl = []
        for element in itertools.product(*states):
            tbl.append(list(element))
        

        self._truth_table = tbl

        #Anytime the truth table is changed we need to update the data layout and the headers
        self.beginResetModel()
        
        new_data = self._truth_table[:]
        for i, row in enumerate(new_data):
            new_data[i] = new_data[i] + self._default_data_row[:]
        self._data = new_data
        
        self._headers = headers + self._default_headers

        self.endResetModel()
        
        return True


    def truthTable(self):
        return self._truth_table


    def setDataArray(self, data):
        '''
            in format [ ['state', 'status'      , 'icon_layer', 'is_warning', 'warning_timeout', 'warning_message', 'is_alarm', 'alarm_timeout', 'alarm_message', 
                        [   0   , 'my status 1' , 'layer_0'   ,        False,               0.0,                '',      False,             0.0,              '',
                        [   1   , 'my status 2' , 'layer_1'   ,         True,               5.0,      'my warning',       True,            10.0,    'some alarm',
                        [   2   , 'my status 3' , 'layer_2'   ,        False,               0.0,                '',      False,             0.0,              '',
                        [   3   , 'my status 4' , 'layer_3'   ,        False,               0.0,                '',      False,             0.0,              '',
                       


                                    'triggers_action', 'action_timeout', 'action', 'log_entrance'],
                                                False,              0.0,     None,           True],
                                                 True,             10.0,     None,           True],
                                                False,              0.0,     None,           True],
                                                False,              0.0,     None,           True],



        '''
            
        #Data validation first
        try:
            if data[0] == self._data_array_headers: 
                data_main = data[1:]
            else:
                MessageBox('Invalid headers for set Data', data[0])
                return False

            num_rows = len(data_main)

            if num_rows != len(self._truth_table):
                MessageBox('Invalid number of states for device', 'sent: ', num_rows, 'need: ', len(self._truth_table) )
                return False
        
            #Check state column is in order, 0,1,2,.. n
            first_col = [row[0] for row in data_main]
            if first_col != list(range(0, len(self._truth_table))):
                MessageBox('State column must be in format 0, 1 ,2 ....n', first_col )
                return False
            
            #Check status column is text
            for item in [row[1] for row in data_main]:
                if not isinstance(item, str):
                    MessageBox('status must be of type str', item, 'is of type: ', type(item))
                    return False
            
            #Check icon_layer column is text
            for item in [row[2] for row in data_main]:
                if not isinstance(item, str):
                    MessageBox('icon_layer must be of type str', item, 'is of type: ', type(item))
                    return False

            #Check is_warning column is True/False
            for item in [row[3] for row in data_main]:
                if not isinstance(item, bool):
                    MessageBox('is_warning must be True or False', item, 'is of type: ', type(item))
                    return False

            #Check warning_timeout column is a number or none
            for item in [row[4] for row in data_main]:
                if not isinstance(item, (float, int,)):
                    MessageBox('warning_timeout must be of type float or int', item, 'is of type: ', type(item))
                    return False

            #Check warning_message column is a string or none
            for item in [row[5] for row in data_main]:
                if not isinstance(item, str):
                    MessageBox('warning_message must be of type str', item, 'is of type: ', type(item))
                    return False
            
            #Check is_alarm column is True/False
            for item in [row[6] for row in data_main]:
                if not isinstance(item, bool):
                    MessageBox('is_alarm must be True or False', item, 'is of type: ', type(item))
                    return False

            #Check alarm_timeout column is a number or none
            for item in [row[7] for row in data_main]:
                if not isinstance(item, (float, int,)):
                    MessageBox('alarm_timeout must be of type float or int', item, 'is of type: ', type(item))
                    return False

            #Check alarm_message column is a string or none
            for item in [row[8] for row in data_main]:
                if not isinstance(item, str):
                    MessageBox('alarm_message must be of type str', item, 'is of type: ', type(item))
                    return False
            
            #Check triggers_action column is True/False
            for item in [row[9] for row in data_main]:
                if not isinstance(item, bool):
                    MessageBox('triggers_action must be True or False', item, 'is of type: ', type(item))
                    return False

            #Check action_timeout column is a number or none
            for item in [row[10] for row in data_main]:
                if not isinstance(item, (int, float)):
                    MessageBox('action_timeout must be of type float or int', item, 'is of type: ', type(item))
                    return False


            ##TODO action column checks
            #
            #Check log_entrance is True or False
            for item in [row[12] for row in data_main]:
                if not isinstance(item, bool):
                    MessageBox('log_entrance must be True or False', item, 'is of type: ', type(item))
                    return False






        except Exception as e:
            MessageBox('Device state table data array testing failed', '\n', data, '\n', e)
            return False


        self.beginResetModel()

        new_data = self._truth_table[:]
        for i, row in enumerate(data_main):
            new_data[i] = new_data[i] + row[1:]
        self._data = new_data

        self.endResetModel()
        return True


    def dataArray(self):
        data = []
        data.append(self._data_array_headers[:])

        for i, row in enumerate(self._data):
            status          = self._data[i][self.statusColumn()]
            icon_layer      = self._data[i][self.iconLayerColumn()]
            is_warning      = self._data[i][self.isWarningColumn()]
            warning_timeout = self._data[i][self.warningTimeoutColumn()]
            warning_message = self._data[i][self.warningMessageColumn()]
            is_alarm        = self._data[i][self.isAlarmColumn()]
            alarm_timeout   = self._data[i][self.alarmTimeoutColumn()]
            alarm_message   = self._data[i][self.alarmMessageColumn()]
            triggers_action = self._data[i][self.triggersActionColumn()]
            action_timeout  = self._data[i][self.actionTimeoutColumn()]
            action          = self._data[i][self.actionColumn()]
            log_entrance    = self._data[i][self.logEntranceColumn()]

            data.append([i, status, icon_layer, is_warning, warning_timeout, warning_message, is_alarm, alarm_timeout, alarm_message, triggers_action, action_timeout, action, log_entrance])
        
        return data



    def headerData(self, section, orientation, role):
        if role == QtCore.Qt.DisplayRole:
            if orientation == QtCore.Qt.Horizontal:
                return self._headers[section]
            else:
                return str(section).format("%1")

    def flags(self, index):
        if index.column() < len(self._truth_table[0]):
            return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable
        
       
        elif index.column() in [self.warningTimeoutColumn(), self.warningMessageColumn()] and self._data[index.row()][self.isWarningColumn()] == False:
            return QtCore.Qt.ItemIsSelectable
        
        elif index.column() in [self.alarmTimeoutColumn(), self.alarmMessageColumn()] and self._data[index.row()][self.isAlarmColumn()] == False:
            return QtCore.Qt.ItemIsSelectable
        
        elif index.column() in [self.actionTimeoutColumn()] and self._data[index.row()][self.triggersActionColumn()] == False:
            return QtCore.Qt.ItemIsSelectable
        
        else:
            return QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable


    #FIXME the layer things need to really be a dropdown based on the layers availabe in the manual icon node
    def data(self, index, role):
        if role == QtCore.Qt.EditRole or role == QtCore.Qt.DisplayRole:
            row = index.row()
            col = index.column()
            return self._data[row][col]
        
        elif role == QtCore.Qt.ToolTipRole:
            return 'Need to add a tooltip'
        
        elif role == QtCore.Qt.TextAlignmentRole:
            return QtCore.Qt.AlignCenter   


    def setData(self, index, value, role = QtCore.Qt.EditRole):
        if role == QtCore.Qt.EditRole:
            if type(value) == type(QtCore.QVariant()): 
                value = value.toPyObject()

            row = index.row()
            col = index.column()


            if col == self.statusColumn():
                value = str(value)
                self._data[row][col] = value
                self.dataChanged.emit(index, index)
                return True

            elif col in [self.iconLayerColumn(), self.warningMessageColumn(), self.alarmMessageColumn()]:
                value = str(value)
                self._data[row][col] = value
                self.dataChanged.emit(index, index)
                return True
            
            elif col in [self.warningTimeoutColumn(), self.alarmTimeoutColumn(), self.actionTimeoutColumn()]:
                if value == None:
                    self._data[row][col] = None
                else:
                    self._data[row][col] = float(value)

                self.dataChanged.emit(index, index)
                return True
           
            #FIXME
            elif col == self.actionColumn():
                value = str(value)
                self._data[row][col] = value
                self.dataChanged.emit(index, index)
                return True
            
            elif col in [self.isWarningColumn(), self.isAlarmColumn(), self.triggersActionColumn(), self.logEntranceColumn()]:
                if value == True:
                    self._data[row][col] = True
                else:
                    self._data[row][col] = False
                self.dataChanged.emit(index, index)
                return True
       
        return False

